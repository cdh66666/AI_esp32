import edge_tts
from playsound import playsound
from  asyncio import run as asyncio_run
import  os
import uuid


class TTS:
    def __init__(self, voice="zh-CN-XiaoxiaoNeural"):
        """
        TTS初始化，支持自定义语音角色
        """
        self.voice = voice

    async def text_to_speech_async(self, text, filename="output.mp3"):
        """
        异步文本转语音，保存为mp3
        :param text: str, 要转换的文本
        :param filename: str, 输出文件名
        """
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(filename)

    def text_to_speech(self, text, play=True):
        """
        同步文本转语音，便于主程序直接调用
        :param text: str, 要转换的文本
        :param play: bool, 是否自动播放
        """
        filename = f"output_{uuid.uuid4()}.mp3"
        asyncio_run(self.text_to_speech_async(text, filename))
        if play:
            playsound(filename)
            os.remove(filename)
 
 
 
if __name__ == "__main__":
    tts = TTS()
    text = input("请输入要转换的文本：")
    tts.text_to_speech(text)