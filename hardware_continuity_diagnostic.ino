#include <Arduino.h>
#include <SPI.h>

// ==============================================================================
// 🔌 PERIPHERAL 1: ADS1256 FRONTEND ON NATIVE FSPI (SPI2)
// ==============================================================================
const int ADS_CS_PIN   = 10; // FSPICS0
const int ADS_DRDY_PIN = 4;  // Hardware Interrupt Input
SPIClass fspi_bus(FSPI);     // Explicitly bind to the FSPI hardware block

// ==============================================================================
// 🔌 PERIPHERAL 2: DISCRETE TPM 2.0 ON NATIVE HSPI (SPI3)
// ==============================================================================
const int TPM_CS_PIN   = 38; // HSPICS0
const int TPM_SCLK_PIN = 36; // HSPICLK
const int TPM_MISO_PIN = 37; // HSPIQ
const int TPM_MOSI_PIN = 35; // HSPID
const int TPM_RST_PIN  = 39; // Dedicated Hardware Reset
SPIClass hspi_bus(HSPI);     // Explicitly bind to the HSPI hardware block

// ==============================================================================
// 📋 DIAGNOSTIC REGISTER TARGETS
// ==============================================================================
const uint8_t ADS_CMD_RREG    = 0x10; // Read Register Command Base
const uint8_t ADS_REG_STATUS  = 0x00; // ID is stored in upper 4 bits of STATUS (0xx3 for ADS1256)
const uint32_t TPM_REG_DID_VID = 0x00000000; // TCG standard Vendor ID / Device ID register offset

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); } // Wait for USB-UART link to settle
    
    Serial.println("\n======================================================================");
    Serial.println("VIVIC AI: BARE-METAL HARDWARE CONTINUITY & BUS DIAGNOSTIC");
    Serial.println("======================================================================");

    // 1. Initialize GPIO Control Pins to Safe Defensively-High States
    pinMode(ADS_CS_PIN, OUTPUT);
    pinMode(TPM_CS_PIN, OUTPUT);
    pinMode(TPM_RST_PIN, OUTPUT);
    digitalWrite(ADS_CS_PIN, HIGH);
    digitalWrite(TPM_CS_PIN, HIGH);
    
    pinMode(ADS_DRDY_PIN, INPUT_PULLUP);

    // 2. Execute Hard Reset Sequence on TPM Module to stabilize internal state machine
    Serial.print("[INIT] Triggering hardware reset on TPM 2.0 line (GPIO 39)...");
    digitalWrite(TPM_RST_PIN, LOW);
    delay(50); // Hold line low to discharge capacitors
    digitalWrite(TPM_RST_PIN, HIGH);
    delay(100); // Wait for boot-up ROM execution window to clear
    Serial.println(" DONE.");

    // 3. Instantiate Native FSPI Block for the ADS1256 Frontend
    // Uses hardware default pins: SCLK=12, MISO=13, MOSI=11
    Serial.print("[BUS] Initializing FSPI Peripheral Engine (SPI2)...");
    fspi_bus.begin(12, 13, 11, ADS_CS_PIN);
    Serial.println(" ONLINE.");

    // 4. Instantiate Native HSPI Block for the Discrete TPM 2.0 Module
    // Maps your custom mapped high-speed IO tracks explicitly
    Serial.print("[BUS] Initializing HSPI Peripheral Engine (SPI3)...");
    hspi_bus.begin(TPM_SCLK_PIN, TPM_MISO_PIN, TPM_MOSI_PIN, TPM_CS_PIN);
    Serial.println(" ONLINE.");

    delay(200); // Allow electrical rails to reach complete steady-state equilibrium
}

void loop() {
    Serial.println("\n----------------------------------------------------------------------");
    Serial.println("[SCAN] Beginning physical bus continuity scan...");
    Serial.println("----------------------------------------------------------------------");

    // ==============================================================================
    // 🧪 SCAN PATH 1: TI ADS1256 FRONTEND VALIDATION
    // ==============================================================================
    Serial.print(" -> Probing ADS1256 Frontend Matrix... ");
    
    // Check if DRDY is alive (should toggle or stay at high-impedance default pull-up state)
    int drdy_status = digitalRead(ADS_DRDY_PIN);
    
    fspi_bus.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE1));
    digitalWrite(ADS_CS_PIN, LOW);
    
    fspi_bus.transfer(ADS_CMD_RREG | ADS_REG_STATUS); // Command: Read Status Register
    fspi_bus.transfer(0x00);                         // Command: Read 1 byte (0x00 = 1)
    delayMicroseconds(10);                           // t6 parameter delay window
    uint8_t status_byte = fspi_bus.transfer(0x00);   // Fetch data byte
    
    digitalWrite(ADS_CS_PIN, HIGH);
    fspi_bus.endTransaction();

    uint8_t chip_id = status_byte >> 4; // Extract identification bits
    
    // Verification check: Factory ADS1256 ID bits must match binary x011 (3)
    if (chip_id == 3 || chip_id == 7) {
        Serial.print("SUCCESS. Valid Chip ID captured: 0x");
        Serial.print(chip_id, HEX);
        Serial.print(" (DRDY Pin State: ");
        Serial.print(drdy_status == LOW ? "LOW/ACTIVE" : "HIGH/IDLE");
        Serial.println(")");
    } else {
        Serial.print("FAILURE! Read Status: 0x");
        Serial.print(status_byte, HEX);
        Serial.println(" -> Check SCLK(12), MISO(13), MOSI(11), and CS(10) lines.");
    }

    // ==============================================================================
    // 🧪 SCAN PATH 2: DISCRETE TPM 2.0 ACCESS MATRIX VALIDATION
    // ==============================================================================
    Serial.print(" -> Probing Discrete TPM 2.0 Module... ");
    
    hspi_bus.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0)); // Standard TCG mode 0 alignment
    digitalWrite(TPM_CS_PIN, LOW);
    
    // Request Vendor ID register (TCG address space mapping offset 0x00 via 3-byte command headers)
    hspi_bus.transfer(0x80); // Read operation flag
    hspi_bus.transfer(0x00); // Address byte high
    hspi_bus.transfer(0x00); // Address byte low
    
    // Read out the 4-byte unified DID/VID registry envelope sequence
    uint8_t v1 = hspi_bus.transfer(0x00);
    uint8_t v2 = hspi_bus.transfer(0x00);
    uint8_t v3 = hspi_bus.transfer(0x00);
    uint8_t v4 = hspi_bus.transfer(0x00);
    
    digitalWrite(TPM_CS_PIN, HIGH);
    hspi_bus.endTransaction();

    uint32_t did_vid = ((uint32_t)v1 << 24) | ((uint32_t)v2 << 16) | ((uint32_t)v3 << 8) | v4;

    // A completely dead or un-wired bus returns 0xFFFFFFFF or 0x00000000
    if (did_vid != 0xFFFFFFFF && did_vid != 0x00000000) {
        Serial.print("SUCCESS. Valid Device/Vendor ID captured: 0x");
        Serial.println(did_vid, HEX);
    } else {
        Serial.print("FAILURE! Communication Bus Blank: 0x");
        Serial.print(did_vid, HEX);
        Serial.println(" -> Check SCLK(36), MISO(37), MOSI(35), and CS(38) lines.");
    }

    Serial.println("----------------------------------------------------------------------");
    delay(5000); // Repeat diagnostic polling cycle every 5 seconds
}
