#include <stdio.h>
#include "esp32-s3-szp.h"

static const char *TAG = "main";

t_sQMI8658 QMI8658; // 定义QMI8658结构体变量


void app_main(void)
{
    ESP_ERROR_CHECK(i2c_master_init());
    ESP_LOGI(TAG, "I2C initialized successfully");
    qmi8658_init();
    while (1)
    {
        vTaskDelay(10 / portTICK_PERIOD_MS);  // 延时1000ms
        qmi8658_fetch_angleFromAcc(&QMI8658);   // 获取XYZ轴的倾角
        // 输出XYZ轴的倾角
        // ESP_LOGI(TAG, "angle_x : %.2f , angle_y : %.2f ,angle_z : %.2f",QMI8658.AngleX, QMI8658.AngleY, QMI8658.AngleZ);
        printf("angle_x : %.2f , angle_y : %.2f ,angle_z : %.2f\n", QMI8658.AngleX, QMI8658.AngleY, QMI8658.AngleZ);
    }
}
