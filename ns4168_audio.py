from machine import Pin, I2S
import math
import time
import array

class AudioPlayer:
    def __init__(self, bclk_pin, lrck_pin, dout_pin, dtmf_sample_rate=8000, volume=3000):
        """
        初始化音频播放器
        :param bclk_pin: I2S BCLK引脚
        :param lrck_pin: I2S LRCK引脚
        :param dout_pin: I2S DOUT引脚
        :param dtmf_sample_rate: DTMF信号采样率
        :param volume: 初始音量（最大建议16000）
        """
        self.bclk = Pin(bclk_pin)
        self.lrck = Pin(lrck_pin)
        self.dout = Pin(dout_pin)
        self.dtmf_sample_rate = dtmf_sample_rate
        self.volume = volume
        self.i2s = None
        
        # DTMF频率表
        self.row_freqs = [697, 770, 852, 941]
        self.col_freqs = [1209, 1336, 1477, 1633]
        self.keys = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]
        
        # 初始化I2S
        self._init_i2s(self.dtmf_sample_rate, 16, I2S.MONO)
    
    def _init_i2s(self, sample_rate, bits, format):
        """初始化或重新配置I2S"""
        if self.i2s:
            self.i2s.deinit()
        
        self.i2s = I2S(
            0,
            sck=self.bclk,
            ws=self.lrck,
            sd=self.dout,
            mode=I2S.TX,
            bits=bits,
            format=format,
            rate=sample_rate,
            ibuf=4096
        )
    
    def set_volume(self, volume):
        """设置音量"""
        self.volume = min(max(volume, 0), 30000)  # 限制在0-16000范围
    
    def play_dtmf(self, f1, f2, duration_ms=300):
        """播放DTMF信号"""
        # 确保I2S配置正确
        self._init_i2s(self.dtmf_sample_rate, 16, I2S.MONO)
        
        samples = (duration_ms * self.dtmf_sample_rate) // 1000
        buffer = array.array('h', [0] * 256)
        
        for n in range(samples):
            t = n / self.dtmf_sample_rate
            sample = int((math.sin(2 * math.pi * f1 * t) + 
                         math.sin(2 * math.pi * f2 * t)) * self.volume)
            buffer[n % 256] = sample
            
            if (n + 1) % 256 == 0:
                self.i2s.write(buffer)
        
        remaining = samples % 256
        if remaining:
            self.i2s.write(buffer[:remaining])
        
        time.sleep_ms(10)
    
    def play_key(self, key):
        """播放指定按键的DTMF信号"""
        for r in range(4):
            for c in range(4):
                if self.keys[r][c] == key:
                    self.play_dtmf(self.row_freqs[r], self.col_freqs[c])
                    time.sleep_ms(50)
                    return
        print(f"未找到按键: {key}")
    
    def play_wav(self, filename):
        """播放WAV文件（支持16位单声道/立体声）"""
        try:
            with open(filename, "rb") as f:
                # 读取WAV文件头
                header = f.read(44)
                
                # 验证WAV格式
                if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    print("不是有效的WAV文件")
                    return
                
                # 解析WAV参数
                sample_rate = int.from_bytes(header[24:28], 'little')
                channels = int.from_bytes(header[22:24], 'little')
                bits_per_sample = int.from_bytes(header[34:36], 'little')
                
                # 检查位深度
                if bits_per_sample != 16:
                    print("只支持16位WAV文件")
                    return
                
                # 配置I2S
                i2s_format = I2S.MONO if channels == 1 else I2S.STEREO
                self._init_i2s(sample_rate, bits_per_sample, i2s_format)
                
                # 播放音频
                buffer = bytearray(1024)
                while True:
                    bytes_read = f.readinto(buffer)
                    if bytes_read == 0:
                        break
                    self.i2s.write(buffer[:bytes_read])
                
                # 恢复DTMF配置
                self._init_i2s(self.dtmf_sample_rate, 16, I2S.MONO)
                print(f"WAV文件 {filename} 播放完成")
                
        except OSError as e:
            print(f"文件错误: {e}")
        except Exception as e:
            print(f"播放错误: {e}")
            # 出错后恢复DTMF配置
            self._init_i2s(self.dtmf_sample_rate, 16, I2S.MONO)
    
    def deinit(self):
        """释放资源"""
        if self.i2s:
            self.i2s.deinit()
            self.i2s = None
    
    
    
    
    

# ------------------测试程序------------------
def main():
    from xl9555 import XL9555
    # 初始化XL9555并使能音频输出
    xl = XL9555(sda_pin=10, scl_pin=11, i2c_addr=0x20)
    xl.set_single_io_config(port=0, io_num=0, is_input=False)
    xl.set_single_io_level(port=0, io_num=0, level=True)
    time.sleep_ms(15)  # 等待启动完成
    
    # 初始化音频播放器
    player = AudioPlayer(
        bclk_pin=46,
        lrck_pin=9,
        dout_pin=8,
        volume=30000  # 设置初始音量
    )
    
    try:
        print("音频播放器测试开始...")
        while True:
            # 播放WAV文件
            print("播放WAV文件...")
            player.play_wav("test_audio.wav")
            time.sleep_ms(1000)
            
            # 播放DTMF序列
            print("播放DTMF序列 1350#...")
            for key in ['1', '3', '5', '0', '#']:
                player.play_key(key)
            
            # 等待2秒后重复
            time.sleep_ms(2000)
            
    except KeyboardInterrupt:
        print("测试结束")
    finally:
        player.deinit()

if __name__ == "__main__":
    main()
    