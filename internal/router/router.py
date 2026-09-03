from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import (
    AppHandler,
    BuiltinToolHandler,
    ApiToolHandler
)


@inject
@dataclass
class Router:
    """路由"""
    app_handler: AppHandler  # 仅声明字段，自动生成构造器
    builtin_tool_handler: BuiltinToolHandler
    api_tool_handler: ApiToolHandler

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

        # 内置插件模块
        bp.add_url_rule("/builtin-tools", view_func=self.builtin_tool_handler.get_builtin_tools)
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/tools/<string:tool_name>",
            view_func=self.builtin_tool_handler.get_provider_tool,
        )
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/icon",
            view_func=self.builtin_tool_handler.get_provider_icon,
        )
        bp.add_url_rule(
            "/builtin-tools/categories",
            view_func=self.builtin_tool_handler.get_categories,
        )

        # 4.自定义API插件模块
        # bp.add_url_rule(
        #     "/api-tools",
        #     view_func=self.api_tool_handler.get_api_tool_providers_with_page,
        # )
        bp.add_url_rule(
            "/api-tools/validate-openapi-schema",
            methods=["POST", "OPTIONS"],
            view_func=self.api_tool_handler.validate_openapi_schema,
        )
        bp.add_url_rule(
            "/api-tools",
            methods=["POST"],
            view_func=self.api_tool_handler.create_api_tool_provider,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            view_func=self.api_tool_handler.get_api_tool_provider,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            methods=["POST"],
            view_func=self.api_tool_handler.update_api_tool_provider,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>/tools/<string:tool_name>",
            view_func=self.api_tool_handler.get_api_tool,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>/delete",
            methods=["POST"],
            view_func=self.api_tool_handler.delete_api_tool_provider,
        )
        # 3 在应用上注册蓝图
        app.register_blueprint(bp)
