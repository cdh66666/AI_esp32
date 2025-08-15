


# 🚀 基于 ESP32 的全栈智能设备开发

 
  
  
- [🚀 基于 ESP32 的全栈智能设备开发](#-基于-esp32-的全栈智能设备开发)
  - [💡 项目主要功能](#-项目主要功能)
  - [📁 项目文件简介](#-项目文件简介)
  - [🛠️ 开发环境准备](#️-开发环境准备)
  - [⚙️ 环境配置流程](#️-环境配置流程)
    



## 💡 项目主要功能

- LLM 大模型对话：支持多轮/单轮 AI 聊天
- TTS 文本转音频：文本转语音，支持多角色
- Opus 音频编解码：音频压缩与传输
- ASR 本地音频转文字：本地语音识别

 
## 📁 项目文件简介

| 文件/文件夹         | 说明                                   |
|---------------------|---------------------------------------|
| main.py             | 一体化 AI 问答+语音播报主程序           |
| llm.py              | LLM 大模型对话示例，支持流式问答        |
| tts.py              | 文本转语音（TTS）示例，支持多角色       |
| output.mp3          | 语音合成输出文件                       | 
| requirements.txt    | Python 库依赖列表                      | 
| config.yaml         | 项目参数配置文件                       | 


---


## 🛠️ 开发环境准备

1. [【Python环境搭建】Miniconda的安装及配置教程](https://blog.csdn.net/AlgoZZi/article/details/145074821?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522b8d7c9378b6fe8ef91ed19aca136a061%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=b8d7c9378b6fe8ef91ed19aca136a061&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-145074821-null-null.142^v102^pc_search_result_base7&utm_term=miniconda%E5%AE%89%E8%A3%85&spm=1018.2226.3001.4187)
2. [Visual Studio Code](https://code.visualstudio.com/)
3. [ESP-IDF 插件安装教程](https://blog.csdn.net/qq_57139623/article/details/147322963)

---


## ⚙️ 环境配置流程

```bash
# 1. 创建虚拟环境
conda create -n ai_esp32 python=3.11 -y
# 2. 激活虚拟环境
conda activate ai_esp32
# 3. 安装python库
pip install -r requirements.txt 
```
 
 


