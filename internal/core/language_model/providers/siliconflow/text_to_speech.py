"""
@Time       :2026/9/25
@Author     :240227206@qq.com
@File       :text_to_speech.py
"""
import os
from typing import Optional

import requests

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Text_to_speech(BaseLanguageModel):
    """硅基流动语音合成模型"""

    api_base: str = "https://api.siliconflow.cn/v1"
    api_key: str = ""

    def __init__(self, model: str = "FunAudioLLM/CosyVoice2-0.5B", **kwargs):
        kwargs.setdefault("openai_api_base", "https://api.siliconflow.cn/v1")
        kwargs.setdefault("openai_api_key", os.getenv("SILICONFLOW_API_KEY"))
        kwargs["model"] = model
        super().__init__(**kwargs)
        self.api_base = kwargs.get("openai_api_base", "https://api.siliconflow.cn/v1")
        self.api_key = kwargs.get("openai_api_key", os.getenv("SILICONFLOW_API_KEY", ""))

    def synthesize(
        self,
        text: str,
        model_name: str = None,
        voice: str = "anna",
        response_format: str = "mp3",
        speed: float = 1.0,
        sample_rate: Optional[int] = None,
        stream: bool = False,
    ) -> bytes:
        """
        文字转语音

        :param text: 待合成的文本
        :param model_name: 模型名称，不传则用初始化的 model
        :param voice: 音色名称（如 anna, alex 等）
        :param response_format: 输出格式 mp3/wav/opus/pcm
        :param speed: 语速 0.25~4.0
        :param sample_rate: 采样率
        :param stream: 是否流式输出
        :return: 音频二进制数据
        """
        url = f"{self.api_base}/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        full_model = model_name or self.model
        payload = {
            "model": full_model,
            "input": text,
            "voice": f"{full_model}:{voice}",
            "response_format": response_format,
            "speed": speed,
            "stream": stream,
        }
        if sample_rate is not None:
            payload["sample_rate"] = sample_rate

        response = requests.post(url, headers=headers, json=payload, stream=stream)
        response.raise_for_status()
        return response.content

    def synthesize_stream(
        self,
        text: str,
        model_name: str = None,
        voice: str = "anna",
        response_format: str = "mp3",
        speed: float = 1.0,
        sample_rate: Optional[int] = None,
    ):
        """
        流式文字转语音，返回音频流迭代器

        :return: 音频二进制块迭代器
        """
        url = f"{self.api_base}/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        full_model = model_name or self.model
        payload = {
            "model": full_model,
            "input": text,
            "voice": f"{full_model}:{voice}",
            "response_format": response_format,
            "speed": speed,
            "stream": True,
        }
        if sample_rate is not None:
            payload["sample_rate"] = sample_rate

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        return response.iter_content(chunk_size=4096)

    def _llm_type(self) -> str:
        return "siliconflow-text-to-speech"
