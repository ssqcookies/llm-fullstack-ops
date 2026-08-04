"""
@Time       :2026/8/2 17:08
@Author     :240227206@qq.com
@File       :response.py
"""
from dataclasses import field, dataclass, asdict
from typing import Any, Union

from flask import jsonify

from pkg.response.http_code import ResponseCode


@dataclass
class Response:
    """"基础HTTP接口响应格式"""
    code: ResponseCode = ResponseCode.SUCCESS
    message: str = ''
    # default_factory 每次实例化新建空 dict
    data: Any = field(default_factory=dict)


#  带业务数据返回（data 有内容）
# 函数：success_resp / fail_resp / validation_resp
# 使用场景：接口需要带回有效业务数据
# 查询列表、查询详情、AI 问答返回答案、分页列表、新增后返回 ID 等
# data 字段必须塞内容，前端要解析 data 里的对象 / 数组
def json(data: Union[Response, None] = None):
    """基础响应接口，内部自动将Response dataclass转为字典"""
    if isinstance(data, Response):
        data = asdict(data)
    return jsonify(data), 200


def success_resp(data: Any = None):
    """成功返回"""
    return json(Response(code=ResponseCode.SUCCESS, message="", data=data))


def fail_resp(data: Any = None):
    """失败返回"""
    return json(Response(code=ResponseCode.FAIL, message="", data=data))


def validation_resp(errors: dict = None):
    """数据验证错误响应"""
    first_key = next(iter(errors))
    if first_key is not None:
        msg = errors.get(first_key)[0]
    else:
        msg = ""
    return json(Response(code=ResponseCode.VALIDATE_ERROR, message=msg, data=errors))


# 只返回提示文案（data 强制空字典）
# 函数：success_message / fail_message / not_found_message 等
# 使用场景：只需要告知操作结果，没有任何数据要返回
# 纯操作类接口，不需要前端拿 data：
# 删除成功、修改成功、新增成功、账号不存在、权限不足、参数错误提示

def message(code: ResponseCode = None, msg: str = ""):
    """基础消息响应，固定返回消息提示，数据固定为空字典"""
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    """成功的消息响应"""
    return message(code=ResponseCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    """失败的消息响应"""
    return message(code=ResponseCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    """未找到消息响应"""
    return message(code=ResponseCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ""):
    """未授权消息响应"""
    return message(code=ResponseCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ""):
    """无权限消息响应"""
    return message(code=ResponseCode.FORBIDDEN, msg=msg)
