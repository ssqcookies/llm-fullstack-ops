"""
@Time       :2026/8/13 23:56
@Author     :240227206@qq.com
@File       :category_entity.py
"""
from pydantic import BaseModel, field_validator

from internal.exception import FailException


class CategoryEntity(BaseModel):
    """分类实体定义「工具分类」的数据结构"""
    category: str  # 分类唯一标识
    name: str  # 分类名称
    icon: str  # 分类图标名称

    @field_validator("icon")
    def check_icon_extension(cls, value: str):
        """校验icon的扩展名是不是.svg，如果不是则抛出错误"""
        if not value.endswith(".svg"):
            raise FailException("该分类的icon图标并不是.svg格式")
        return value
