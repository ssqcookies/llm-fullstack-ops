"""
@Time       :2026/9/25
@Author     :240227206@qq.com
@File       :tts_service.py
"""
from dataclasses import dataclass
from typing import Optional, Generator

from injector import inject

from internal.core.language_model.language_model_manager import LanguageModelManager
from internal.core.language_model.entities.model_entity import ModelType
from internal.exception import NotFoundException


@inject
@dataclass
class TtsService:
    """语音合成服务"""
    language_model_manager: LanguageModelManager

    def synthesize(
        self,
        text: str,
        provider_name: str = "siliconflow",
        model_name: str = "cosyvoice2-0.5b",
        voice: str = "anna",
        response_format: str = "mp3",
        speed: float = 1.0,
        sample_rate: Optional[int] = None,
    ) -> bytes:
        """
        文字转语音

        :param text: 待合成的文本
        :param provider_name: 提供商名称
        :param model_name: 模型名称（内部标识名）
        :param voice: 音色
        :param response_format: 输出格式 mp3/wav/opus/pcm
        :param speed: 语速 0.25~4.0
        :param sample_rate: 采样率
        :return: 音频二进制数据
        """
        # 1.获取提供商
        provider = self.language_model_manager.get_provider(provider_name)

        # 2.获取模型实体
        model_entity = provider.get_model_entity(model_name)
        if model_entity.model_type != ModelType.TEXT_TO_SPEECH:
            raise NotFoundException("该模型不是语音合成模型")

        # 3.获取语音合成模型类并实例化
        model_class = provider.get_model_class(ModelType.TEXT_TO_SPEECH)
        tts_model = model_class(
            model=model_entity.model_name,
            features=model_entity.features,
            metadata=model_entity.metadata,
        )

        # 4.调用语音合成
        return tts_model.synthesize(
            text=text,
            model_name=model_entity.model_name,
            voice=voice,
            response_format=response_format,
            speed=speed,
            sample_rate=sample_rate,
        )

    def synthesize_stream(
        self,
        text: str,
        provider_name: str = "siliconflow",
        model_name: str = "cosyvoice2-0.5b",
        voice: str = "anna",
        response_format: str = "mp3",
        speed: float = 1.0,
        sample_rate: Optional[int] = None,
    ) -> Generator[bytes, None, None]:
        """
        流式文字转语音

        :return: 音频二进制块迭代器
        """
        provider = self.language_model_manager.get_provider(provider_name)
        model_entity = provider.get_model_entity(model_name)
        if model_entity.model_type != ModelType.TEXT_TO_SPEECH:
            raise NotFoundException("该模型不是语音合成模型")

        model_class = provider.get_model_class(ModelType.TEXT_TO_SPEECH)
        tts_model = model_class(
            model=model_entity.model_name,
            features=model_entity.features,
            metadata=model_entity.metadata,
        )

        return tts_model.synthesize_stream(
            text=text,
            model_name=model_entity.model_name,
            voice=voice,
            response_format=response_format,
            speed=speed,
            sample_rate=sample_rate,
        )
