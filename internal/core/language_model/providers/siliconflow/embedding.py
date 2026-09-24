"""
@Time       :2026/9/25
@Author     :240227206@qq.com
@File       :embedding.py
"""
import os

from langchain_openai import OpenAIEmbeddings

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Embedding(OpenAIEmbeddings, BaseLanguageModel):
    """硅基流动向量嵌入模型"""

    def __init__(self, **kwargs):
        kwargs.setdefault("openai_api_base", "https://api.siliconflow.cn/v1")
        kwargs.setdefault("openai_api_key", os.getenv("SILICONFLOW_API_KEY"))
        super().__init__(**kwargs)
