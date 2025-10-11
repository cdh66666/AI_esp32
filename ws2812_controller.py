from machine import Pin
import neopixel
import time

class WS2812Controller:
    def __init__(self, pin_num, led_count):
        # 初始化WS2812灯带
        self.np = neopixel.NeoPixel(Pin(pin_num), led_count)
        self.led_count = led_count
        self.clear()  # 初始化全灭

    def clear(self):
        """熄灭所有LED"""
        for i in range(self.led_count):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def set_color(self, r, g, b):
        """设置所有LED为相同颜色"""
        for i in range(self.led_count):
            self.np[i] = (r, g, b)
        self.np.write()
    
    def set_single_led(self, index, r, g, b):
        """
        单独设置指定索引的LED颜色
        :param index: LED索引（从0开始）
        :param r: 红色值（0-255）
        :param g: 绿色值（0-255）
        :param b: 蓝色值（0-255）
        """
        # 检查索引是否有效
        if 0 <= index < self.led_count:
            self.np[index] = (r, g, b)
            self.np.write()
        else:
            print(f"错误：LED索引 {index} 无效，有效范围是 0 到 {self.led_count-1}")
    
 