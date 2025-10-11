import urequests
import ujson
import _thread
import time
 
class DeepSeekClient:
    def __init__(self, api_key, api_url="https://api.deepseek.com/v1/chat/completions", 
                 summary_file="chat_summary.txt",system_prompt="你是一个女助手", max_summary_chars=6000):
        self.api_key = api_key
        self.api_url = api_url
        self.summary_file = summary_file
        self.max_summary_chars = max_summary_chars  # 3000字≈6000字符
        self.system_prompt = system_prompt
        self.history = self._load_summary_from_local()
        self.chat_round = self._calc_current_round()
        self.is_summarizing = False
        self.summary_completed = False  # 新增：标记浓缩是否完成

    def _load_summary_from_local(self):
        try:
            with open(self.summary_file, "r", encoding="utf-8") as f:
                summary = f.read().strip()
            if len(summary) > self.max_summary_chars:
                summary = summary[:self.max_summary_chars] + "..."
                print(f"[提示] 本地摘要过长，已截断至{self.max_summary_chars}字符～")
            
            if summary:
                print(f"[提示] 已加载本地历史摘要（{len(summary)}字符）～")
                return [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "assistant", "content": f"【历史对话摘要】：{summary}"}
                ]
            else:
                print(f"[提示] 本地摘要文件为空，将重新开始～")
        except OSError:
            print(f"[提示] 未找到本地摘要文件，将重新开始～")
        except Exception as e:
            print(f"[警告] 读取摘要失败：{str(e)[:20]}，将重新开始～")
        return [{"role": "system", "content": self.system_prompt}]

    def _calc_current_round(self):
        user_assistant_msgs = [msg for msg in self.history if msg["role"] in ["user", "assistant"]]
        return len(user_assistant_msgs) // 2

    def _save_summary_to_local(self, summary):
        try:
            if len(summary) > self.max_summary_chars:
                summary = summary[:self.max_summary_chars] + "..."
                print(f"[提示] 摘要过长，已截断至{self.max_summary_chars}字符～")
            
            with open(self.summary_file, "w", encoding="utf-8") as f:
                f.write(summary.strip())
            print(f"\n[提示] 历史对话摘要已保存（{len(summary)}字符）～")
            return True
        except Exception as e:
            print(f"[错误] 保存摘要失败：{str(e)[:20]}")
            return False

    def _do_summary(self, history_snapshot, wifi_manager, is_exit=False):
        """新增is_exit参数，标记是否为退出时的浓缩"""
        try:
            print(f"\n[{'退出前' if is_exit else '后台'}] 开始提炼对话重点（最长{self.max_summary_chars//2}字）...")
            
            summary_prompt = f"""请你作为对话助手，将以下历史对话提炼为精简摘要。要求：
1. 保留主人（用户）的核心需求、喜好、关键信息；
2. 保留你（助手）的关键回应；
3. 去除重复、冗余内容，语言自然流畅；
4. 严格控制在{self.max_summary_chars//2}字以内；
5. 用自然的中文表述，不要使用Markdown格式。

历史对话：
"""
            history_text = ""
            for msg in history_snapshot:
                role = "主人" if msg["role"] == "user" else "助手"
                history_text += f"{role}：{msg['content']}\n"
            
            request_data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是对话摘要助手，仅输出符合要求的精简摘要，不额外回复"},
                    {"role": "user", "content": summary_prompt + history_text}
                ],
                "max_tokens": self.max_summary_chars//2,
                "temperature": 0.3
            }

            json_str = ujson.dumps(request_data)
            json_bytes = json_str.encode('utf-8')
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Length": str(len(json_bytes))
            }

            response = urequests.post(self.api_url, headers=headers, data=json_bytes, stream=False)
            if response.status_code != 200:
                raise Exception(f"API错误[{response.status_code}]")

            json_data = ujson.loads(response.text)
            summary = json_data["choices"][0]["message"]["content"].strip()
            response.close()

            if summary:
                self._save_summary_to_local(summary)
                self.history = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "assistant", "content": f"【历史对话摘要】：{summary}"}
                ]
                self.chat_round = 0
                print(f"[{'退出前' if is_exit else '后台'}] 历史提炼完成，{('准备退出～' if is_exit else '可继续聊天～')}")
            else:
                print(f"[{'退出前' if is_exit else '后台'}] 未获取到有效摘要")

        except Exception as e:
            print(f"[{'退出前' if is_exit else '后台'}] 提炼失败：{str(e)[:20]}")
        finally:
            self.is_summarizing = False
            self.summary_completed = True  # 标记浓缩完成

    def _trigger_summary_background(self, wifi_manager, is_exit=False):
        if self.is_summarizing:
            print(f"[提示] 正在提炼历史，请稍候...")
            return
        
        history_snapshot = [msg.copy() for msg in self.history]
        self.is_summarizing = True
        self.summary_completed = False  # 重置完成标记
        
        _thread.start_new_thread(
            self._do_summary,
            (history_snapshot, wifi_manager, is_exit)
        )

    def trigger_summary_and_wait(self, wifi_manager):
        """同步触发浓缩并等待完成（供退出时使用）"""
        # 如果正在浓缩，直接等待
        if self.is_summarizing:
            print("[提示] 等待当前浓缩完成...")
        else:
            # 触发退出时的浓缩
            self._trigger_summary_background(wifi_manager, is_exit=True)
        
        # 等待浓缩完成（最多等待30秒，避免无限阻塞）
        timeout = 30
        interval = 0.5
        for _ in range(int(timeout / interval)):
            if self.summary_completed:
                return True
            time.sleep(interval)
        
        print(f"[警告] 浓缩超时（{timeout}秒），强制退出～")
        return False

    def clear_history(self):
        try:
            open(self.summary_file, "w").close()
            print(f"[提示] 本地摘要已清空～")
        except Exception as e:
            print(f"[警告] 清空本地摘要失败：{str(e)[:20]}")
        
        self.history = [{"role": "system", "content": self.system_prompt}]
        self.chat_round = 0
        print(f"[提示] 历史对话已重置，可重新开始聊天～")

    def chat_stream(self, prompt, wifi_manager):
        if not wifi_manager.is_connected():
            return False, "未连接WiFi，请先联网哦～"

        if self.chat_round >= 5 and not self.is_summarizing:
            self._trigger_summary_background(wifi_manager)
            print(f"[提示] 已累计5轮对话，正在后台提炼重点，不影响当前聊天～")

        self.history.append({"role": "user", "content": prompt})

        request_data = {
            "model": "deepseek-chat",
            "messages": self.history,
            "stream": True,
            "max_tokens": 1024,
            "temperature": 0.7
        }

        try:
            json_str = ujson.dumps(request_data)
            json_bytes = json_str.encode('utf-8')
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Length": str(len(json_bytes))
            }

            response = urequests.post(
                self.api_url, headers=headers, data=json_bytes, stream=True
            )

            if response.status_code != 200:
                error_msg = f"API错误[{response.status_code}]：{response.text[:50]}"
                response.close()
                self.history.pop()
                return False, f"抱歉呀主人，{error_msg}～"

            full_reply = ""
            print("Deepseek:", end="")

            while True:
                line = response.raw.readline()
                if not line:
                    break

                line_str = line.decode("utf-8").strip()
                if not line_str or line_str.startswith("data: [DONE]"):
                    continue

                if line_str.startswith("data: "):
                    try:
                        json_data = ujson.loads(line_str[len("data: "):])
                        delta = json_data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            print(content, end="")
                            full_reply += content

                        if json_data.get("choices", [{}])[0].get("finish_reason") == "stop":
                            break

                    except Exception as e:
                        print(f"\n解析小错误：{str(e)[:20]}", end="")
                        continue

            response.close()
            print()

            if full_reply:
                self.history.append({"role": "assistant", "content": full_reply})
                if not self.is_summarizing:
                    self.chat_round = self._calc_current_round()
                return True, full_reply
            else:
                self.history.pop()
                return False, "没获取到回复呢，主人可以再问一次哦～"

        except Exception as e:
            self.history.pop()
            return False, f"请求小问题：{str(e)[:20]}～"
    