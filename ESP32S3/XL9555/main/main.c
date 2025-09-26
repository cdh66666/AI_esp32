#include "stdio.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include "XL9555.h"
#include "esp_log.h"


#define TAG "main"
#define I2C_MASTER_SCL_IO GPIO_NUM_11       // SCL引脚
#define I2C_MASTER_SDA_IO GPIO_NUM_10       // SDA引脚
#define XL9555_INT_IO GPIO_NUM_17

void xl9555_callback(uint16_t pin,int level)
{
    switch(pin)
    {
        case IO0_1:
            ESP_LOGI(TAG,"1 %d",level);
            break;
        case IO0_2:
            ESP_LOGI(TAG,"2 %d",level);
            break;
        case IO0_3:
            ESP_LOGI(TAG,"3 %d",level);
            break;
        case IO0_4:
            ESP_LOGI(TAG,"4 %d",level);
            break;
        default:break;
    }
}

void ledc_init(void) 
{
    //初始化定时器
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = LEDC_LOW_SPEED_MODE, //低速模式
        .timer_num        = LEDC_TIMER_0,         //定时器0
        .duty_resolution  = LEDC_TIMER_12_BIT,    //12位分辨率
        .freq_hz          = 5000,                 //频率5kHz
        .clk_cfg          = LEDC_AUTO_CLK          //自动选择时钟
    }; 
    ledc_timer_config(&ledc_timer);

    //初始化PWM通道
    ledc_channel_config_t ledc_channel = {
        .speed_mode     = LEDC_LOW_SPEED_MODE, //低速模式
        .channel        = LEDC_CHANNEL_0,      //通道0
        .timer_sel      = LEDC_TIMER_0,        //选择定时器0
        .intr_type      = LEDC_INTR_DISABLE,   //关闭中断
        .gpio_num       = GPIO_NUM_15,         //GPIO15
        .duty           = 0,                   //占空比为0
        .hpoint         = 0                    //从计数值0开始
    };
    ledc_channel_config(&ledc_channel);


    //渐变
    ledc_fade_func_install(0); //安装渐变功能


}





void app_main(void)
{
    ledc_init();
 
    XL9555_init(I2C_MASTER_SDA_IO,I2C_MASTER_SCL_IO,XL9555_INT_IO,xl9555_callback);
    xl9555_ioconfig(0xFFFF);
    



    while(1)
    {
    //设置从0到4095的渐变，时间5秒
    ledc_set_fade_with_time(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 4095, 100); 
    ledc_fade_start(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, LEDC_FADE_WAIT_DONE); //开始渐变
    vTaskDelay(1000 / portTICK_PERIOD_MS); //延时1秒
    //设置从4095到0的渐变，时间5秒
    ledc_set_fade_with_time(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0, 1000);
    ledc_fade_start(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, LEDC_FADE_WAIT_DONE); //开始渐变
    vTaskDelay(1000 / portTICK_PERIOD_MS); //延时1秒
    }

}