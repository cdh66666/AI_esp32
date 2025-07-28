#deepseek apikey: sk-b6e35f5ddcd54552bbe2c6996ae566a
from openai import OpenAI


 
class LLM:
    def __init__(self):
        """
        LLM初始化，配置参数内置
        """
        self.model_name = "deepseek-chat"
        self.api_key = "sk-3a6e6937b7cd4530914c5affe7e7abff"
        self.url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=self.api_key, base_url=self.url)

    def ask_once(self):
        """
        单轮问答，用户输入问题，模型流式输出答案
        """
        prompt = input("\n请输入你的问题：")
        if not prompt.strip():
            print("未输入问题，已退出。"); return
        print("A: ", end="", flush=True)
        self.generate_response(prompt)

    def ask_loop(self):
        """
        多轮交互问答，用户输入问题，模型流式输出答案，输入空行退出
        """
        print("\n欢迎使用大模型流式问答，输入你的问题（直接回车退出）：")
        idx = 1
        while True:
            prompt = input(f"\nQ{idx}: ")
            if not prompt.strip():
                print("已退出。"); break
            print(f"A{idx}: ", end="", flush=True)
            self.generate_response(prompt)
            idx += 1

    def generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=True
        )
        content = ""
        print("", end="", flush=True)
        for chunk in response:
            delta = getattr(chunk.choices[0].delta, "content", None)
            if delta:
                print(delta, end="", flush=True)
                content += delta
        print()  # 换行
        return content
    


 

if __name__ == "__main__":
    llm = LLM()
    print("\n【单轮问答测试】")
    llm.ask_once()
    print("\n【多轮问答测试】")
    llm.ask_loop()
    