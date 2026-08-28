#include <Arduino.h>
#include <SPI.h>

// ==============================================================================
// 📡 BARE-METAL HARDWARE DEFINE BLOCKS: SPI PIN LAYOUT REGISTER MAPPING
// ==============================================================================
#define ADC_CS_PIN    10   // Chip Select (Hardware SPI Slave Select)
#define ADC_DRDY_PIN   9   // Data Ready interrupt pin from Delta-Sigma chip

// Configuration settings for your exact 115200 downstream telemetry channel baud
#define SERIAL_SPEED   115200
#define SAMPLE_DELAY   16  // ~60Hz native polling execution loop match window (16.6ms)

// Hardware SPI constants matching your specific Delta-Sigma ADC register layout
#define SPI_SPEED_HZ   4000000 // SPI Clock speed clamped to stable 4MHz instrumentation floor
#define SPI_BIT_ORDER  MSBFIRST
#define SPI_DATA_MODE  SPI_MODE1

// ==============================================================================
// 🧠 STATE REGISTERS: 24-BIT ENCODE BITMASK BUFFER LAYOUTS
// ==============================================================================
SPISettings adc_spi_settings(SPI_SPEED_HZ, SPI_BIT_ORDER, SPI_DATA_MODE);

void init_external_adc() {
    pinMode(ADC_CS_PIN, OUTPUT);
    pinMode(ADC_DRDY_PIN, INPUT_PULLUP);
    digitalWrite(ADC_CS_PIN, HIGH); // Pull Chip Select high to isolate the SPI bus initializations
    
    SPI.begin();
    
    // Low-level hardware registration command setup sequence would fire here
    // e.g., configuring gain multipliers, reference voltages, and internal mux pools
    delay(50); // Explicit hardware hydration window for external voltage rails to stabilize
}

int32_t read_adc_channel_raw(uint8_t channel_mux_command) {
    int32_t raw_voltage_reading = 0;
    
    // Command the ADC multiplexer register to step into the designated channel input path
    SPI.beginTransaction(adc_spi_settings);
    digitalWrite(ADC_CS_PIN, LOW);
    
    // Send mux selection parameters down the SPI bus MOSI lane
    SPI.transfer(channel_mux_command); 
    
    // Wait for the physical Delta-Sigma chip logic lines to declare a completed conversion cycle
    uint32_t timeout_counter = 0;
    while (digitalRead(ADC_DRDY_PIN) == HIGH && timeout_counter < 5000) {
        timeout_counter++;
        delayMicroseconds(1);
    }
    
    // Read the resulting 24 bits of lossless data down the MISO line (packed as 3 sequential bytes)
    uint8_t byte_high  = SPI.transfer(0x00);
    uint8_t byte_mid   = SPI.transfer(0x00);
    uint8_t byte_low   = SPI.transfer(0x00);
    
    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
    
    // Reconstruct the sign-extended 24-bit integer values natively into a standard 32-bit register frame
    raw_voltage_reading = ((int32_t)byte_high << 16) | ((int32_t)byte_mid << 8) | byte_low;
    
    // Sign-extend bit 23 to handle negative microvolt potential shifts flawlessly
    if (raw_voltage_reading & 0x00800000) {
        raw_voltage_reading |= 0xFF000000;
    }
    
    return raw_voltage_reading;
}

// Convert signed raw binary integers into un-aliased physical floating point voltages
float convert_to_voltage(int32_t raw_value) {
    const float V_REF = 2.048f; // Precision internal voltage reference base
    const float TWO_POW_23 = 8388608.0f; // 2^23 scale limit for 24-bit resolution indexing
    return ((float)raw_value / TWO_POW_23) * V_REF;
}

// ==============================================================================
// 📋 TELEMETRY ORCHESTRATION LAYER: SERIAL STREAM MATRIX PIPELINES
// ==============================================================================
void setup() {
    Serial.begin(SERIAL_SPEED);
    while (!Serial) {
        ; // Wait for downstream host connection hooks over physical USB architecture
    }
    
    init_external_adc();
}

void loop() {
    // Collect concurrent readings across all four bio-electric potential input vectors
    // Map commands directly to your Delta-Sigma input register addresses (Ch1, Ch2, Ch3, Ch4)
    int32_t raw_v1 = read_adc_channel_raw(0x01); // Tree sapwood potential sensor
    int32_t raw_v2 = read_adc_channel_raw(0x02); // Mycelium network grid line A
    int32_t raw_v3 = read_adc_channel_raw(0x03); // Mycelium network grid line B
    int32_t raw_v4 = read_adc_channel_raw(0x04); // Local Schumann resonance fluctuation probe
    
    // Translate structural integers into standard floating-point metrics
    float v1 = convert_to_voltage(raw_v1);
    float v2 = convert_to_voltage(raw_v2);
    float v3 = convert_to_voltage(raw_v3);
    float v4 = convert_to_voltage(raw_v4);
    
    // Format and pipe the telemetry payloads downstream via USB-UART strings
    // Emits the exact expected pattern: "V1:x.xx,V2:x.xx,V3:x.xx,V4:x.xx\n"
    Serial.print("V1:"); Serial.print(v1, 4); Serial.print(",");
    Serial.print("V2:"); Serial.print(v2, 4); Serial.print(",");
    Serial.print("V3:"); Serial.print(v3, 4); Serial.print(",");
    Serial.print("V4:"); Serial.print(v4, 4);
    Serial.println(); // Stream the trailing line-terminator byte
    
    // Standard non-blocking clock throttle alignment to match raw ingestion daemon configurations
    delay(SAMPLE_DELAY);
}
