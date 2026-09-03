"""
@Time       :2026/7/30 11:05
@Author     :240227206@qq.com
@File       :app_handler.py
"""
import os
import uuid
from dataclasses import dataclass
from operator import itemgetter
from typing import Dict, Any

from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.memory import BaseMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI

from internal.exception import ValidationException
from internal.schema.app_schema import KimiForm
from internal.service import AppService
from pkg.response import success_resp, success_message

# 会话内存映射池【学习使用，生产环境替换为Redis持久映射】
SESSION_MEM_MAP: Dict[str, BaseMemory] = {}


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
        # google_serper = self.provider_factory.get_tool("google", "google_serper")()
        # # raise FailException("数据未找到")
        return "pong"

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """加载记忆变量信息"""
        # 从config中获取configurable
        configurable = config.get("configurable", {})
        # configurable_memory = configurable.get("memory", None)
        session_id = configurable.get("session_id", None)
        configurable_memory = SESSION_MEM_MAP.get(session_id)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        """存储对应的上下文信息到记忆实体中"""
        configurable = config.get("configurable", {})
        session_id = configurable.get("session_id", None)
        configurable_memory = SESSION_MEM_MAP.get(session_id)
        # configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

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

        # 生成会话标识，正式业务建议前端传入session_id区分聊天窗口

        # 创建prompt与记忆
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个强大的聊天机器人，能根据用户提问回复对应的问题"),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])
        # ==========改动重点==========
        # 从请求体获取前端传来的session_id
        session_id = app_id

        # 不存在则新建
        if not session_id:
            session_id = str(uuid.uuid4())

        # 去全局映射池查找memory
        memory = SESSION_MEM_MAP.get(session_id)
        # 找不到就创建新记忆实例
        if memory is None:
            memory = ConversationBufferWindowMemory(
                k=3,
                input_key="query",
                output_key="output",
                return_messages=True,
                chat_memory=FileChatMessageHistory(f"./storage/memory/{session_id}.txt"),
            )
            SESSION_MEM_MAP[session_id] = memory
        # ==========================
        # memory = ConversationBufferWindowMemory(
        #     k=3,
        #     input_key="query",
        #     output_key="output",
        #     return_messages=True,
        #     chat_memory=FileChatMessageHistory(f"./storage/memory/{session_id}.txt"),
        # )
        # # 将memory存入全局会话映射
        # SESSION_MEM_MAP[session_id] = memory

        llm = ChatOpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL"),
            model="kimi-k2.6",
            temperature=1
        )

        # chain = RunnablePassthrough.assign(
        #     history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        # ) | prompt | llm | StrOutputParser()
        chain = (RunnablePassthrough.assign(
            history=RunnableLambda(self._load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()).with_listeners(on_end=self.save_context)

        # 调用链生成内容
        chain_input = {"query": query_content}
        # content = chain.invoke(chain_input)
        # ❌ 0.2.x 禁止：往configurable传入对象实例，configurable 只允许存放可序列化基础类型（str /int/float /bool）
        # 旧版 langchain - core：✅ 允许 configurable 存放任意 Python 对象（Memory 实例、类实例）
        # content = chain.invoke(chain_input, config={"configurable": {"memory": memory}})
        # ✅ 仅传递字符串session_id，不再传递对象，规避类型校验报错
        # 构造配置
        run_config: RunnableConfig = {
            "configurable": {"session_id": session_id}
        }
        content = chain.invoke(chain_input, config=run_config)

        # memory.save_context(chain_input, {"output": content})

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
