"""
@Time       :2026/9/25 00:51
@Author     :240227206@qq.com
@File       :audio_service.py
"""

import base64
import json
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Generator, Union
from uuid import UUID

from injector import inject
from werkzeug.datastructures import FileStorage

from internal.exception import NotFoundException, FailException
from internal.model import Account, Message, App, AppConfig, AppConfigVersion
from pkg.sqlalchemy import SQLAlchemy
from .app_service import AppService
from .asr_service import AsrService
from .base_service import BaseService
from .tts_service import TtsService
from ..entity.app_entity import AppStatus
from ..entity.conversation_entity import InvokeFrom


@inject
@dataclass
class AudioService(BaseService):
    """语音服务，涵盖语音转文本、消息流式输出语音"""
    db: SQLAlchemy
    app_service: AppService
    asr_service: AsrService
    tts_service: TtsService

    def audio_to_text(
        self,
        audio: FileStorage,
        provider_name: str = "siliconflow",
        model_name: str = "sensevoice-small",
    ) -> str:
        """将传递的语音转换成文本"""
        # 1.提取音频文件，并将音频文件转换成BytesIO
        file_content = audio.stream.read()
        audio_file = BytesIO(file_content)
        audio_file.name = audio.filename or "recording.wav"

        # 2.调用ASR服务将音频转换成文字
        try:
            text = self.asr_service.transcribe(
                audio_file=audio_file,
                provider_name=provider_name,
                model_name=model_name,
            )
        except Exception as error:
            logging.error("语音转文字失败: %(error)s", {"error": error}, exc_info=True)
            raise FailException("语音转文字失败，请稍后重试")

        # 3.返回识别的文字内容
        return text

    def message_to_audio(
        self,
        message_id: UUID,
        account: Account,
        provider_name: str = "siliconflow",
        model_name: str = "cosyvoice2-0.5b",
    ) -> Generator:
        """将消息转换成流式事件输出语音"""
        # 1.根据传递的消息id获取消息并校验权限
        message = self.get(Message, message_id)
        if not message or message.is_deleted or message.answer.strip() == "" or message.created_by != account.id:
            raise NotFoundException("该消息不存在，请核实后重试")

        # 2.校验消息归属的会话状态是否正常
        conversation = message.conversation
        if conversation is None or conversation.is_deleted or conversation.created_by != account.id:
            raise NotFoundException("该消息会话不存在，请核实后重试")

        # 3.定义文本转语音启动配置、音色，默认为开启+anna音色
        enable = True
        voice = "anna"

        # 4.根据会话信息获取会话归属的应用
        if message.invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER]:
            app = self.get(App, conversation.app_id)
            if not app:
                raise NotFoundException("该消息会话归属应用不存在或校验失败，请核实后重试")
            if message.invoke_from == InvokeFrom.DEBUGGER is True and app.account_id != account.id:
                raise NotFoundException("该消息会话归属的应用不存在或校验失败，请核实后重试")
            if message.invoke_from == InvokeFrom.WEB_APP is False and app.status != AppStatus.PUBLISHED:
                raise NotFoundException("该消息会话归属的应用未发布，请核实后重试")

            app_config: Union[AppConfig, AppConfigVersion] = (
                app.draft_app_config
                if message.invoke_from == InvokeFrom.DEBUGGER
                else app.app_config
            )
            text_to_speech = app_config.text_to_speech
            enable = text_to_speech.get("enable", False)
            voice = text_to_speech.get("voice", "anna")
        elif message.invoke_from == InvokeFrom.SERVICE_API:
            raise NotFoundException("开放API消息不支持文本转语音服务")

        # 5.根据状态获取不同的配置并判断是否开启文字转语音
        if enable is False:
            raise FailException("该应用未开启文字转语音功能，请核实后重试")

        # 6.调用TTS服务将消息answer转换成流式事件输出语音
        try:
            audio_stream = self.tts_service.synthesize_stream(
                text=message.answer.strip(),
                provider_name=provider_name,
                model_name=model_name,
                voice=voice,
                response_format="mp3",
            )
        except Exception as error:
            logging.error("文字转语音失败: %(error)s", {"error": error}, exc_info=True)
            raise FailException("文字转语音失败，请稍后重试")

        # 7.封装流式事件输出语音数据
        def tts() -> Generator:
            """内部函数，从音频流中逐块读取并封装SSE事件"""
            common_data = {
                "conversation_id": str(conversation.id),
                "message_id": str(message.id),
                "audio": "",
            }
            for chunk in audio_stream:
                if not chunk:
                    continue
                data = {**common_data, "audio": base64.b64encode(chunk).decode("utf-8")}
                yield f"event: tts_message\ndata: {json.dumps(data)}\n\n"
            yield f"event: tts_end\ndata: {json.dumps(common_data)}\n\n"

        return tts()
