"""
消息推送模块

支持飞书、钉钉、企业微信、Telegram等推送渠道
"""

from .base import BaseNotifier
from .feishu import FeishuNotifier
from .dingtalk import DingTalkNotifier
from .wework import WeWorkNotifier
from .telegram import TelegramNotifier

__all__ = [
    "BaseNotifier",
    "FeishuNotifier",
    "DingTalkNotifier",
    "WeWorkNotifier",
    "TelegramNotifier",
]
