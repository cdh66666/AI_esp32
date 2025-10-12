import machine
import time
import math
from xl9555 import XL9555

class NS4168Audio:
    def __init__(self, 
                 sck_pin=46,    # NS4168 BCLK引脚
                 ws_pin=9,     # NS4168 LRCLK引脚
                 sd_pin=8,     # NS4168 SDATA引脚
                 ctrl_port=0,  # XL9555控制NS4168 CTRL的端口
                 ctrl_io=0,    # XL9555控制NS4168 CTRL的IO
                 sample_rate=16000,  # 采样率（匹配表2：16kHz对应BCLK 256kHz）
                 bits=16
                 ):
        # 1. 初始化XL9555并使能NS4168（CTRL引脚置高）
        self.xl = XL9555(sda_pin=10, scl_pin=11, i2c_addr=0x20)
        self.xl.set_single_io_config(port=ctrl_port, io_num=ctrl_io, is_input=False)
        self.xl.set_single_io_level(port=ctrl_port, io_num=ctrl_io, level=True)
        time.sleep_ms(15)  # 满足NCN启动10ms要求
        print("NS4168已使能")

        # 2. 配置I2S引脚为输出模式
        self.bclk = machine.Pin(sck_pin, machine.Pin.OUT)
        self.lrclk = machine.Pin(ws_pin, machine.Pin.OUT)
        self.sdata = machine.Pin(sd_pin, machine.Pin.OUT)
        self.bclk.value(0)
        self.lrclk.value(0)
        self.sdata.value(0)

        self.sample_rate = sample_rate
        self.bits = bits
        # BCLK频率 = 采样率 × 位深（表2：16kHz采样率→256kHz BCLK）
        self.bclk_freq = sample_rate * bits  
        self.bclk_period_us = int(1_000_000 / self.bclk_freq)  # BCLK周期（微秒）

    def _send_bit(self, bit):
        """模拟BCLK上升沿发送1位数据（严格时序）"""
        self.bclk.value(0)
        self.sdata.value(bit)
        time.sleep_us(self.bclk_period_us // 2)  # 保持数据稳定
        self.bclk.value(1)
        time.sleep_us(self.bclk_period_us // 2)

    def _send_sample(self, sample):
        """发送1个16位采样值（MSB优先，匹配图1时序）"""
        self.lrclk.value(0)  # 左声道（单声道固定左声道）
        # 从最高位(MSB)到最低位(LSB)依次发送
        for i in range(self.bits - 1, -1, -1):
            self._send_bit((sample >> i) & 1)
        self.lrclk.value(1)  # 右声道（单声道可省略，保持时序完整）

    def play_test_tone(self, duration_ms=2000):
        """播放固定幅度测试音（1/8满幅，避免NCN防失真）"""
        total_samples = self.sample_rate * duration_ms // 1000
        fixed_val = 4096  # 1/8满幅（0~32767范围）

        print(f"开始播放测试音（{duration_ms}ms，幅度{fixed_val}）...")
        start = time.ticks_ms()
        sample_count = 0

        while sample_count < total_samples and time.ticks_diff(time.ticks_ms(), start) < duration_ms + 1000:
            self._send_sample(fixed_val)
            sample_count += 1
        print("测试音播放完成")

    def play_sine(self, duration_ms=2000, freq=1000):
        """播放正弦波测试音（更易识别）"""
        total_samples = self.sample_rate * duration_ms // 1000

        print(f"开始播放{freq}Hz正弦波（{duration_ms}ms）...")
        start = time.ticks_ms()
        sample_count = 0

        while sample_count < total_samples and time.ticks_diff(time.ticks_ms(), start) < duration_ms + 1000:
            # 生成正弦波采样值（16位范围：0~32767）
            sample = int(8192 * math.sin(2 * math.pi * freq * sample_count / self.sample_rate))
            self._send_sample(sample)
            sample_count += 1
        print("正弦波播放完成")

    def stop(self):
        """关断NS4168（CTRL引脚置低）"""
        self.xl.set_single_io_level(port=0, io_num=0, level=False)
        # 重置引脚电平
        self.bclk.value(0)
        self.lrclk.value(0)
        self.sdata.value(0)
        print("NS4168已关断")

# 测试逻辑
if __name__ == "__main__":
    try:
        audio = NS4168Audio()
        # 先尝试固定电平测试音
        audio.play_test_tone(duration_ms=2000)
        # 再尝试1kHz正弦波（更易听出是否发声）
        audio.play_sine(duration_ms=2000, freq=1000)
    finally:
        if 'audio' in locals():
            audio.stop()