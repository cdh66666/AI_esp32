idf_component_register(SRCS "ap_wifi.c" "wifi_manager.c" "main.c" "ws_server.c" "button.c" "XL9555.c"
                    INCLUDE_DIRS ".")

spiffs_create_partition_image(html ../html FLASH_IN_PROJECT)