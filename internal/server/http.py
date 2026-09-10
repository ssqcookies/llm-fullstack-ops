"""
@Time       :2026/7/31 15:42
@Author     :240227206@qq.com
@File       :http.py
"""

import os

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate

from config.config import Config
from internal.exception import CustomException
from internal.extension import logging_extension, redis_extension, celery_extension
from internal.middleware import Middleware
from internal.router import Router
from pkg.response import json, Response, ResponseCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """http服务引擎"""

    def __init__(
            self,
            *args,
            conf: Config,
            db: SQLAlchemy,
            migrate: Migrate,
            login_manager: LoginManager,
            # 中间件
            middleware: Middleware,
            router: Router,
            **kwargs
    ):
        # 调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 注册绑定异常错误处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 添加校验规则
        self.config.from_object(conf)

        # 初始化flask扩展
        db.init_app(self)
        migrate.init_app(self, db=db, directory="internal/migration")

        redis_extension.init_app(self)
        celery_extension.init_app(self)
        logging_extension.init_app(self)

        # # 解决前后端跨域问题
        CORS(self, resources={
            r"/*": {
                "origins": "*",
                "supports_credentials": True,
                # "methods": ["GET", "POST"],
                # "allow_headers": ["Content-Type"],
            }
        })
        # CORS(self,
        #      supports_credentials=True,
        #      resources={
        #          r"/*": {
        #              "origins": ["http://localhost:5173"],
        #              "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        #              "allow_headers": ["Content-Type"]
        #          }
        #      })
        #
        # with self.app_context():
        #     _ = App()
        # db.create_all()
        # db.create_all() 会绕过迁移系统，直接在数据库里建表，只能建新表，不能改已有表的结构
        # 改用 flask db migrate + flask db upgrade 建表，因为后面要频繁改表结构（加字段、改类型），create_all 做不到，Flask-Migrate 就是为了解决这个问题。

        # 6.注册应用中间件
        login_manager.request_loader(middleware.request_loader)

        # 注册应用路由
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        # 1.异常信息是不是我们的自定义异常，如果是可以提取message和code等信息
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {},
            ))
        # 2.如果不是我们的自定义异常，则有可能是程序、数据库抛出的异常，也可以提取信息，设置为FAIL状态码
        if self.debug or os.getenv("FLASK_ENV") == "development":
            raise error
        else:
            return json(Response(
                code=ResponseCode.FAIL,
                message=str(error),
                data={},
            ))
