# main.py
from wifi_manager import WiFiManager
from chinese_input import ChineseInputHandler
from deepseek_client import DeepSeekClient
from ws2812_controller import WS2812Controller
from config import WIFI_SSID, WIFI_PASSWORD, API_KEY, LED_PIN, LED_COUNT, MAID_PROMPT
# 导入拆分后的模块
from cmd_handler import CmdHandler
from light_parser import LightParser

def main():
    # 1. 核心组件初始化（仅1次，逻辑集中）
    wifi = WiFiManager(WIFI_SSID, WIFI_PASSWORD)
    input_handler = ChineseInputHandler()
    chat_client = DeepSeekClient(API_KEY, system_prompt=MAID_PROMPT)
    led_ctrl = WS2812Controller(LED_PIN, LED_COUNT)
    # 初始化拆分模块（注入依赖）
    light_parser = LightParser(led_ctrl)

    # 2. WiFi连接（结果判断，失败直接退出）
    success, wifi_msg = wifi.connect()
    print(wifi_msg)
    if not success:
        return

    # 3. 欢迎信息（简洁提示）
    print("欢迎使用对话系统～")
    print("提示：输入'exit'退出 | 'clear'清空历史 | 'show'查看聊天记录 | 例：'第1个灯亮红灯'\n")

    # 4. 核心对话循环（仅调度，无具体业务逻辑）
    while True:
        # 4.1 获取用户输入
        user_input = input_handler.get_input("你: ")

        # 4.2 处理特殊指令（show/exit/clear）
        cmd_result = CmdHandler.process_cmd(user_input, chat_client, wifi)
        if cmd_result is False:  # exit指令返回False，退出循环
            break
        if cmd_result is True:  # show/clear指令返回True，跳过后续逻辑
            continue

        # 4.3 调用大模型对话
        success, reply = chat_client.chat_stream(user_input, wifi)
        if not success:
            print(f"Deepseek: {reply}")
            continue

        # 4.4 解析灯控指令（有则处理，无则显示聊天回复）
        light_handled = light_parser.process_light_reply(reply)


if __name__ == "__main__":
    main()