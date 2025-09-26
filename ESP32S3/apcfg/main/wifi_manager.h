#pragma once

#include "esp_err.h"
#include "esp_wifi.h"


typedef enum {
    wifi_STATE_CONNECTED,
    wifi_STATE_DISCONNECTED,
}wifi_STATE;


typedef void (*p_wifi_state_cb)(wifi_STATE);
typedef void (*p_wifi_scan_cb)(int num, wifi_ap_record_t* ap_records);
void wifi_manager_init(p_wifi_state_cb f);
 
esp_err_t wifi_manager_ap(void);

void wifi_manager_connect(const char* ssid,const char* password);

esp_err_t wifi_manager_scan(p_wifi_scan_cb f);