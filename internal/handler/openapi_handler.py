"""
@Time       :2026/9/15 10:03
@Author     :240227206@qq.com
@File       :openapi_handler.py
"""

from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject

from internal.schema.openapi_schema import OpenAPIChatReq
from internal.service import OpenAPIService
from pkg.response import validation_resp, compact_generate_response


@inject
@dataclass
class OpenAPIHandler:
    """开放API处理器"""
    openapi_service: OpenAPIService

    @login_required
    def chat(self):
        """开放Chat对话接口"""
        # 1.提取请求并校验数据
        req = OpenAPIChatReq()
        if not req.validate():
            return validation_resp(req.errors)

        # 2.调用服务创建会话
        resp = self.openapi_service.chat(req, current_user)

        return compact_generate_response(resp)
