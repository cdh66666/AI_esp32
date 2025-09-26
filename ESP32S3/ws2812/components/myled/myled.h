#ifndef MYLED_H
#define MYLED_H
 
#include "led_strip.h"
led_strip_handle_t configure_led(void);
void blink_led(led_strip_handle_t led_strip);
void waterfall_led(led_strip_handle_t led_strip);
#endif // MYLED_H