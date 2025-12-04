"""
文件操作工具函数
"""

import re
from pathlib import Path
from typing import Optional

from .time_utils import format_date_folder


def ensure_directory_exists(directory: str) -> None:
    """确保目录存在，不存在则创建

    Args:
        directory: 目录路径
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_output_path(subfolder: str, filename: str) -> str:
    """获取输出文件路径

    Args:
        subfolder: 子文件夹名称（如 "html" 或 "txt"）
        filename: 文件名

    Returns:
        完整的输出路径
    """
    date_folder = format_date_folder()
    output_dir = Path("output") / date_folder / subfolder
    ensure_directory_exists(str(output_dir))
    return str(output_dir / filename)


def clean_title(title: str) -> str:
    """清理标题中的特殊字符

    Args:
        title: 原始标题

    Returns:
        清理后的标题
    """
    if not isinstance(title, str):
        title = str(title)

    # 替换换行符为空格
    cleaned_title = title.replace("\n", " ").replace("\r", " ")

    # 合并多个空格为一个
    cleaned_title = re.sub(r"\s+", " ", cleaned_title)

    # 去除首尾空格
    cleaned_title = cleaned_title.strip()

    return cleaned_title


def get_project_root() -> Path:
    """获取项目根目录

    Returns:
        项目根目录路径
    """
    return Path(__file__).parent.parent.parent


def get_config_path(filename: str = "config.yaml") -> Path:
    """获取配置文件路径

    Args:
        filename: 配置文件名

    Returns:
        配置文件完整路径
    """
    return get_project_root() / "config" / filename


def html_escape(text: str) -> str:
    """HTML转义

    Args:
        text: 需要转义的文本

    Returns:
        转义后的文本
    """
    if not isinstance(text, str):
        text = str(text)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
