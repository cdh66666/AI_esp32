


# 🚀 基于 ESP32 的全栈智能设备开发

---


## 📚 目录

- [🚀 基于 ESP32 的全栈智能设备开发](#-基于-esp32-的全栈智能设备开发)
  - [📚 目录](#-目录)
  - [💡 学习与示例代码](#-学习与示例代码)
  - [🛠️ 开发环境准备](#️-开发环境准备)
  - [⚙️ 环境配置流程](#️-环境配置流程)
  - [📖 常用命令与说明](#-常用命令与说明)
---

## 💡 学习与示例代码

本项目的 `tutorials` 文件夹用于存放各类课程学习代码与实用示例，便于查阅和复用。

| 文件名 | 内容简介 | 使用示例 |
| ------ | -------- | -------- |
| llm.py | 支持单轮和多轮交互的AI对话代码，演示如何用OpenAI/DeepSeek API实现流式问答 | `python tutorials/llm.py` |
| tts.py | 文本转语音（TTS）示例，支持自定义语音角色，合成mp3并自动播放 | `python tutorials/tts.py` |
| main.py | 一体化AI问答+语音播报示例，输入问题后自动AI回复并语音朗读 | `python main.py` |

---

## 🛠️ 开发环境准备

1. [Miniconda（推荐国内镜像）](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/)
2. [Visual Studio Code](https://code.visualstudio.com/)
3. [ESP-IDF 插件安装教程](https://blog.csdn.net/qq_57139623/article/details/147322963)

---

## ⚙️ 环境配置流程

```bash
# 1. 创建虚拟环境
conda create -n ai_esp32 python=3.11 -y
# 2. 激活虚拟环境
conda activate ai_esp32
# 3. 安装 openai 库（如需对接大模型 API）
pip install openai
# 4. 安装 edge_tts 库（文本转语音）
pip install edge_tts
```

---

## 📖 常用命令与说明

- 进入项目目录后，按需执行上述命令。
- 推荐使用国内镜像源加速依赖下载。
- 其他 ESP32 相关开发环境搭建请参考官方文档或插件教程。

 


