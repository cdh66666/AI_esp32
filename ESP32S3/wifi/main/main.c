#include <stdio.h>
#include "wifi_manager.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TAG "main"

#define WIFI_SSID "超级无敌大帅哥"
#define WIFI_PASSWORD "qwerty123"

void wifi_state_handler(wifi_STATE state)
{

    switch(state)
    {
        case wifi_STATE_CONNECTED:
            ESP_LOGI(TAG,"wifi connected");
            break;
        case wifi_STATE_DISCONNECTED:
            ESP_LOGI(TAG,"wifi disconnected");
            break;
        default:
            break;
    }
}


void app_main(void)
{
    nvs_flash_init();
    wifi_manager_init(wifi_state_handler);
    wifi_manager_connect(WIFI_SSID,WIFI_PASSWORD);
    while (1)
    {
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }

}
