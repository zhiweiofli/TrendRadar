"""
配置和数据验证模块
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from .exceptions import ConfigError, ValidationError
from .logger import get_logger

logger = get_logger(__name__)


class ConfigValidator:
    """配置验证器"""

    # 必需的配置键（utils/config.py 生成的是大写键名）
    REQUIRED_KEYS = ["WEIGHT_CONFIG", "PLATFORMS", "REPORT_MODE"]

    # 报告模式选项
    VALID_REPORT_MODES = ["daily", "incremental", "current"]

    def validate(self, config: Dict) -> None:
        """验证配置文件完整性和正确性

        Args:
            config: 配置字典

        Raises:
            ConfigError: 配置验证失败
        """
        logger.info("开始验证配置...")

        self._check_required_keys(config)
        self._validate_weights(config)
        self._validate_platforms(config)
        self._validate_report_mode(config)
        self._validate_webhooks(config)

        logger.info("配置验证通过")

    def _check_required_keys(self, config: Dict) -> None:
        """检查必需字段

        Args:
            config: 配置字典

        Raises:
            ConfigError: 缺少必需字段
        """
        missing_keys = []
        for key in self.REQUIRED_KEYS:
            if key not in config:
                missing_keys.append(key)

        if missing_keys:
            raise ConfigError(
                f"配置缺少必需字段: {', '.join(missing_keys)}",
                "请检查 config/config.yaml 文件和 utils/config.py 的配置加载逻辑",
            )

    def _validate_weights(self, config: Dict) -> None:
        """验证权重配置

        Args:
            config: 配置字典

        Raises:
            ConfigError: 权重配置错误
        """
        weight_config = config.get("WEIGHT_CONFIG", {})

        if not weight_config:
            raise ConfigError(
                "权重配置 (WEIGHT_CONFIG) 不能为空",
                "请在 config.yaml 中配置 weight 部分",
            )

        required_weights = ["RANK_WEIGHT", "FREQUENCY_WEIGHT", "HOTNESS_WEIGHT"]
        for weight_name in required_weights:
            if weight_name not in weight_config:
                raise ConfigError(
                    f"权重配置缺少字段: {weight_name}",
                    "请确保 weight 配置包含所有三个权重字段",
                )

            weight_value = weight_config[weight_name]
            if not isinstance(weight_value, (int, float)):
                raise ConfigError(
                    f"权重 {weight_name} 必须是数字，当前为: {type(weight_value).__name__}",
                    "请检查 weight 配置中的数值类型",
                )

            if not (0 <= weight_value <= 1):
                raise ConfigError(
                    f"权重 {weight_name} 必须在 0-1 之间，当前为: {weight_value}",
                    "请调整权重值到合理范围",
                )

        # 检查权重总和
        weight_sum = sum(
            [
                weight_config["RANK_WEIGHT"],
                weight_config["FREQUENCY_WEIGHT"],
                weight_config["HOTNESS_WEIGHT"],
            ]
        )

        if abs(weight_sum - 1.0) > 0.01:
            raise ConfigError(
                f"权重总和必须为 1.0，当前为: {weight_sum:.3f}",
                "请调整三个权重值，使其总和等于 1.0",
            )

    def _validate_platforms(self, config: Dict) -> None:
        """验证平台配置

        Args:
            config: 配置字典

        Raises:
            ConfigError: 平台配置错误
        """
        platforms = config.get("PLATFORMS", [])

        if not platforms:
            raise ConfigError(
                "平台列表 (PLATFORMS) 不能为空",
                "请在 config.yaml 的 platforms 部分至少配置一个平台",
            )

        if not isinstance(platforms, list):
            raise ConfigError(
                "平台配置必须是列表类型", "请检查 config.yaml 中 platforms 的格式"
            )

        platform_ids = set()
        for i, platform in enumerate(platforms):
            if not isinstance(platform, dict):
                raise ConfigError(
                    f"平台配置项 #{i+1} 必须是字典类型", "请检查每个平台配置项的格式"
                )

            if "id" not in platform:
                raise ConfigError(
                    f"平台配置项 #{i+1} 缺少 'id' 字段", "每个平台必须有 id 字段"
                )

            platform_id = platform["id"]
            if platform_id in platform_ids:
                raise ConfigError(
                    f"平台 ID 重复: {platform_id}", "请确保每个平台的 id 是唯一的"
                )
            platform_ids.add(platform_id)

    def _validate_report_mode(self, config: Dict) -> None:
        """验证报告模式

        Args:
            config: 配置字典

        Raises:
            ConfigError: 报告模式无效
        """
        report_mode = config.get("REPORT_MODE")

        if not report_mode:
            raise ConfigError(
                "报告模式 (REPORT_MODE) 未配置", "请在 config.yaml 中配置 report.mode"
            )

        if report_mode not in self.VALID_REPORT_MODES:
            raise ConfigError(
                f"无效的报告模式: {report_mode}",
                f"有效选项: {', '.join(self.VALID_REPORT_MODES)}",
            )

    def _validate_webhooks(self, config: Dict) -> None:
        """验证 Webhook URL 格式

        Args:
            config: 配置字典

        Raises:
            ConfigError: Webhook URL 格式错误
        """
        webhook_keys = [
            ("FEISHU_WEBHOOK_URL", "飞书"),
            ("DINGTALK_WEBHOOK_URL", "钉钉"),
            ("WEWORK_WEBHOOK_URL", "企业微信"),
        ]

        for key, name in webhook_keys:
            url = config.get(key, "")
            if url and not url.startswith(("http://", "https://")):
                raise ConfigError(
                    f"{name} Webhook URL 格式错误: {url}",
                    f"{name} Webhook URL 必须以 http:// 或 https:// 开头",
                )


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate_news_item(self, item: Dict) -> bool:
        """验证单条新闻数据

        Args:
            item: 新闻数据项

        Returns:
            是否有效
        """
        required_fields = ["title", "url"]

        for field in required_fields:
            if field not in item or not item[field]:
                self.logger.warning(f"新闻数据缺少必需字段: {field}")
                return False

        # 验证 title 长度
        title = item.get("title", "")
        if len(title) > 500:
            self.logger.warning(f"新闻标题过长: {len(title)} 字符")
            return False

        # 验证 URL 格式
        url = item.get("url", "")
        if not self._is_valid_url(url):
            self.logger.warning(f"新闻 URL 格式无效: {url}")
            return False

        return True

    def _is_valid_url(self, url: str) -> bool:
        """验证 URL 格式

        Args:
            url: URL 字符串

        Returns:
            是否为有效 URL
        """
        if not url:
            return False

        # 简单的 URL 格式验证
        url_pattern = re.compile(
            r"^https?://"  # http:// 或 https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # 域名
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP 地址
            r"(?::\d+)?"  # 可选端口
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return bool(url_pattern.match(url))

    def validate_and_clean(self, items: List[Dict]) -> List[Dict]:
        """验证并清洗数据

        Args:
            items: 新闻数据列表

        Returns:
            清洗后的有效数据列表
        """
        valid_items = []
        invalid_count = 0

        for item in items:
            if self.validate_news_item(item):
                # 清洗数据
                cleaned_item = self._clean_news_item(item)
                valid_items.append(cleaned_item)
            else:
                invalid_count += 1

        if invalid_count > 0:
            self.logger.warning(f"发现 {invalid_count} 条无效数据，已过滤")

        self.logger.info(f"数据验证完成: 有效 {len(valid_items)}, 无效 {invalid_count}")
        return valid_items

    def _clean_news_item(self, item: Dict) -> Dict:
        """清洗单条新闻数据

        Args:
            item: 原始新闻数据

        Returns:
            清洗后的数据
        """
        cleaned = item.copy()

        # 清洗标题
        if "title" in cleaned:
            title = cleaned["title"]
            # 去除多余空格
            title = " ".join(str(title).split())
            # 限制长度
            if len(title) > 200:
                title = title[:197] + "..."
            cleaned["title"] = title

        # 清洗 URL
        if "url" in cleaned:
            cleaned["url"] = str(cleaned["url"]).strip()

        return cleaned


def validate_frequency_words_file(file_path: str) -> bool:
    """验证关键词文件格式

    Args:
        file_path: 关键词文件路径

    Returns:
        是否有效

    Raises:
        ConfigError: 文件格式错误
    """
    if not Path(file_path).exists():
        raise ConfigError(
            f"关键词文件不存在: {file_path}",
            "请确保 config/frequency_words.txt 文件存在",
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            raise ConfigError(
                "关键词文件为空", "请在 config/frequency_words.txt 中添加至少一个关键词"
            )

        valid_lines = 0
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 验证格式：关键词 或 关键词:权重
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) != 2:
                    raise ConfigError(
                        f"关键词文件第 {i} 行格式错误: {line}",
                        "格式应为: 关键词:权重 或 关键词",
                    )

                keyword, weight = parts
                if not keyword.strip():
                    raise ConfigError(
                        f"关键词文件第 {i} 行关键词为空", "请确保每行都有关键词"
                    )

                try:
                    int(weight.strip())
                except ValueError:
                    raise ConfigError(
                        f"关键词文件第 {i} 行权重必须是整数: {weight}",
                        "请确保权重是有效的整数",
                    )

            valid_lines += 1

        if valid_lines == 0:
            raise ConfigError(
                "关键词文件没有有效内容", "请确保文件中至少有一行有效的关键词配置"
            )

        logger.info(f"关键词文件验证通过: {valid_lines} 个有效关键词")
        return True

    except UnicodeDecodeError:
        raise ConfigError("关键词文件编码错误", "请确保文件使用 UTF-8 编码保存")
