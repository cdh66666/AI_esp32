#include "myled.h"
#include "led_strip.h"
#include "esp_log.h"
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "myled";

led_strip_handle_t configure_led(void)
{
    // LED strip general initialization, according to your led board design
    led_strip_config_t strip_config = {
        .strip_gpio_num = 18, // The GPIO that connected to the LED strip's data line
        .max_leds = 3,        // The number of LEDs in the strip,
        .led_model = LED_MODEL_WS2812,        // LED strip model
        .color_component_format = LED_STRIP_COLOR_COMPONENT_FMT_GRB, // The color order of the strip: GRB
        .flags = {
            .invert_out = false, // don't invert the output signal
        }
    };

    // LED strip backend configuration: RMT
    led_strip_rmt_config_t rmt_config = {
        .clk_src = RMT_CLK_SRC_DEFAULT,        // different clock source can lead to different power consumption
        .resolution_hz = 10 * 1000 * 1000, // RMT counter clock frequency
        .mem_block_symbols = 0, // let the driver choose a proper memory block size automatically
        .flags = {
            .with_dma = 0,     // Using DMA can improve performance when driving more LEDs
        }
    };

    // LED Strip object handle
    led_strip_handle_t led_strip;
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip));
    ESP_LOGI(TAG, "Created LED strip object with RMT backend");
    return led_strip;
}

void blink_led(led_strip_handle_t led_strip)
{
    bool led_on_off = false;

    ESP_LOGI(TAG, "Start blinking LED strip");
    while (1) {
        if (led_on_off) {
            // Set all LED off
            ESP_ERROR_CHECK(led_strip_clear(led_strip));
            led_on_off = false;
        } else {
            // 循环设置第 0~2 个像素为白色（共 3 个像素）
            for (int i = 0; i < 3; i++) {
                // 参数：led_strip 对象 → 像素索引 → R → G → B
                ESP_ERROR_CHECK(led_strip_set_pixel(led_strip, i, 0, 255, 255));
            }
            // 设置完成后，必须调用 refresh 刷新显示
            ESP_ERROR_CHECK(led_strip_refresh(led_strip));
            ESP_ERROR_CHECK(led_strip_refresh(led_strip));
            led_on_off = true;
        }
        vTaskDelay(pdMS_TO_TICKS(1000)); // wait for a second
    }
}


void waterfall_led(led_strip_handle_t led_strip)
{
    int pixel_count = 3; // 总LED数量，可根据实际情况调整
    int current_pixel = 0;

    ESP_LOGI(TAG, "Start waterfall LED effect");
    while (1) {
        // 先清除所有LED
        ESP_ERROR_CHECK(led_strip_clear(led_strip));
        
        // 只点亮当前像素（青色）
        ESP_ERROR_CHECK(led_strip_set_pixel(led_strip, current_pixel, 0, 255, 255));
        
        // 刷新显示
        ESP_ERROR_CHECK(led_strip_refresh(led_strip));
        
        // 移动到下一个像素，循环往复
        current_pixel = (current_pixel + 1) % pixel_count;
        
        // 每个像素停留500ms
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
