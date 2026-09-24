"""
@Time       :2026/9/25
@Author     :240227206@qq.com
@File       :asr_service.py
"""
from dataclasses import dataclass
from typing import BinaryIO

from injector import inject

from internal.core.language_model.language_model_manager import LanguageModelManager
from internal.core.language_model.entities.model_entity import ModelType
from internal.exception import NotFoundException


@inject
@dataclass
class AsrService:
    """语音识别服务"""
    language_model_manager: LanguageModelManager

    def transcribe(
        self,
        audio_file: BinaryIO,
        provider_name: str = "siliconflow",
        model_name: str = "sensevoice-small",
    ) -> str:
        """
        语音转文字

        :param audio_file: 音频文件对象
        :param provider_name: 提供商名称
        :param model_name: 模型名称（内部标识名）
        :return: 识别后的文本
        """
        # 1.获取提供商
        provider = self.language_model_manager.get_provider(provider_name)

        # 2.获取模型实体
        model_entity = provider.get_model_entity(model_name)
        if model_entity.model_type != ModelType.SPEECH_TO_TEXT:
            raise NotFoundException("该模型不是语音识别模型")

        # 3.获取语音识别模型类并实例化
        model_class = provider.get_model_class(ModelType.SPEECH_TO_TEXT)
        asr_model = model_class(
            model=model_entity.model_name,
            features=model_entity.features,
            metadata=model_entity.metadata,
        )

        # 4.调用语音识别
        return asr_model.transcribe(audio_file, model_name=model_entity.model_name)
