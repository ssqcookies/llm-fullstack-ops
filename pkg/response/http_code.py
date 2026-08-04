"""
@Time       :2026/8/2 17:06
@Author     :240227206@qq.com
@File       :http_code.py
"""
from enum import Enum


class ResponseCode(str, Enum):
    """HTTP基础业务状态码"""
    # 成功
    SUCCESS = "success"
    # 通用失败
    FAIL = "fail"
    # 404资源不存在
    NOT_FOUND = "not_found"
    # 未登录/未授权
    UNAUTHORIZED = "unauthorized"
    # 权限不足
    FORBIDDEN = "forbidden"
    # 参数校验错误（WTForms表单校验失败统一走这个）
    VALIDATE_ERROR = "validate_error"
