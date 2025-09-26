#include "ap_wifi.h"
#include "esp_spiffs.h"
#include "string.h"
#include "ws_server.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include <sys/stat.h>
#include "esp_log.h"

#define SPIFF_MOUNT "/spiffs"
#define HTML_PATH "/spiffs/apcfg.html"
#define TAG "ap_wifi"


static char* html_code = NULL;
static char current_ssid[32] = {0};
static char current_password[64] = {0};
static EventGroupHandle_t apcfg_ev;
#define APCFG_BIT (BIT0)


char *init_web_page_buffer(void)
{
    esp_vfs_spiffs_conf_t conf = {
        .base_path = SPIFF_MOUNT,
        .partition_label = NULL,
        .max_files = 3,
        .format_if_mount_failed = false,
    };

    esp_vfs_spiffs_register(&conf);
    struct stat st;
    if(stat(HTML_PATH, &st))
    {
        return NULL;
    }
    char *buf = malloc(st.st_size + 1);
    memset(buf, 0, st.st_size + 1);
    FILE *fp = fopen(HTML_PATH, "r");
    if(fp)
    {
        if(fread(buf,st.st_size,1,fp) == 0)
        {
            free(buf);
            buf = NULL; 
        }
        fclose(fp);
        
    }
    else
    {
        free(buf);
        buf = NULL; 
    }
    return buf;
}

static void ap_wifi_task(void* param)
{
    EventBits_t ev;
    while(1)
    {
        ev = xEventGroupWaitBits(apcfg_ev,APCFG_BIT,pdTRUE,pdFALSE,pdMS_TO_TICKS(10*1000));
        if(ev & APCFG_BIT)
        {
            web_ws_stop();
            wifi_manager_connect(current_ssid,current_password);
        }
    }
}

void ap_wifi_init(p_wifi_state_cb f)
{
    wifi_manager_init(f);
    html_code = init_web_page_buffer();
    apcfg_ev = xEventGroupCreate();
    xTaskCreatePinnedToCore(ap_wifi_task,"ap_wifi_task",4*1024,NULL,3,NULL,1);
}

void ap_wifi_connect(void)
{

}

void wifi_scan_handle(int num, wifi_ap_record_t* ap_records)
{
    cJSON *root = cJSON_CreateObject();
    cJSON *wifilist_js = cJSON_AddArrayToObject(root,"wifi_list");
    for(int i=0;i<num;i++)
    {
        cJSON *wifi_js = cJSON_CreateObject();
        cJSON_AddStringToObject(wifi_js,"ssid",(char*)ap_records[i].ssid);
        cJSON_AddNumberToObject(wifi_js,"rssi",ap_records[i].rssi);
        cJSON_AddBoolToObject(wifi_js,"encrypted",ap_records[i].authmode != WIFI_AUTH_OPEN);
        cJSON_AddItemToArray(wifilist_js,wifi_js);
    }
    char *data = cJSON_Print(root);
    ESP_LOGI(TAG,"WS send: %s",data);
    web_ws_send((uint8_t*)data,strlen(data));
    cJSON_free(data);
    cJSON_Delete(root);
}

static void ws_receive_handle(uint8_t *payload,int len)
{
    cJSON *root = cJSON_Parse((char *)payload);
    if(root) 
    {
        cJSON *scan_js = cJSON_GetObjectItem(root,"scan");
        cJSON *ssid_js = cJSON_GetObjectItem(root,"ssid");
        cJSON *password_js = cJSON_GetObjectItem(root,"password_js");
        if(scan_js)
        {
            char *scan_value = cJSON_GetStringValue(scan_js);
            if(strcmp(scan_value,"start") == 0)
            {
                //启动扫描
                wifi_manager_scan(wifi_scan_handle);
            }
        }
        if(ssid_js && password_js)
        {
            char *ssid_value = cJSON_GetStringValue(ssid_js);
            char *password_value = cJSON_GetStringValue(password_js); 
            snprintf(current_ssid,sizeof(current_ssid),"%s",ssid_value);
            snprintf(current_password,sizeof(current_password),"%s",password_value);
            xEventGroupSetBits(apcfg_ev,APCFG_BIT);
            // web_ws_stop();
            // wifi_manager_connect(ssid_value,ssid_password);
        
        }
    
    }
    
}


//进入配网模式
void ap_wifi_apcfg(void)
{
    wifi_manager_ap();
    ws_cfg_t ws_cfg = 
    {
        .html_code = html_code,
        .receive_fn = ws_receive_handle,
    };
    web_ws_start(&ws_cfg);
    
}

