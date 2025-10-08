"""
消息推送基类模块

定义统一的推送接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseNotifier(ABC):
    """消息推送基类"""

    def __init__(
        self, webhook_url: str, proxy_url: Optional[str] = None, timeout: int = 30
    ):
        """初始化推送器

        Args:
            webhook_url: Webhook URL
            proxy_url: 代理URL（可选）
            timeout: 超时时间（秒）
        """
        self.webhook_url = webhook_url
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.headers = self._get_headers()
        self.proxies = self._get_proxies()

    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {"Content-Type": "application/json"}

    def _get_proxies(self) -> Optional[Dict]:
        """获取代理配置"""
        if self.proxy_url:
            return {"http": self.proxy_url, "https": self.proxy_url}
        return None

    @abstractmethod
    def render_content(
        self, report_data: Dict, update_info: Optional[Dict] = None, mode: str = "daily"
    ) -> str:
        """渲染消息内容（子类实现）

        Args:
            report_data: 报告数据
            update_info: 更新信息（可选）
            mode: 报告模式

        Returns:
            渲染后的内容字符串
        """
        pass

    @abstractmethod
    def build_payload(self, content: str, report_type: str) -> Dict:
        """构建推送载荷（子类实现）

        Args:
            content: 渲染后的内容
            report_type: 报告类型

        Returns:
            推送载荷字典
        """
        pass

    @abstractmethod
    def send(
        self,
        report_data: Dict,
        report_type: str,
        update_info: Optional[Dict] = None,
        mode: str = "daily",
    ) -> bool:
        """发送推送（子类实现）

        Args:
            report_data: 报告数据
            report_type: 报告类型
            update_info: 更新信息（可选）
            mode: 报告模式

        Returns:
            是否发送成功
        """
        pass

    def get_platform_name(self) -> str:
        """获取平台名称"""
        return self.__class__.__name__.replace("Notifier", "")
