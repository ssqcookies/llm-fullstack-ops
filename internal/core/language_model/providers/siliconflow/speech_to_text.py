"""
@Time       :2026/9/25
@Author     :240227206@qq.com
@File       :speech_to_text.py
"""
import os
from typing import BinaryIO

import requests

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Speech_to_text(BaseLanguageModel):
    """硅基流动语音识别模型"""

    api_base: str = "https://api.siliconflow.cn/v1"
    api_key: str = ""

    def __init__(self, model: str = "FunAudioLLM/SenseVoiceSmall", **kwargs):
        kwargs.setdefault("openai_api_base", "https://api.siliconflow.cn/v1")
        kwargs.setdefault("openai_api_key", os.getenv("SILICONFLOW_API_KEY"))
        # 父类需要 model 字段
        kwargs["model"] = model
        super().__init__(**kwargs)
        self.api_base = kwargs.get("openai_api_base", "https://api.siliconflow.cn/v1")
        self.api_key = kwargs.get("openai_api_key", os.getenv("SILICONFLOW_API_KEY", ""))

    def transcribe(self, audio_file: BinaryIO, model_name: str = None) -> str:
        """
        语音转文字

        :param audio_file: 音频文件对象（二进制）
        :param model_name: 模型名称，不传则用初始化的 model
        :return: 识别后的文本
        """
        url = f"{self.api_base}/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        files = {
            "file": audio_file,
        }
        data = {
            "model": model_name or self.model,
        }
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")

    def _llm_type(self) -> str:
        return "siliconflow-speech-to-text"
