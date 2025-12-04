"""
Telegram推送模块（支持分批发送）
"""

import time
from typing import Dict, List, Optional

import requests

from ..utils.file_utils import clean_title
from ..utils.logger import get_logger
from ..utils.time_utils import get_beijing_time
from .base import BaseNotifier

logger = get_logger(__name__)


class TelegramNotifier(BaseNotifier):
    """Telegram推送器"""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        proxy_url: Optional[str] = None,
        timeout: int = 30,
        max_bytes: int = 4000,
        batch_interval: float = 1.0,
    ):
        """初始化Telegram推送器

        Args:
            bot_token: Bot Token
            chat_id: Chat ID
            proxy_url: 代理URL
            timeout: 超时时间
            max_bytes: 单次最大字节数（Telegram限制4096字节）
            batch_interval: 批次发送间隔（秒）
        """
        # 构建webhook_url
        webhook_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        super().__init__(webhook_url, proxy_url, timeout)

        self.bot_token = bot_token
        self.chat_id = chat_id
        self.max_bytes = max_bytes
        self.batch_interval = batch_interval

    def _format_title(self, title_data: Dict, show_source: bool = True) -> str:
        """格式化标题显示（HTML格式）"""
        cleaned_title = clean_title(title_data["title"])
        link_url = title_data.get("mobile_url") or title_data.get("url", "")

        # HTML转义
        def html_escape(text: str) -> str:
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        cleaned_title = html_escape(cleaned_title)

        # 标题链接
        if link_url:
            formatted_title = f'<a href="{link_url}">{cleaned_title}</a>'
        else:
            formatted_title = cleaned_title

        # 新增标记
        title_prefix = "🆕 " if title_data.get("is_new") else ""

        # 构建完整标题
        if show_source:
            source_name = html_escape(title_data["source_name"])
            result = f"[{source_name}] {title_prefix}{formatted_title}"
        else:
            result = f"{title_prefix}{formatted_title}"

        # 排名显示
        ranks = title_data.get("ranks", [])
        if ranks:
            min_rank = min(ranks)
            max_rank = max(ranks)
            rank_threshold = title_data.get("rank_threshold", 10)

            if min_rank <= rank_threshold:
                if min_rank == max_rank:
                    rank_display = f"<b>[{min_rank}]</b>"
                else:
                    rank_display = f"<b>[{min_rank} - {max_rank}]</b>"
            else:
                if min_rank == max_rank:
                    rank_display = f"[{min_rank}]"
                else:
                    rank_display = f"[{min_rank} - {max_rank}]"

            result += f" {rank_display}"

        # 时间显示
        time_display = title_data.get("time_display", "")
        if time_display:
            result += f" - {time_display}"

        # 出现次数
        count = title_data.get("count", 1)
        if count > 1:
            result += f" ({count}次)"

        return result

    def render_content(
        self, report_data: Dict, update_info: Optional[Dict] = None, mode: str = "daily"
    ) -> str:
        """渲染Telegram内容（HTML格式）"""
        now = get_beijing_time()
        text_content = ""

        # 头部信息
        total_titles = sum(
            len(stat["titles"])
            for stat in report_data.get("stats", [])
            if stat["count"] > 0
        )
        text_content += f"<b>总新闻数：</b> {total_titles}\n\n"
        text_content += f"<b>时间：</b> {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text_content += f"<b>类型：</b> 热点分析报告\n\n"
        text_content += "━━━━━━━━━━━━━━━━━━\n\n"

        # 处理主要统计数据
        if report_data.get("stats"):
            text_content += "📊 <b>热点词汇统计</b>\n\n"

            total_count = len(report_data["stats"])

            for i, stat in enumerate(report_data["stats"]):
                word = stat["word"]
                count = stat["count"]

                sequence_display = f"[{i + 1}/{total_count}]"

                if count >= 10:
                    text_content += (
                        f"🔥 {sequence_display} <b>{word}</b> : <b>{count}</b> 条\n\n"
                    )
                elif count >= 5:
                    text_content += (
                        f"📈 {sequence_display} <b>{word}</b> : <b>{count}</b> 条\n\n"
                    )
                else:
                    text_content += (
                        f"📌 {sequence_display} <b>{word}</b> : {count} 条\n\n"
                    )

                for j, title_data in enumerate(stat["titles"], 1):
                    formatted_title = self._format_title(title_data, show_source=True)
                    text_content += f"  {j}. {formatted_title}\n"

                    if j < len(stat["titles"]):
                        text_content += "\n"

                if i < len(report_data["stats"]) - 1:
                    text_content += "\n━━━━━━━━━━━━━━━━━━\n\n"

        if not report_data.get("stats"):
            if mode == "incremental":
                mode_text = "增量模式下暂无新增匹配的热点词汇"
            elif mode == "current":
                mode_text = "当前榜单模式下暂无匹配的热点词汇"
            else:
                mode_text = "暂无匹配的热点词汇"
            text_content += f"📭 {mode_text}\n\n"

        if report_data.get("new_titles"):
            if text_content and "暂无匹配" not in text_content:
                text_content += "\n━━━━━━━━━━━━━━━━━━\n\n"

            text_content += f"🆕 <b>本次新增热点新闻</b> (共 {report_data['total_new_count']} 条)\n\n"

            for source_data in report_data["new_titles"]:
                text_content += f"<b>{source_data['source_name']}</b> ({len(source_data['titles'])} 条):\n\n"

                for j, title_data in enumerate(source_data["titles"], 1):
                    title_data_copy = title_data.copy()
                    title_data_copy["is_new"] = False
                    formatted_title = self._format_title(
                        title_data_copy, show_source=False
                    )
                    text_content += f"  {j}. {formatted_title}\n"

                text_content += "\n"

        if report_data.get("failed_ids"):
            if text_content and "暂无匹配" not in text_content:
                text_content += "\n━━━━━━━━━━━━━━━━━━\n\n"

            text_content += "⚠️ <b>数据获取失败的平台：</b>\n\n"
            for i, id_value in enumerate(report_data["failed_ids"], 1):
                text_content += f"  • <b>{id_value}</b>\n"

        text_content += f"\n\n<i>更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}</i>"

        if update_info:
            text_content += f"\n<i>TrendRadar 发现新版本 {update_info['remote_version']}，当前 {update_info['current_version']}</i>"

        return text_content

    def _split_into_batches(self, content: str) -> List[str]:
        """将内容分批（按字节大小）"""
        content_bytes = content.encode("utf-8")

        if len(content_bytes) <= self.max_bytes:
            return [content]

        batches = []
        current_batch = ""
        lines = content.split("\n")

        for line in lines:
            test_batch = current_batch + line + "\n"
            if len(test_batch.encode("utf-8")) > self.max_bytes:
                if current_batch:
                    batches.append(current_batch.rstrip())
                current_batch = line + "\n"
            else:
                current_batch = test_batch

        if current_batch:
            batches.append(current_batch.rstrip())

        return batches if batches else [content]

    def build_payload(self, content: str, report_type: str) -> Dict:
        """构建Telegram推送载荷"""
        return {
            "chat_id": self.chat_id,
            "text": content,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

    def send(
        self,
        report_data: Dict,
        report_type: str,
        update_info: Optional[Dict] = None,
        mode: str = "daily",
    ) -> bool:
        """发送到Telegram（支持分批）"""
        try:
            # 渲染内容
            content = self.render_content(report_data, update_info, mode)

            # 分批
            batches = self._split_into_batches(content)
            logger.info(f"Telegram消息分为 {len(batches)} 批次发送 [{report_type}]")

            # 逐批发送
            for i, batch_content in enumerate(batches, 1):
                batch_size = len(batch_content.encode("utf-8"))
                logger.info(
                    f"发送Telegram第 {i}/{len(batches)} 批次，大小：{batch_size} 字节 [{report_type}]"
                )

                # 添加批次标识
                if len(batches) > 1:
                    batch_header = f"<b>[第 {i}/{len(batches)} 批次]</b>\n\n"
                    batch_content = batch_header + batch_content

                # 构建载荷
                payload = self.build_payload(batch_content, report_type)

                # 发送请求
                response = requests.post(
                    self.webhook_url,
                    headers=self.headers,
                    json=payload,
                    proxies=self.proxies,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.info(
                            f"Telegram第 {i}/{len(batches)} 批次发送成功 [{report_type}]"
                        )
                        if i < len(batches):
                            time.sleep(self.batch_interval)
                    else:
                        logger.error(
                            f"Telegram第 {i}/{len(batches)} 批次发送失败 [{report_type}]，错误：{result.get('description')}"
                        )
                        return False
                else:
                    logger.error(
                        f"Telegram第 {i}/{len(batches)} 批次发送失败 [{report_type}]，状态码：{response.status_code}"
                    )
                    return False

            logger.info(f"Telegram所有 {len(batches)} 批次发送完成 [{report_type}]")
            return True

        except Exception as e:
            logger.error(f"Telegram通知发送出错 [{report_type}]：{e}", exc_info=True)
            return False
