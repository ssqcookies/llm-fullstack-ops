"""
@Time       :2026/9/18 16:17
@Author     :240227206@qq.com
@File       :chat.py
"""
from langchain_community.chat_models.moonshot import MoonshotChat

from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(MoonshotChat, BaseLanguageModel):
    """硅基流动聊天模型"""
    pass
