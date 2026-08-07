"""
@Time       :2026/7/30 11:05
@Author     :240227206@qq.com
@File       :app_handler.py
"""
import os
import uuid
from dataclasses import dataclass

from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from internal.exception import ValidationException, FailException
from internal.schema.app_schema import KimiForm
from internal.service import AppService
from pkg.response import success_resp, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    def create_app(self):
        """"调用服务创建新的app记录"""
        app = self.app_service.create_app()
        return success_message(f"应用已经成功创建，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名字是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改，名字是{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为{app.id}")

    def ping(self):
        raise FailException("数据未找到")
        # return "pong"

    def completion(self, app_id: uuid.UUID):
        """聊天接口"""
        # 1 提取从接口中获取的输入，post
        # query = request.json.get("query")
        req = KimiForm()
        if not req.validate():
            raise ValidationException(req.errors)
        # 校验通过，用 .data 拿真实字符串
        # query_content = req.query.data
        #
        # # 2 构建openai客户端，并发起请求
        # kimi_client = OpenAI(
        #     api_key=os.getenv("KIMI_API_KEY"),
        #     base_url=os.getenv("KIMI_BASE_URL")
        # )
        #
        # resp = kimi_client.chat.completions.create(
        #     model="kimi-k2.7-code",
        #     messages=[
        #         {"role": "user", "content": query_content}
        #     ]
        # )
        # ai_answer = resp.choices[0].message.content
        #
        # # 3. 包装JSON返回给前端
        # return success_resp({"content": ai_answer})
        query_content = req.query.data

        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL"),
            model="kimi-k2.7-code"
        )
        parser = StrOutputParser()

        chain = prompt | llm | parser
        content = chain.invoke({"query": query_content})

        return success_resp({"content": content})
