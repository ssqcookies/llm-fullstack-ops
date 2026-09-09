"""
@Time       :2026/9/8 14:13
@Author     :240227206@qq.com
@File       :embeddings_service.py
"""
import os
from dataclasses import dataclass

import tiktoken
from injector import inject
from langchain.embeddings import CacheBackedEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from redis import Redis


@inject
@dataclass
class EmbeddingsService:
    """文本嵌入模型服务"""
    _store: RedisStore
    _embeddings: Embeddings
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self, redis: Redis):
        """构造函数，初始化文本嵌入模型客户端、存储器、缓存客户端"""
        # 1. Redis 向量存储
        self._store = RedisStore(client=redis)
        # 2. 本地 Embedding 模型
        # self._embeddings = HuggingFaceEmbeddings(
        #     model_name="Alibaba-NLP/gte-multilingual-base",  # 阿里通义多语言模型
        #     cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),  # 模型下载到本地这个目录
        #     model_kwargs={
        #         "trust_remote_code": True,  # 允许执行模型仓库里的自定义代码（gte 模型需要）
        #     }
        # )
        # 线上  Embedding 模型
        self._embeddings = OpenAIEmbeddings(
            model="BAAI/bge-m3",
            base_url=os.environ.get("SILICONFLOW_BASE_URL", ""),
            api_key=os.environ.get("SILICONFLOW_API_KEY", ""),
        )

        # 3. 带 Redis 缓存的 Embedding
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,  # 缓存存到 Redis
            namespace="embeddings",  # Redis key 前缀：embeddings:{hash}
        )

    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算传入文本的token数"""
        encoding = tiktoken.encoding_for_model("gpt-3.5")
        return len(encoding.encode(query))

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings
