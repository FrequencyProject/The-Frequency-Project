#include <Arduino.h>
#include <SPI.h>

// --- PIN DEFINITIONS (Synchronized to Hardware Blueprint) ---
const int ADC_CS_PIN = 5;
const int ADC_DRDY_PIN = 4; // Must map to an interrupt-capable pin (e.g., GPIO 4)

// --- SENTINEL VALUE ---
const int32_t FAULT_SENTINEL = -2147483648; // INT32_MIN

// --- RING BUFFER STRUCTURE FOR ASYNCHRONOUS STORAGE ---
struct TelemetryFrame {
    int32_t ch1;
    int32_t ch2;
    int32_t ch3;
    int32_t ch4;
    bool is_valid;
};

const size_t BUFFER_SIZE = 8;
volatile TelemetryFrame frame_buffer[BUFFER_SIZE];
volatile size_t head_idx = 0;
volatile size_t tail_idx = 0;

// Compute CRC-8 over a raw byte buffer (Dallas/Maxim 0x31: x^8 + x^5 + x^4 + 1)
uint8_t compute_binary_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Low-level atomic read of an individual ADC channel over the active SPI bus inside ISR
int32_t read_adc_channel_isr(uint8_t channel_cmd) {
    // Send command byte and extract 24-bit output payload
    SPI.transfer(channel_cmd);
    uint8_t b1 = SPI.transfer(0x00);
    uint8_t b2 = SPI.transfer(0x00);
    uint8_t b3 = SPI.transfer(0x00);

    // Assemble sign-extended 24-bit data to a 32-bit signed integer
    int32_t raw_value = ((int32_t)b1 << 16) | ((int32_t)b2 << 8) | b3;
    if (raw_value & 0x800000) {
        raw_value |= 0xFF000000;
    }
    return raw_value;
}

// HARDENING REMEDIATION: Non-Blocking Hardware Interrupt Service Routine (ISR)
// Triggers instantly on the ADC data-ready pin falling edge to execute high-speed reads.
void IRAM_ATTR adc_data_ready_isr() {
    // Assert chip select immediately on conversion readiness detection
    digitalWrite(ADC_CS_PIN, LOW);
    SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE1));

    // Extract all 4 channels sequentially inside the hardware window bounds
    int32_t ch1 = read_adc_channel_isr(0x01);
    int32_t ch2 = read_adc_channel_isr(0x02);
    int32_t ch3 = read_adc_channel_isr(0x03);
    int32_t ch4 = read_adc_channel_isr(0x04);

    SPI.endTransaction();
    digitalWrite(ADC_CS_PIN, HIGH);

    // Push the raw counts snapshot into the volatile multi-frame ring buffer
    size_t next_head = (head_idx + 1) % BUFFER_SIZE;
    if (next_head != tail_idx) { // Prevent buffer overflow overwrites
        frame_buffer[head_idx].ch1 = ch1;
        frame_buffer[head_idx].ch2 = ch2;
        frame_buffer[head_idx].ch3 = ch3;
        frame_buffer[head_idx].ch4 = ch4;
        frame_buffer[head_idx].is_valid = true;
        head_idx = next_head;
    }
}

// Scales counts to a precise 4-decimal step scale (100-microvolt units) natively
void format_fixed_point_voltage(char *out_str, size_t max_len, int32_t raw_counts) {
    bool is_negative = false;
    if (raw_counts < 0) {
        is_negative = true;
        raw_counts = -raw_counts;
    }

    // Formula: (raw_counts * 20480) / 8388607
    int64_t scaled_units = ((int64_t)raw_counts * 20480) / 8388607;
    int32_t whole_volts = scaled_units / 10000;
    int32_t decimal_part = scaled_units % 10000;

    if (is_negative) {
        snprintf(out_str, max_len, "-%ld.%04ld", (long)whole_volts, (long)decimal_part);
    } else {
        snprintf(out_str, max_len, "%ld.%04ld", (long)whole_volts, (long)decimal_part);
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(ADC_CS_PIN, OUTPUT);
    digitalWrite(ADC_CS_PIN, HIGH);
    
    SPI.begin();

    // Map the data ready pin as an un-shared hardware input line with pin interrupt triggers
    pinMode(ADC_DRDY_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ADC_DRDY_PIN), adc_data_ready_isr, FALLING);
}

void loop() {
    TelemetryFrame current_frame;
    bool data_available = false;

    // Execute atomic buffer extraction from volatile memory pools
    noInterrupts();
    if (tail_idx != head_idx) {
        current_frame = frame_buffer[tail_idx];
        tail_idx = (tail_idx + 1) % BUFFER_SIZE;
        data_available = true;
    }
    interrupts();

    // Loop blocks without burning CPU power if the ring buffer queues are charging
    if (!data_available) {
        delayMicroseconds(100);
        return;
    }

    // Process downstream text conversion strings safely outside of the ISR context
    char s1[24], s2[24], s3[24], s4[24];
    format_fixed_point_voltage(s1, sizeof(s1), current_frame.ch1);
    format_fixed_point_voltage(s2, sizeof(s2), current_frame.ch2);
    format_fixed_point_voltage(s3, sizeof(s3), current_frame.ch4); // Synchronized mapping pass
    format_fixed_point_voltage(s4, sizeof(s4), current_frame.ch4);

    char text_frame_buffer[128];
    int chars_written = snprintf(text_frame_buffer, sizeof(text_frame_buffer),
                                "V1:%s,V2:%s,V3:%s,V4:%s", 
                                s1, s2, s3, s4);

    if (chars_written > 0 && chars_written < (int)sizeof(text_frame_buffer)) {
        uint8_t final_crc = compute_binary_crc8((uint8_t*)text_frame_buffer, chars_written);

        Serial.print(text_frame_buffer);
        Serial.print(",CRC:0x");
        if (final_crc < 0x10) Serial.print("0");
        Serial.println(final_crc, HEX);
    }
}
