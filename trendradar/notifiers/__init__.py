"""
消息推送模块

支持飞书、钉钉、企业微信、Telegram等推送渠道
"""

from .base import BaseNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier
from .telegram import TelegramNotifier
from .wework import WeWorkNotifier

__all__ = [
    "BaseNotifier",
    "FeishuNotifier",
    "DingTalkNotifier",
    "WeWorkNotifier",
    "TelegramNotifier",
]
