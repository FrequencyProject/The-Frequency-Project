#include <Arduino.h>
#include <SPI.h>
#include <string.h> // Enforces explicit declaration profile for strlen()

// --- PIN DEFINITIONS (Synchronized to Hardware Blueprint) ---
const int ADC_CS_PIN = 5;
const int ADC_DRDY_PIN = 4;
const int32_t FAULT_SENTINEL = -2147483648; // INT32_MIN
const uint32_t TIMEOUT_LIMIT = 5000;

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

int32_t read_adc_channel_raw(uint8_t channel_cmd) {
    uint32_t timeout_counter = 0;
    while (digitalRead(ADC_DRDY_PIN) == HIGH && timeout_counter < TIMEOUT_LIMIT) {
        timeout_counter++;
    }
    if (timeout_counter >= TIMEOUT_LIMIT) {
        digitalWrite(ADC_CS_PIN, HIGH);
        return FAULT_SENTINEL;
    }
    SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE1));
    digitalWrite(ADC_CS_PIN, LOW);
    SPI.transfer(channel_cmd);
    uint8_t b1 = SPI.transfer(0x00);
    uint8_t b2 = SPI.transfer(0x00);
    uint8_t b3 = SPI.transfer(0x00);
    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
    
    int32_t raw_value = ((int32_t)b1 << 16) | ((int32_t)b2 << 8) | b3;
    if (raw_value & 0x800000) {
        raw_value |= 0xFF000000;
    }
    return raw_value;
}

float convert_to_voltage(int32_t raw_counts) {
    // Standard signed 24-bit conversion divisor
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
    int32_t raw_ch1 = read_adc_channel_raw(0x01);
    int32_t raw_ch2 = read_adc_channel_raw(0x02);
    int32_t raw_ch3 = read_adc_channel_raw(0x03);
    int32_t raw_ch4 = read_adc_channel_raw(0x04);
    
    if (raw_ch1 == FAULT_SENTINEL || raw_ch2 == FAULT_SENTINEL || 
        raw_ch3 == FAULT_SENTINEL || raw_ch4 == FAULT_SENTINEL) {
        Serial.println("V1:FAULT,V2:FAULT,V3:FAULT,V4:FAULT");
        delay(10);
        return;
    }
    
    float v1 = convert_to_voltage(raw_ch1);
    float v2 = convert_to_voltage(raw_ch2);
    float v3 = convert_to_voltage(raw_ch3);
    float v4 = convert_to_voltage(raw_ch4);
    
    char payload[128];
    // 1. Build string format with explicit 4-decimal precision
    snprintf(payload, sizeof(payload), "V1:%.4f,V2:%.4f,V3:%.4f,V4:%.4f", v1, v2, v3, v4);
    
    // 2. Compute CRC directly over the raw transmitted ASCII payload characters
    uint8_t final_crc = compute_binary_crc8((uint8_t*)payload, strlen(payload));
    
    // 3. Broadcast the payload matched with the string-level checksum
    Serial.print(payload);
    Serial.print(",CRC:0x");
    if (final_crc < 0x10) Serial.print("0");
    Serial.println(final_crc, HEX);
    
    delay(16);
}
