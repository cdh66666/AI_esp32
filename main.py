from wifi_manager import WiFiManager
from chinese_input import ChineseInputHandler
from deepseek_client import DeepSeekClient
from ws2812_controller import WS2812Controller
from config import WIFI_SSID, WIFI_PASSWORD, API_KEY, LED_PIN, LED_COUNT, MAID_PROMPT
from cmd_handler import CmdHandler
from light_parser import LightParser

def main():
    # 1. 核心组件初始化（仅1次，逻辑集中）
    wifi = WiFiManager(WIFI_SSID, WIFI_PASSWORD)
    input_handler = ChineseInputHandler()
    # 初始化DeepSeekClient（已包含摘要文件管理逻辑）
    chat_client = DeepSeekClient(API_KEY, system_prompt=MAID_PROMPT)
    led_ctrl = WS2812Controller(LED_PIN, LED_COUNT)
    light_parser = LightParser(led_ctrl)

    try:
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
            # 4.1 获取用户输入（捕获输入时的KeyboardInterrupt）
            try:
                user_input = input_handler.get_input("你: ")
            except KeyboardInterrupt:
                # 输入时按Ctrl+C，触发保存退出流程
                raise  # 抛出异常，让外层try-except统一处理

            # 4.2 处理特殊指令（show/exit/clear）
            cmd_result = CmdHandler.process_cmd(user_input, chat_client, wifi)
            if cmd_result is False:  # exit指令返回False，主动触发保存退出
                # 调用DeepSeekClient的同步保存方法，等待摘要完成
                chat_client.trigger_summary_and_wait(wifi)
                break
            if cmd_result is True:  # show/clear指令返回True，跳过后续逻辑
                continue

            # 4.3 调用大模型对话
            success, reply = chat_client.chat_stream(user_input, wifi)
            if not success:
                print(f"Deepseek: {reply}")
                continue

            # 4.4 解析灯控指令（有则处理，无则显示聊天回复）
            light_parser.process_light_reply(reply)
            
    except KeyboardInterrupt:
        # 捕获用户中断（Ctrl+C），调用专用同步保存方法
        print("\n\n[提示] 检测到中断请求，正在保存对话摘要（请稍候）...")
        # 关键：调用DeepSeekClient的trigger_summary_and_wait，确保保存完成再退出
        # 传入wifi管理器，确保保存时WiFi连接有效
        chat_client.trigger_summary_and_wait(wifi)
        print("[提示] 对话摘要保存完成，程序退出～")
    except Exception as e:
        # 捕获其他未知错误，优先保存摘要再提示错误
        print(f"\n[错误] 程序发生异常：{str(e)[:30]}")
        print("[提示] 尝试紧急保存对话摘要...")
        chat_client.trigger_summary_and_wait(wifi)
        print("[提示] 紧急保存完成，程序退出～")
    finally:
        # 无论何种退出方式，确保LED关闭（释放硬件资源）
        print("\n[提示] 清理硬件资源...")
        led_ctrl.clear()
        print("[提示] 硬件资源清理完成～")

if __name__ == "__main__":
    main()