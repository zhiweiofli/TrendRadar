"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml


def load_config(config_path: Optional[str] = None) -> Dict:
    """加载配置文件

    Args:
        config_path: 配置文件路径，默认从环境变量或使用默认路径

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: 配置文件格式错误
    """
    if config_path is None:
        config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # 构建配置字典
    config = _build_config_dict(config_data)

    return config


def _build_config_dict(config_data: Dict) -> Dict:
    """构建配置字典

    Args:
        config_data: 从 YAML 加载的原始配置数据

    Returns:
        处理后的配置字典
    """
    config = {
        # 应用配置
        "VERSION_CHECK_URL": config_data["app"]["version_check_url"],
        "SHOW_VERSION_UPDATE": config_data["app"]["show_version_update"],
        "TEST_MODE": os.environ.get("TEST_MODE", "").lower() == "true"
        or config_data["app"].get("test_mode", False),
        # 爬虫配置
        "REQUEST_INTERVAL": config_data["crawler"]["request_interval"],
        "USE_PROXY": config_data["crawler"]["use_proxy"],
        "DEFAULT_PROXY": config_data["crawler"]["default_proxy"],
        "ENABLE_CRAWLER": config_data["crawler"]["enable_crawler"],
        "ENABLE_ASYNC": config_data["crawler"].get(
            "enable_async", True
        ),  # 新增异步开关
        # 报告配置（支持新旧两种格式，优先使用旧格式保持向后兼容）
        "REPORT_MODE": config_data.get("REPORT_MODE")
        or config_data.get("report", {}).get("mode", "daily"),
        "RANK_THRESHOLD": config_data.get("RANK_THRESHOLD")
        or config_data.get("report", {}).get("rank_threshold", 10),
        # 通知配置
        "ENABLE_NOTIFICATION": config_data["notification"]["enable_notification"],
        "MESSAGE_BATCH_SIZE": config_data["notification"]["message_batch_size"],
        "DINGTALK_BATCH_SIZE": config_data["notification"].get(
            "dingtalk_batch_size", 20000
        ),
        "BATCH_SEND_INTERVAL": config_data["notification"]["batch_send_interval"],
        "FEISHU_MESSAGE_SEPARATOR": config_data["notification"][
            "feishu_message_separator"
        ],
        # 静默推送配置
        "SILENT_PUSH": {
            "ENABLED": config_data["notification"]
            .get("silent_push", {})
            .get("enabled", False),
            "TIME_RANGE": {
                "START": config_data["notification"]
                .get("silent_push", {})
                .get("time_range", {})
                .get("start", "08:00"),
                "END": config_data["notification"]
                .get("silent_push", {})
                .get("time_range", {})
                .get("end", "22:00"),
            },
            "ONCE_PER_DAY": config_data["notification"]
            .get("silent_push", {})
            .get("once_per_day", True),
            "RECORD_RETENTION_DAYS": config_data["notification"]
            .get("silent_push", {})
            .get("push_record_retention_days", 7),
        },
        # 权重配置（支持新旧两种格式）
        "WEIGHT_CONFIG": {
            "RANK_WEIGHT": config_data.get("weight", {}).get("rank_weight", 0.6),
            "FREQUENCY_WEIGHT": config_data.get("weight", {}).get(
                "frequency_weight", 0.3
            ),
            "HOTNESS_WEIGHT": config_data.get("weight", {}).get("hotness_weight", 0.1),
        },
        # 平台配置
        "PLATFORMS": config_data["platforms"],
    }

    # Webhook 配置（环境变量优先）
    notification = config_data.get("notification", {})
    webhooks = notification.get("webhooks", {})

    config["FEISHU_WEBHOOK_URL"] = os.environ.get(
        "FEISHU_WEBHOOK_URL", ""
    ).strip() or webhooks.get("feishu_url", "")
    config["DINGTALK_WEBHOOK_URL"] = os.environ.get(
        "DINGTALK_WEBHOOK_URL", ""
    ).strip() or webhooks.get("dingtalk_url", "")
    config["WEWORK_WEBHOOK_URL"] = os.environ.get(
        "WEWORK_WEBHOOK_URL", ""
    ).strip() or webhooks.get("wework_url", "")
    config["TELEGRAM_BOT_TOKEN"] = os.environ.get(
        "TELEGRAM_BOT_TOKEN", ""
    ).strip() or webhooks.get("telegram_bot_token", "")
    config["TELEGRAM_CHAT_ID"] = os.environ.get(
        "TELEGRAM_CHAT_ID", ""
    ).strip() or webhooks.get("telegram_chat_id", "")

    return config


def load_frequency_words(file_path: Optional[str] = None):
    """加载频率词配置

    支持两种格式：
    1. 旧格式（每行一个词组）：[必须词] 普通词1, 普通词2, 普通词3
    2. 新格式（多行分组）：
       +必须词1
       +必须词2
       普通词1
       普通词2

    Args:
        file_path: 频率词文件路径

    Returns:
        (processed_groups, filter_words) 元组

    Raises:
        FileNotFoundError: 文件不存在
    """
    if file_path is None:
        file_path = os.environ.get("FREQUENCY_WORDS_PATH", "config/frequency_words.txt")

    words_file = Path(file_path)
    if not words_file.exists():
        raise FileNotFoundError(f"频率词文件 {file_path} 不存在")

    with open(words_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed_groups = []
    filter_words = []
    is_filter_section = False

    for line in lines:
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith("#"):
            continue

        # 检测过滤词分隔符
        if line == "---":
            is_filter_section = True
            continue

        # 处理过滤词
        if is_filter_section:
            # 分割逗号分隔的过滤词
            words = [w.strip() for w in line.split(",") if w.strip()]
            filter_words.extend(words)
            continue

        # 处理词组配置（支持 [必须词] 普通词1, 普通词2 格式）
        if line.startswith("[") and "]" in line:
            # 提取必须词和普通词
            bracket_end = line.index("]")
            required_part = line[1:bracket_end].strip()  # 提取 [] 中的内容
            normal_part = line[bracket_end + 1 :].strip()  # 提取 ] 后的内容

            # 解析必须词（可能有多个，逗号分隔）
            group_required_words = [
                w.strip() for w in required_part.split(",") if w.strip()
            ]

            # 解析普通词（逗号分隔）
            group_normal_words = [
                w.strip() for w in normal_part.split(",") if w.strip()
            ]

            if group_required_words or group_normal_words:
                if group_normal_words:
                    group_key = " ".join(group_normal_words[:3])  # 使用前3个词作为 key
                else:
                    group_key = " ".join(group_required_words)

                processed_groups.append(
                    {
                        "required": group_required_words,
                        "normal": group_normal_words,
                        "group_key": group_key,
                    }
                )

    return processed_groups, filter_words
