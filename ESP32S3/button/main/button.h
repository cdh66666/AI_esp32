#pragma once

#include "esp_err.h"
 

typedef void(*button_press_cb_t)(int gpio);


//获取GPIO电平的操作回调函数
typedef int(*button_getlevel_cb_t)(int gpio);

typedef struct 
{
    int gpio_num;         // GPIO编号
    int active_level;    // 按键按下时的电平
    int long_press_time; // 长按时间，单位ms
    button_press_cb_t short_press_cb; // 短按回调
    button_press_cb_t long_press_cb;  // 长按回调
    button_getlevel_cb_t get_level_cb; // 获取GPIO电平的操作回调函数
}button_config_t;


typedef  enum
{
    BUTTON_RELEASE,      // 按键释放
    BUTTON_PRESS,        // 按键按下(消抖状态)
    BUTTON_HOLD,        // 按键保持按下
    BUTTON_LONG_PRESS_HOLD   // 按键长按，等待松手

}BUTTON_STATE;

typedef struct Button_info
{
    /* data */
    button_config_t btn_cfg;
    BUTTON_STATE state;      // 按键状态
    int press_time;         // 按键按下时间，单位ms
    struct Button_info *next; // 指向下一个按键结构体
 
}button_info_t;

esp_err_t button_event_set(button_config_t* cfg);