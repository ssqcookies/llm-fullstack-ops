"""
@Time       :2026/7/30 11:05
@Author     :240227206@qq.com
@File       :app_handler.py
"""
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter

from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
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
        # 创建prompt与记忆
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的聊天机器人，能根据用户提问回复对应的问题"),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])
        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )

        llm = ChatOpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL"),
            model="kimi-k2.6",
            temperature=1
        )

        chain = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()

        # 调用链生成内容
        chain_input = {"query": query_content}
        content = chain.invoke(chain_input)
        memory.save_context(chain_input, {"output": content})

        # 无记忆单次调用
        # prompt = ChatPromptTemplate.from_template("{query}")
        # llm = ChatOpenAI(
        #     api_key=os.getenv("KIMI_API_KEY"),
        #     base_url=os.getenv("KIMI_BASE_URL"),
        #     model="kimi-k2.6",
        #     temperature=1
        # )
        # parser = StrOutputParser()
        #
        # chain = prompt | llm | parser
        # content = chain.invoke({"query": query_content})

        return success_resp({"content": content})
