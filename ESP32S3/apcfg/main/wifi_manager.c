#include "wifi_manager.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "stdio.h"
#include "string.h"
#include "lwip/ip4_addr.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"    

#define MAX_CONNECT_RETRY  10
static int sta_connect_cnt = 0;//重连次数

#define TAG "wifi_manager"

static const char *ap_ssid_name = "ESP32S3";
static const char *ap_password = "12345678";

static SemaphoreHandle_t scan_sem = NULL;



//当前sta连接状态
static bool is_sta_connected = false;

//wifi状态回调函数
static p_wifi_state_cb wifi_callback = NULL;

static esp_netif_t* esp_netif_ap = NULL;

static void event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT)
    {
        switch (event_id) {
            case WIFI_EVENT_STA_START:
                esp_wifi_connect();  
                break;
            case WIFI_EVENT_STA_DISCONNECTED:
                if(is_sta_connected && wifi_callback)
                {
                    is_sta_connected=false;
                    wifi_callback(wifi_STATE_DISCONNECTED);
                }  
                if(sta_connect_cnt < MAX_CONNECT_RETRY){
                    esp_wifi_connect();
                    sta_connect_cnt++;
                    ESP_LOGI(TAG,"retry to connect to the AP");
                } 
                break;
            case WIFI_EVENT_STA_CONNECTED:
                ESP_LOGI(TAG,"wifi connected");
                break;
            case WIFI_EVENT_AP_STACONNECTED:
                ESP_LOGI(TAG,"sta connected to ap");
                break;
            case WIFI_EVENT_AP_STADISCONNECTED:
                ESP_LOGI(TAG,"sta disconnected from ap");
            default:
                break;
        }
    }
    else if (event_base == IP_EVENT)
    {
        switch (event_id) {
            case IP_EVENT_STA_GOT_IP:
            is_sta_connected=true;
                if(wifi_callback) wifi_callback(wifi_STATE_CONNECTED);
                ESP_LOGI(TAG,"got ip");
                break;
            default:
                break;
        }
    }
}



void wifi_manager_init(p_wifi_state_cb f)
{
    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    esp_netif_ap = esp_netif_create_default_wifi_ap();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL,
                                                        NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        IP_EVENT_STA_GOT_IP,
                                                        &event_handler,
                                                        NULL,
                                                        NULL));
    wifi_callback = f;
    scan_sem = xSemaphoreCreateBinary();
    xSemaphoreGive(scan_sem);
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA) );
  
    ESP_ERROR_CHECK(esp_wifi_start() );

}

void wifi_manager_connect(const char* ssid,const char* password)
{
    wifi_config_t wifi_config = {
        .sta = {
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };
    snprintf((char*)wifi_config.sta.ssid, 31, "%s", ssid);
    snprintf((char*)wifi_config.sta.password, 63, "%s", password);
 
   
    wifi_mode_t mode;
    ESP_ERROR_CHECK(esp_wifi_get_mode(&mode));
    if(mode != WIFI_MODE_STA){
        ESP_ERROR_CHECK(esp_wifi_stop());
        ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA) );
    }
    sta_connect_cnt=0;
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config) );
    ESP_ERROR_CHECK(esp_wifi_start() );
}


esp_err_t wifi_manager_ap(void)
{
 
    wifi_mode_t mode;
    ESP_ERROR_CHECK(esp_wifi_get_mode(&mode));
    if(mode == WIFI_MODE_APSTA)
    {
        return ESP_OK;
    }
    ESP_ERROR_CHECK(esp_wifi_disconnect());
    ESP_ERROR_CHECK(esp_wifi_stop());
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA) );
    wifi_config_t wifi_config = {
        .ap = {
            .channel = 5,
            .max_connection = 2,
            .authmode = WIFI_AUTH_WPA2_PSK,
        },
    };
    snprintf((char*)wifi_config.ap.ssid, 32,  "%s", ap_ssid_name);
    wifi_config.ap.ssid_len = strlen(ap_ssid_name);
    snprintf((char*)wifi_config.ap.password, 64,  "%s", ap_password);

    esp_wifi_set_config(WIFI_IF_AP, &wifi_config);

    esp_netif_ip_info_t ipInfo;
    IP4_ADDR(&ipInfo.ip, 192, 168, 100, 1);         //IP地址
    IP4_ADDR(&ipInfo.gw, 192, 168, 100, 1);         //网关地址
    IP4_ADDR(&ipInfo.netmask, 255, 255, 255, 0);    //子网掩码

    esp_netif_dhcps_stop(esp_netif_ap); //停止dhcp服务（自动分配ip的服务）
    esp_netif_set_ip_info(esp_netif_ap, &ipInfo);
    esp_netif_dhcps_start(esp_netif_ap); //启动dhcp服务

    return esp_wifi_start();

}


static void scan_task(void* param)
{
    p_wifi_scan_cb callback= (p_wifi_scan_cb)param;
    uint16_t ap_count = 0;
    uint16_t ap_num = 20;
    wifi_ap_record_t *ap_list = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t)*ap_num);
   
    esp_wifi_scan_start(NULL, true);
    esp_wifi_scan_get_ap_num(&ap_count);
    esp_wifi_scan_get_ap_records(&ap_num, ap_list);
    ESP_LOGI(TAG, "Total APs count: %d , actual ap number : %d", ap_count,ap_num);
    if(callback) callback(ap_num,ap_list);
    free(ap_list);
    xSemaphoreGive(scan_sem);
    vTaskDelete(NULL);
}

esp_err_t wifi_manager_scan(p_wifi_scan_cb f)
{
    if(xSemaphoreTake(scan_sem, 0))
    {
        esp_wifi_clear_ap_list();
        xTaskCreatePinnedToCore(scan_task, "scan_task", 8*1024, (void*)f, 3, NULL, 1);
    }
    return ESP_OK;
}