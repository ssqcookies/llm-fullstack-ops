"""
@Time       :2026/9/18 16:17
@Author     :240227206@qq.com
@File       :chat.py
"""
import os

from langchain_openai import ChatOpenAI

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """硅基流动聊天模型"""

    def __init__(self, **kwargs):
        kwargs.setdefault("openai_api_base", "https://api.siliconflow.cn/v1")
        kwargs.setdefault("openai_api_key", os.getenv("SILICONFLOW_API_KEY"))
        super().__init__(**kwargs)

    def get_num_tokens_from_messages(self, messages) -> int:
        """重写 token 计数，用 cl100k_base 估算"""
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        total = 0
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                total += len(encoding.encode(msg.content))
        return total
