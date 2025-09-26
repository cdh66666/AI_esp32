#include "myled.h"


void app_main(void)
{
    // Configure the LED strip
    led_strip_handle_t led_strip = configure_led();

 
    waterfall_led(led_strip);


}