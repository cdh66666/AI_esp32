# cmd_handler.py
import os
from deepseek_client import DeepSeekClient

class CmdHandler:
    @staticmethod
    def handle_show():
        """处理 show 指令：查看聊天记录摘要"""
        if "chat_summary.txt" in os.listdir():
            try:
                with open("chat_summary.txt", "r", encoding="utf-8") as f:
                    summary = f.read().strip()
                print("\n" + "="*30)
                print("当前聊天记录摘要：")
                print(summary if summary else "暂无聊天记录")
                print("="*30 + "\n")
            except Exception as e:
                print(f"Deepseek: 读取记录时出了点小问题～({str(e)[:15]})")
        else:
            print("Deepseek: 还没有聊天记录呢，先和我聊聊天吧～")
        return True  # 表示已处理指令

    @staticmethod
    def handle_exit(chat_client, wifi):
        """处理 exit 指令：保存记录并退出"""
        print("Deepseek: 正在保存聊天记录，主人再见～")
        chat_client.trigger_summary_and_wait(wifi)
        return False  # 表示需要退出循环

    @staticmethod
    def handle_clear(chat_client):
        """处理 clear 指令：清空历史记录"""
        chat_client.clear_history()
        print("Deepseek: 历史已清空，我们重新开始吧～")
        return True  # 表示已处理指令

    @classmethod
    def process_cmd(cls, user_input, chat_client, wifi):
        """统一分发特殊指令"""
        user_input = user_input.lower()
        if user_input == "show":
            return cls.handle_show()
        elif user_input == "exit":
            return cls.handle_exit(chat_client, wifi)
        elif user_input == "clear":
            return cls.handle_clear(chat_client)
        else:
            return None  # 表示不是特殊指令，需继续后续逻辑