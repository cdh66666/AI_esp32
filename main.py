from src.llm import LLM
from src.tts import TTS
from src.asr import ASR

if __name__ == "__main__":
    llm = LLM()
    tts = TTS()
    asr = ASR()

    while True:
        # 录音并识别
        prompt = asr.recognize_from_mic()
        if prompt:
            print("AI答复：", end="", flush=True)
            # 获取AI回答文本
            response = llm.generate_response(prompt)
            # 换行，便于显示
            print()
            # 语音播报AI回答
            tts.text_to_speech(response)
        else:
            print("未识别到内容，请重试。")