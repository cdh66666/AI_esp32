#pragma once

typedef enum {
    wifi_STATE_CONNECTED,
    wifi_STATE_DISCONNECTED,
}wifi_STATE;


typedef void (*p_wifi_state_cb)(wifi_STATE);

void wifi_manager_init(p_wifi_state_cb f);

void wifi_manager_connect(const char* ssid,const char* password);
