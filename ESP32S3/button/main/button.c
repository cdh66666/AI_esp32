#include "button.h"
#include "esp_log.h"
#include "string.h"
#include "esp_timer.h"

#define TAG "button"

static button_info_t *button_head = NULL;
static esp_timer_handle_t button_timer_handle;
static bool timer_running = false;
static void button_handler(void* arg);

esp_err_t button_event_set(button_config_t* cfg)
{
    button_info_t* btn = (button_info_t*)malloc(sizeof(button_info_t));
    if(!btn)
        return ESP_FAIL;
    memset(btn, 0, sizeof(button_info_t));
    memcpy(&btn->btn_cfg, cfg, sizeof(button_config_t));
    if(!button_head)
    {
        button_head = btn;
    }
    else
    {
        button_info_t* info = button_head;
        while(info->next)
            info = info->next;
        info->next = btn;

    }
    if (!timer_running)
    {
        timer_running = true;
    static int button_interval = 5; //按键扫描时间间隔，单位ms
 
    esp_timer_create_args_t button_timer = 
    {
        .callback = button_handler,
        .name = "button",
        .dispatch_method = ESP_TIMER_TASK,
        .arg = (void*)button_interval,

    };
    esp_timer_create(&button_timer,&button_timer_handle);
    esp_timer_start_periodic(button_timer_handle, button_interval * 1000); //定时器周期，单位us
    timer_running = true;
    }

    return ESP_OK;


}




static void button_handler(void* arg)
{
    button_info_t *btn_info = button_head;
    int interval = (int)arg; //按键扫描时间间隔，单位ms
    for(;btn_info;btn_info = btn_info->next)
    {
        int gpio_num = btn_info->btn_cfg.gpio_num;
        switch(btn_info->state)
        {
            
            case BUTTON_RELEASE:  //按键松开
                if(btn_info->btn_cfg.get_level_cb(gpio_num) == btn_info->btn_cfg.active_level)
                {
                    btn_info->state = BUTTON_PRESS;
                    btn_info->press_time += interval;
                }
                break;
            case BUTTON_PRESS:   //按键按下(消抖状态)
                if(btn_info->btn_cfg.get_level_cb(gpio_num) == btn_info->btn_cfg.active_level)
                {
                    btn_info->press_time += interval;
                    if(btn_info->press_time >= 50) //按键消抖时间50ms
                    {
                        if(btn_info->btn_cfg.short_press_cb)
                            btn_info->btn_cfg.short_press_cb(gpio_num);
                        btn_info->state = BUTTON_HOLD;
                    }
                }
                else
                {
                    btn_info->state = BUTTON_RELEASE;
                    btn_info->press_time = 0;
                }
                break;
            case BUTTON_HOLD:
                if(btn_info->btn_cfg.get_level_cb(gpio_num) == btn_info->btn_cfg.active_level)
                {
                    btn_info->press_time += interval;
                    if(btn_info->press_time >= btn_info->btn_cfg.long_press_time) //长按时间
                    {
                        if(btn_info->btn_cfg.long_press_cb)
                            btn_info->btn_cfg.long_press_cb(gpio_num);
                        btn_info->state = BUTTON_LONG_PRESS_HOLD;
                    }
                }
                else
                {
                    btn_info->state = BUTTON_RELEASE;
                    btn_info->press_time = 0;
                }
                break;
            case BUTTON_LONG_PRESS_HOLD:
                if(btn_info->btn_cfg.get_level_cb(gpio_num) != btn_info->btn_cfg.active_level)
                {
                    btn_info->state = BUTTON_RELEASE;
                    btn_info->press_time = 0;
                }
                break;
            default:break;
        }
    }


}





