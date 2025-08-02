import speech_recognition as sr
import yaml

class ASR:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        self.duration = config['record_duration']

    def recognize_from_mic(self, wavfile="mic_record.wav"):
        """
        用pyaudio录音保存为wav文件，再识别
        """
        import pyaudio
        import wave
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print(f"请开始说话（录音{self.duration}秒）...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * self.duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(wavfile, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("录音完成，正在识别...")
        with sr.AudioFile(wavfile) as source:
            audio = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            print("识别结果：", text)
            return text
        except Exception as e:
            print("识别失败：", e)
            return None


if __name__ == "__main__":
    asr = ASR()
    asr.recognize_from_mic()