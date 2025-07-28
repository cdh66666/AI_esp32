from tutorials.llm import LLM
from tutorials.tts import TTS

if __name__ == "__main__":
    llm = LLM()
    tts = TTS()
    prompt = input("请输入你的问题：")
    print("AI答复：", end="", flush=True)
    # 获取AI回答文本
    response = llm.generate_response(prompt)
    # 换行，便于显示
    print()
    # 语音播报AI回答
    tts.text_to_speech(response)
