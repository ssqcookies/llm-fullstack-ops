"""
@Time       :2026/9/25 09:51
@Author     :240227206@qq.com
@File       :platform_entity.py
"""
from enum import Enum


class WechatConfigStatus(str, Enum):
    """微信配置状态"""
    CONFIGURED = "configured"  # 已配置
    UNCONFIGURED = "unconfigured"  # 未配置
