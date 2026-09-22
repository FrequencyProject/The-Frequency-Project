
#include <stdio.h>
#include <stdint.h>
#include "esp_timer.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define GPIO_DEBUG_PIN       GPIO_NUM_4

// Select your target rate: 1000 Hz, 500 Hz, or 250 Hz
#define TARGET_SAMPLE_RATE_HZ 1000
#define SAMPLING_PERIOD_US    (1000000 / TARGET_SAMPLE_RATE_HZ)

// Telemetry packet layout
typedef struct __attribute__((packed)) {
    uint32_t seq;           
    int64_t  timestamp_us;  
    int16_t  sample_data;   
} SensorPacket_t;

static SensorPacket_t tx_packet;
static volatile uint32_t sample_counter = 0;

static void IRAM_ATTR sampling_timer_callback(void* arg) {
    // 1. Logic Analyzer verification pin
    gpio_set_level(GPIO_DEBUG_PIN, (sample_counter % 2));

    // 2. Populate packet headers
    tx_packet.seq = sample_counter++;
    tx_packet.timestamp_us = esp_timer_get_time();

    // 3. Acquire dummy/sensor sample 
    tx_packet.sample_data = (int16_t)(sample_counter % 4096); 
}

void init_sampling_subsystem(void) {
    gpio_reset_pin(GPIO_DEBUG_PIN);
    gpio_set_direction(GPIO_DEBUG_PIN, GPIO_MODE_OUTPUT);

    const esp_timer_create_args_t timer_args = {
        .callback = &sampling_timer_callback,
        .name = "dsp_sampling_clk",
        .dispatch_method = ESP_TIMER_ISR 
    };

    esp_timer_handle_t timer_handle;
    ESP_ERROR_CHECK(esp_timer_create(&timer_args, &timer_handle));
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer_handle, SAMPLING_PERIOD_US));
}

