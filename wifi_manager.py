import network
import time

class WiFiManager:
    def __init__(self, ssid, password):
        """初始化WiFi管理器"""
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
    
    def is_connected(self):
        """检查是否已连接WiFi"""
        return self.wlan.isconnected()
    
    def connect(self, max_retry=3):
        """连接WiFi，支持重试机制"""
        # 如果已连接，直接返回
        if self.is_connected():
            ip = self.wlan.ifconfig()[0]
            return True, f"WiFi已连接，IP: {ip}"
        
        # 重试连接
        for retry in range(max_retry):
            try:
                self.wlan.connect(self.ssid, self.password)
                
                # 等待连接（每次尝试最多等10秒）
                for _ in range(10):
                    if self.is_connected():
                        ip = self.wlan.ifconfig()[0]
                        return True, f"WiFi连接成功，IP: {ip}"
                    time.sleep(1)
            except Exception as e:
                return False, f"连接出错: {str(e)}"
        
        # 多次重试失败
        return False, f"WiFi连接失败（已重试{max_retry}次）"
    
    def disconnect(self):
        """断开WiFi连接"""
        if self.is_connected():
            self.wlan.disconnect()
            return True, "已断开WiFi连接"
        return False, "未连接WiFi，无需断开"
    
    def get_ip(self):
        """获取当前IP地址"""
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None
    