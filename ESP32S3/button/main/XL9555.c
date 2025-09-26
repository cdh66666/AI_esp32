#include "XL9555.h"
#include "driver/i2c_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

 

#define XL9555_ADDR 0x20  // I2C地址，根据实际连接调整
 
static i2c_master_bus_handle_t *xl9555_bus_handle = NULL;
static i2c_master_dev_handle_t *xl9555_dev_handle = NULL;
static EventGroupHandle_t xl9555_io_event = NULL;
static xl9555_input_cb_t xl9555_io_callback = NULL;
static  gpio_num_t xl9555_int_io;


#define XL9555_ISR_BIT BIT0


static void IRAM_ATTR xl9555_int_handle(void* arg)
{
    BaseType_t taskWake;
    xEventGroupSetBitsFromISR(xl9555_io_event, XL9555_ISR_BIT, &taskWake);
    portYIELD_FROM_ISR(taskWake);
}

static void xl9555_task(void* param)
{
    EventBits_t ev;
    uint16_t last_input;
    XL9555_read_word(0x00,&last_input);
    while(1)
    {
        ev = xEventGroupWaitBits(xl9555_io_event,XL9555_ISR_BIT,pdTRUE,pdFALSE,portMAX_DELAY);
        if(ev&XL9555_ISR_BIT)
        {
            uint16_t input=0;
            esp_rom_delay_us(1000);
            if(gpio_get_level(xl9555_int_io)!=0)
            {
                continue;
            }
            esp_err_t ret = XL9555_read_word(0x00,&input);
            if(ret == ESP_OK)
            {
                for(int i=0;i<16;i++)
                {
                    uint8_t last_value = last_input&(1<<i)?1:0;
                    uint8_t value = input&(1<<i)?1:0;
                    if(value != last_value && xl9555_io_callback)
                    {
                        xl9555_io_callback((1<<i),value);
                    }
                }
            }
            last_input = input;
        }
    }
}

//初始化I2C和XL9555器件的函数
esp_err_t XL9555_init(gpio_num_t sda_io, gpio_num_t scl_io,gpio_num_t int_io,xl9555_input_cb_t f)
{

    i2c_master_bus_config_t bus_config = {
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .sda_io_num = sda_io,
        .scl_io_num = scl_io,
        .glitch_ignore_cnt = 7,
        .i2c_port = 0,
    };
    i2c_new_master_bus(&bus_config,&xl9555_bus_handle);

    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_7,
        .device_address = XL9555_ADDR,
        .scl_speed_hz = 100000,
    };
    i2c_master_bus_add_device(xl9555_bus_handle, &dev_config, &xl9555_dev_handle);

    xl9555_io_callback = f;
    if(int_io != GPIO_NUM_NC)
    {
        xl9555_io_event = xEventGroupCreate();
        xl9555_int_io = int_io;
        gpio_config_t io_conf = {
            .mode = GPIO_MODE_INPUT,
            .pin_bit_mask = (1ULL << int_io),
            .pull_up_en = GPIO_PULLUP_ENABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_NEGEDGE,
        };
        gpio_config(&io_conf);
        gpio_install_isr_service(0);
        gpio_isr_handler_add(int_io, xl9555_int_handle, (void*)int_io);
    
        xTaskCreatePinnedToCore(xl9555_task,"xl9555",4096,NULL,3,NULL,1);
    
    
    }
    return ESP_OK;
}

    

//写入2个字节到指定寄存器地址
esp_err_t XL9555_write_word(uint8_t reg, uint16_t data)
{
    uint8_t write_buffer[3];
    write_buffer[0] = reg;          //寄存器地址
    write_buffer[1] = data & 0xFF;  //低字节
    write_buffer[2] = (data >> 8) & 0xFF; //高字节

    return i2c_master_transmit(xl9555_dev_handle, write_buffer, sizeof(write_buffer), 500);
}

//读入2个字节从指定寄存器地址
esp_err_t XL9555_read_word(uint8_t reg, uint16_t *data)
{
    uint8_t addr[1];
    addr[0] = reg; //寄存器地址
    return i2c_master_transmit_receive(xl9555_dev_handle, addr, 1, (uint8_t*) data, 2, 500);
}


esp_err_t xl9555_ioconfig(uint16_t config)
{
    esp_err_t ret;
    do
    {
        ret = XL9555_write_word(0x06, config);
        vTaskDelay(pdMS_TO_TICKS(150));
    } while (ret != ESP_OK);
    
    return  ret;
}


int xl9555_pin_read(uint16_t pin)
{
    uint16_t data = 0;
    XL9555_read_word(0x00, &data);
    return (data & pin) ? 1 : 0;
}


esp_err_t xl9555_pin_write(uint16_t pin, uint8_t level)
{
    uint16_t data = 0;
    XL9555_read_word(0x02, &data);
    if (level)
        data |= pin;
    else
        data &= ~pin;
    return XL9555_write_word(0x02, data);
}