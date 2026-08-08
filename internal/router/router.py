from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler


@inject
@dataclass
class Router:
    """路由"""
    app_handler: AppHandler  # 仅声明字段，自动生成构造器
    # @dataclass Python3.7+ 内置 数据类装饰器，简化类样板代码：
    # 自动根据类属性 app_handler: AppHandler 生成 __init__ 构造方法
    # 自动生成 __repr__、__eq__ 等魔术方法
    # def __init__(self, app_handler: AppHandler):
    #     self.app_handler = app_handler
    """路由注册"""

    def register_router(self, app: Flask):
        # 1 创建蓝图
        bp = Blueprint("llmops", __name__, url_prefix="")
        # 2 将url与对应的控制器方法做绑定
        # app.handle = AppHandler() ----使用inject消除硬编码实例化

        bp.add_url_rule("/ping", view_func=self.app_handler.ping, methods=["GET"])
        # URL路径 绑定到 Handler处理函数
        bp.add_url_rule("/apps/<uuid:app_id>/completion", view_func=self.app_handler.completion,
                        methods=["POST"], )
        # bp.add_url_rule("/api/chat", view_func=self.app_handler.completion, methods=["POST"])
        bp.add_url_rule("/app", view_func=self.app_handler.create_app, methods=["POST"])
        bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.get_app, methods=["GET"])
        bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.update_app, methods=["POST"])
        bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.delete_app, methods=["DELETE"])
        # 3 在应用上注册蓝图
        app.register_blueprint(bp)
