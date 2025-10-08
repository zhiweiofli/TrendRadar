"""
日志系统配置
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# 全局日志配置
_loggers = {}


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO",
    console_output: bool = True,
) -> logging.Logger:
    """配置日志系统

    Args:
        name: 日志器名称
        log_file: 日志文件路径，None 表示不写入文件
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: 是否输出到控制台

    Returns:
        配置好的 Logger 对象
    """
    # 避免重复创建
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """获取 Logger 实例

    如果 logger 不存在，会创建一个默认配置的 logger

    Args:
        name: 日志器名称
        level: 日志级别

    Returns:
        Logger 实例
    """
    if name not in _loggers:
        return setup_logger(name, level=level)
    return _loggers[name]


def init_app_logger(
    log_dir: str = "logs", log_level: str = "INFO", enable_file_log: bool = True
) -> logging.Logger:
    """初始化应用级别的日志器

    Args:
        log_dir: 日志目录
        log_level: 日志级别
        enable_file_log: 是否启用文件日志

    Returns:
        应用日志器
    """
    log_file = f"{log_dir}/trendradar.log" if enable_file_log else None
    return setup_logger(
        "trendradar", log_file=log_file, level=log_level, console_output=True
    )
