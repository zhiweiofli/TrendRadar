"""
飞书推送模块
"""

from typing import Dict, Optional

import requests

from ..utils.file_utils import clean_title
from ..utils.logger import get_logger
from ..utils.time_utils import get_beijing_time
from .base import BaseNotifier

logger = get_logger(__name__)


class FeishuNotifier(BaseNotifier):
    """飞书推送器"""

    def __init__(
        self,
        webhook_url: str,
        proxy_url: Optional[str] = None,
        timeout: int = 30,
        message_separator: str = "━━━━━━━━━━━━━━━━━━",
    ):
        super().__init__(webhook_url, proxy_url, timeout)
        self.message_separator = message_separator

    def _format_title(self, title_data: Dict, show_source: bool = True) -> str:
        """格式化标题显示

        Args:
            title_data: 标题数据
            show_source: 是否显示来源

        Returns:
            格式化后的标题
        """
        cleaned_title = clean_title(title_data["title"])
        link_url = title_data.get("mobile_url") or title_data.get("url", "")

        # 标题链接
        if link_url:
            formatted_title = f"[{cleaned_title}]({link_url})"
        else:
            formatted_title = cleaned_title

        # 新增标记
        title_prefix = "🆕 " if title_data.get("is_new") else ""

        # 构建完整标题
        if show_source:
            result = f"<font color='grey'>[{title_data['source_name']}]</font> {title_prefix}{formatted_title}"
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
                    rank_display = f"<font color='red'>**[{min_rank}]**</font>"
                else:
                    rank_display = (
                        f"<font color='red'>**[{min_rank} - {max_rank}]**</font>"
                    )
            else:
                if min_rank == max_rank:
                    rank_display = f"[{min_rank}]"
                else:
                    rank_display = f"[{min_rank} - {max_rank}]"

            result += f" {rank_display}"

        # 时间显示
        time_display = title_data.get("time_display", "")
        if time_display:
            result += f" <font color='grey'>- {time_display}</font>"

        # 出现次数
        count = title_data.get("count", 1)
        if count > 1:
            result += f" <font color='green'>({count}次)</font>"

        return result

    def render_content(
        self, report_data: Dict, update_info: Optional[Dict] = None, mode: str = "daily"
    ) -> str:
        """渲染飞书内容"""
        text_content = ""

        # 处理主要统计数据
        if report_data.get("stats"):
            text_content += "📊 **热点词汇统计**\n\n"

            total_count = len(report_data["stats"])

            for i, stat in enumerate(report_data["stats"]):
                word = stat["word"]
                count = stat["count"]

                sequence_display = f"<font color='grey'>[{i + 1}/{total_count}]</font>"

                # 热度标记
                if count >= 10:
                    text_content += f"🔥 {sequence_display} **{word}** : <font color='red'>{count}</font> 条\n\n"
                elif count >= 5:
                    text_content += f"📈 {sequence_display} **{word}** : <font color='orange'>{count}</font> 条\n\n"
                else:
                    text_content += f"📌 {sequence_display} **{word}** : {count} 条\n\n"

                # 处理标题列表
                for j, title_data in enumerate(stat["titles"], 1):
                    formatted_title = self._format_title(title_data, show_source=True)
                    text_content += f"  {j}. {formatted_title}\n"

                    if j < len(stat["titles"]):
                        text_content += "\n"

                if i < len(report_data["stats"]) - 1:
                    text_content += f"\n{self.message_separator}\n\n"

        # 如果没有统计数据
        if not text_content:
            if mode == "incremental":
                mode_text = "增量模式下暂无新增匹配的热点词汇"
            elif mode == "current":
                mode_text = "当前榜单模式下暂无匹配的热点词汇"
            else:
                mode_text = "暂无匹配的热点词汇"
            text_content = f"📭 {mode_text}\n\n"

        # 处理新增标题
        if report_data.get("new_titles"):
            if text_content and "暂无匹配" not in text_content:
                text_content += f"\n{self.message_separator}\n\n"

            text_content += (
                f"🆕 **本次新增热点新闻** (共 {report_data['total_new_count']} 条)\n\n"
            )

            for source_data in report_data["new_titles"]:
                text_content += f"**{source_data['source_name']}** ({len(source_data['titles'])} 条):\n"

                for j, title_data in enumerate(source_data["titles"], 1):
                    title_data_copy = title_data.copy()
                    title_data_copy["is_new"] = False
                    formatted_title = self._format_title(
                        title_data_copy, show_source=False
                    )
                    text_content += f"  {j}. {formatted_title}\n"

                text_content += "\n"

        # 处理失败的平台
        if report_data.get("failed_ids"):
            if text_content and "暂无匹配" not in text_content:
                text_content += f"\n{self.message_separator}\n\n"

            text_content += "⚠️ **数据获取失败的平台：**\n\n"
            for i, id_value in enumerate(report_data["failed_ids"], 1):
                text_content += f"  • <font color='red'>{id_value}</font>\n"

        # 添加更新时间
        now = get_beijing_time()
        text_content += f"\n\n<font color='grey'>更新时间：{now.strftime('%Y-%m-%d %H:%M:%S')}</font>"

        # 版本更新提示
        if update_info:
            text_content += f"\n<font color='grey'>TrendRadar 发现新版本 {update_info['remote_version']}，当前 {update_info['current_version']}</font>"

        return text_content

    def build_payload(self, content: str, report_type: str) -> Dict:
        """构建飞书推送载荷"""
        now = get_beijing_time()

        return {
            "msg_type": "text",
            "content": {
                "text": content,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": report_type,
            },
        }

    def send(
        self,
        report_data: Dict,
        report_type: str,
        update_info: Optional[Dict] = None,
        mode: str = "daily",
    ) -> bool:
        """发送到飞书"""
        try:
            # 渲染内容
            content = self.render_content(report_data, update_info, mode)

            # 构建载荷
            payload = self.build_payload(content, report_type)

            # 发送请求
            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                json=payload,
                proxies=self.proxies,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                logger.info(f"飞书通知发送成功 [{report_type}]")
                return True
            else:
                logger.error(
                    f"飞书通知发送失败 [{report_type}]，状态码：{response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"飞书通知发送出错 [{report_type}]：{e}", exc_info=True)
            return False
