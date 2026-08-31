#include <Arduino.h>
#include <SPI.h>

// --- PIN DEFINITIONS (Synchronized to Hardware Blueprint) ---
const int ADC_CS_PIN = 5;
const int ADC_DRDY_PIN = 4;

// --- SENTINEL VALUE ---
const int32_t FAULT_SENTINEL = -2147483648; // INT32_MIN

// --- CONFIGURATION ---
const uint32_t TIMEOUT_MICROS_LIMIT = 5000; // Hardened clock-bound limits (5ms)

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

// Low-level raw read of a specified ADC channel via SPI with clock-bound protection
int32_t read_adc_channel_raw(uint8_t channel_cmd) {
    uint32_t start_time = micros();

    // Wait for data ready signal with high-impedance pull-up monitoring using true microsecond clocks
    while (digitalRead(ADC_DRDY_PIN) == HIGH) {
        if ((micros() - start_time) >= TIMEOUT_MICROS_LIMIT) {
            digitalWrite(ADC_CS_PIN, HIGH);
            return FAULT_SENTINEL;
        }
    }

    SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE1));
    digitalWrite(ADC_CS_PIN, LOW);

    // Send command byte and read 24-bit output payload
    SPI.transfer(channel_cmd);
    uint8_t b1 = SPI.transfer(0x00);
    uint8_t b2 = SPI.transfer(0x00);
    uint8_t b3 = SPI.transfer(0x00);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();

    // Assemble sign-extended 24-bit data to 32-bit integer
    int32_t raw_value = ((int32_t)b1 << 16) | ((int32_t)b2 << 8) | b3;
    if (raw_value & 0x800000) {
        raw_value |= 0xFF000000;
    }

    return raw_value;
}

// Convert signed 24-bit raw counts to true analog voltage (-2.048V to +2.048V range)
float convert_to_voltage(int32_t raw_counts) {
    return (float)raw_counts * (2.048f / 8388607.0f);
}

void setup() {
    Serial.begin(115200);
    pinMode(ADC_CS_PIN, OUTPUT);
    pinMode(ADC_DRDY_PIN, INPUT_PULLUP);
    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.begin();
}

void loop() {
    // Read all 4 operational channels sequentially
    int32_t raw_ch1 = read_adc_channel_raw(0x01);
    int32_t raw_ch2 = read_adc_channel_raw(0x02);
    int32_t raw_ch3 = read_adc_channel_raw(0x03);
    int32_t raw_ch4 = read_adc_channel_raw(0x04);

    // Atomic fault interception before committing to downstream string translation
    if (raw_ch1 == FAULT_SENTINEL || raw_ch2 == FAULT_SENTINEL ||
        raw_ch3 == FAULT_SENTINEL || raw_ch4 == FAULT_SENTINEL) {
        Serial.println("V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT,CRC:0x00");
        delay(16);
        return;
    }

    // Safe conversion to floating-point metrics
    float v1 = convert_to_voltage(raw_ch1);
    float v2 = convert_to_voltage(raw_ch2);
    float v3 = convert_to_voltage(raw_ch3);
    float v4 = convert_to_voltage(raw_ch4);

    // HARDENING REMEDIATION: Assemble text data into an isolated string character frame buffer 
    // to match the exact string-level Dallas CRC-8 validation rules expected by your Python daemon.
    char text_frame_buffer[80];
    int chars_written = snprintf(text_frame_buffer, sizeof(text_frame_buffer),
                                "V1:%.4f,V2:%.4f,V3:%.4f,V4:%.4f", 
                                v1, v2, v3, v4);

    if (chars_written > 0 && chars_written < (int)sizeof(text_frame_buffer)) {
        // Calculate the CRC directly over the ASCII characters of the string
        uint8_t final_crc = compute_binary_crc8((uint8_t*)text_frame_buffer, chars_written);

        // Broadcast the completely verified data stream frame over the TX hardware serial bus
        Serial.print(text_frame_buffer);
        Serial.print(",CRC:0x");
        if (final_crc < 0x10) Serial.print("0");
        Serial.println(final_crc, HEX);
    }

    delay(16); // Match with ~60Hz ingestion cycle target
}
