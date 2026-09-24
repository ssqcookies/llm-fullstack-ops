"""
@Time       :2026/8/12 17:13
@Author     :240227206@qq.com
@File       :vector_database_service.py
"""

from dataclasses import dataclass
from typing import Any

from flask import Flask
from flask_weaviate import FlaskWeaviate
from injector import inject
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate.collections import Collection

from .embeddings_service import EmbeddingsService

# 向量数据库的集合名字
COLLECTION_NAME = "Dataset"


@inject
@dataclass
class VectorDatabaseService:
    """向量数据库服务"""
    weaviate: FlaskWeaviate
    embeddings_service: EmbeddingsService

    async def _get_client(self, flask_app: Flask):
        with flask_app.app_context():
            return self.weaviate.client

    @property
    def vector_store(self) -> WeaviateVectorStore:
        return WeaviateVectorStore(
            client=self.weaviate.client,
            index_name=COLLECTION_NAME,
            text_key="text",
            embedding=self.embeddings_service.cache_backed_embeddings,
        )

    async def add_documents(self, documents: list[Document], **kwargs: Any):
        """往向量数据库中新增文档，将vector_store使用async进行二次封装，避免在gevent中实现事件循环错误"""
        self.vector_store.add_documents(documents, **kwargs)

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器"""
        return self.vector_store.as_retriever()

    @property
    def collection(self) -> Collection:
        return self.weaviate.client.collections.get(COLLECTION_NAME)

# import os
#
# import weaviate
# from injector import inject
# from langchain_core.documents import Document
# from langchain_core.vectorstores import VectorStoreRetriever
# from langchain_weaviate import WeaviateVectorStore
# from weaviate import WeaviateClient
# from weaviate.collections import Collection
#
# from .embeddings_service import EmbeddingsService
#
# # 向量数据库的集合名字
# COLLECTION_NAME = "Dataset"
#
#
# @inject
# class VectorDatabaseService:
#     """向量数据库服务"""
#     client: WeaviateClient
#     vector_store: WeaviateVectorStore
#     embeddings_service: EmbeddingsService
#
#     def __init__(self, embeddings_services: EmbeddingsService):
#         """构造函数，完成向量数据库服务的客户端+LangChain向量数据库实例的创建"""
#         # 1.赋值embeddings_service
#         self.embeddings_service = embeddings_services
#
#         # 2.创建/连接weaviate向量数据库
#         self.client = weaviate.connect_to_local(
#             host=os.getenv("WEAVIATE_HTTP_HOST", "127.0.0.1"),
#             port=int(os.getenv("WEAVIATE_HTTP_PORT", "8080")),
#             grpc_port=int(os.getenv("WEAVIATE_GRPC_PORT", "50051")),
#         )
#
#         # 3.创建LangChain向量数据库
#         self.vector_store = WeaviateVectorStore(
#             client=self.client,
#             index_name=COLLECTION_NAME,
#             text_key="text",
#             embedding=self.embeddings_service.cache_backed_embeddings
#             # embedding=self.embeddings_service.embeddings,
#         )
#
#     def get_retriever(self) -> VectorStoreRetriever:
#         """获取检索器"""
#         return self.vector_store.as_retriever()
#
#     @classmethod
#     def combine_documents(cls, documents: list[Document]) -> str:
#         """将对应的文档列表使用换行符进行合并"""
#         return "\n\n".join([document.page_content for document in documents])
#
#     @property
#     def collection(self) -> Collection:
#         return self.client.collections.get(COLLECTION_NAME)
#
#     def close(self):
#         """关闭 Weaviate 连接"""
#         if self.client.is_connected():
#             self.client.close()
