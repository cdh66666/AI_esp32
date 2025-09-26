#include <stdio.h>
#include "button.h"
#include "XL9555.h"
#include "esp_log.h"
#include "ap_wifi.h"
#include "nvs_flash.h"


#define  TAG "main"
volatile uint16_t xl9555_button_level = 0xFFFF;



//xl9555电平变化回调函数
void xl9555_input_callback(uint16_t io_num,int level)
{
    if(level)
        xl9555_button_level |= io_num;
    else
        xl9555_button_level &= ~io_num;

}

//短按回调函数
void btn_short_press_callback(int gpio)
{
    ESP_LOGI(TAG,"Button GPIO %d short pressed\n", gpio);
}
//长按回调函数
void btn_long_press_callback(int gpio)
{
    ap_wifi_apcfg();
}

int get_gpio_level_handle(int gpio)
{
   return xl9555_button_level & gpio ? 1 : 0;
}

void wifi_state_callback(wifi_STATE state)
{
    if (state ==  wifi_STATE_CONNECTED)
    {
        ESP_LOGI(TAG,"wifi connected");
    } 
    if (state ==  wifi_STATE_DISCONNECTED)
    {
        ESP_LOGI(TAG,"wifi disconnected");
    } 
}




void app_main(void)
{
    nvs_flash_init();
    XL9555_init(GPIO_NUM_10,GPIO_NUM_11,GPIO_NUM_17 ,xl9555_input_callback);
    xl9555_ioconfig(0xFFFF); //IO0口为输入，IO1口为输出

    button_config_t btn_cfg = {
        .gpio_num = IO0_1, //使用XL9555的IO0_1作为按键
        .active_level = 0,
        .long_press_time = 3000, //长按时间3秒
        .short_press_cb = btn_short_press_callback,
        .long_press_cb = btn_long_press_callback,
        .get_level_cb = get_gpio_level_handle,
    };
    button_event_set(&btn_cfg);
    ap_wifi_init(wifi_state_callback);

}
