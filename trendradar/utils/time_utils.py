"""
时间处理工具函数
"""

from datetime import datetime
from typing import Tuple

import pytz


def get_beijing_time() -> datetime:
    """获取北京时间

    Returns:
        北京时区的当前时间
    """
    return datetime.now(pytz.timezone("Asia/Shanghai"))


def format_date_folder() -> str:
    """格式化日期文件夹名称

    Returns:
        格式化的日期字符串，如：2025年10月08日
    """
    return get_beijing_time().strftime("%Y年%m月%d日")


def format_time_filename() -> str:
    """格式化时间文件名

    Returns:
        格式化的时间字符串，如：13时45分
    """
    return get_beijing_time().strftime("%H时%M分")


def format_time_display(first_time: str, last_time: str) -> str:
    """格式化时间区间显示

    Args:
        first_time: 开始时间
        last_time: 结束时间

    Returns:
        格式化的时间区间字符串
    """
    if first_time == last_time:
        return first_time
    return f"{first_time} - {last_time}"


def is_in_time_range(start_time: str, end_time: str) -> bool:
    """检查当前时间是否在指定时间范围内

    Args:
        start_time: 开始时间，格式如 "09:00"
        end_time: 结束时间，格式如 "11:00"

    Returns:
        是否在时间范围内
    """
    now = get_beijing_time()
    current_time = now.strftime("%H:%M")
    return start_time <= current_time <= end_time
