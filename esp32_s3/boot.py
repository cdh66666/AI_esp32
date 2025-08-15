# MicroPython代码：手机网页控制SG90舵机角度（适用于esp32-s3）
# 使用Thonny上传本文件到开发板


import network
import socket
import time
from machine import Pin, PWM

# 全局变量：自动模式状态
auto_mode = False

# WiFi配置
SSID = '超级无敌大帅哥'
PASSWORD = 'qwerty123'


# 两个舵机PWM配置
servo1 = PWM(Pin(2), freq=50)
servo2 = PWM(Pin(15), freq=50)

def set_angle(servo, angle):
	# SG90舵机0-180度，脉宽约0.5ms-2.5ms
	min_us = 500
	max_us = 2500
	us = min_us + (max_us - min_us) * angle // 180
	duty = int(us * 1023 // 20000)  # 20ms周期
	servo.duty(duty)

# 连接WiFi
def connect_wifi():
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	if not wlan.isconnected():
		print('Connecting to network...')
		wlan.connect(SSID, PASSWORD)
		while not wlan.isconnected():
			pass
	print('Network config:', wlan.ifconfig())
	return wlan.ifconfig()[0]

def is_int(val):
    try:
        int(val)
        return True
    except:
        return False

def parse_params(param_str):
    params = {}
    for pair in param_str.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            params[k] = v  # 这里可以加解码
    return params

# 简单网页服务器
def web_server(ip):
    global auto_mode
    html = """
<html><head><meta charset='utf-8'><title>SG90 Servo Control</title>
<style>
body { font-family: Arial; }
.slider-box { margin-bottom: 20px; }
.angle-value { font-weight: bold; color: #0078d7; }
</style>
</head>
<body>
<h2>手机滑动控制两个SG90舵机</h2>
<div class="slider-box">
  舵机1角度(0-180):
  <input id="angle1" type="range" min="0" max="180" value="90" oninput="showValue(1);sendAngle()">
  <span id="val1" class="angle-value">90</span>
</div>
<div class="slider-box">
  舵机2角度(0-180):
  <input id="angle2" type="range" min="0" max="180" value="90" oninput="showValue(2);sendAngle()">
  <span id="val2" class="angle-value">90</span>
</div>
<script>
function showValue(idx) {
  var v = document.getElementById('angle'+idx).value;
  document.getElementById('val'+idx).innerText = v;
}
function sendAngle() {
  var v1 = document.getElementById('angle1').value;
  var v2 = document.getElementById('angle2').value;
  var url = '/?angle1=' + v1 + '&angle2=' + v2;
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.send();
}
</script>
</body></html>
    """
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print('Web server started, connect your phone to: http://%s' % ip)
    last_manual = time.ticks_ms()
    while True:
        cl, addr = s.accept()
        req = cl.recv(1024)
        req = req.decode()
        angle1 = None
        angle2 = None
        manual_set = False
        #print("req:",req)
        # 只保留如下参数解析和设置
        if 'GET /?' in req:
 
            param_str = req.split(' ')[1][2:].split(' ')[0]
            params = parse_params(param_str)

            # print("params:", params)
            # print("params_str:", param_str)
            
            if 'angle1' in params and is_int(params['angle1']):
                angle1 = int(params['angle1'])
                print("angle1:", angle1)
                if 0 <= angle1 <= 180:
                    set_angle(servo1, angle1)
            if 'angle2' in params and is_int(params['angle2']):
                angle2 = int(params['angle2'])
                print("angle2:", angle2)
                if 0 <= angle2 <= 180:
                    set_angle(servo2, angle2)
 
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html; charset=utf-8\r\n\r\n')
        cl.send(html)
        cl.close()
 

ip = connect_wifi()
set_angle(servo1, 90)
set_angle(servo2, 90)
web_server(ip)

