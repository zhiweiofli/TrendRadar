"""
数据抓取模块

支持同步和异步两种模式
"""

import asyncio
import json
import random
import time
from typing import Dict, List, Optional, Tuple, Union

import aiohttp
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataFetcher:
    """数据抓取器

    支持同步和异步两种方式抓取数据
    """

    # 默认 API 地址
    API_BASE_URL = "https://newsnow.busiyi.world/api/s"

    # 默认 Headers
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        config: Dict,
        proxy_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 10,
    ):
        """初始化数据抓取器

        Args:
            config: 配置字典
            proxy_url: 代理地址
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
        """
        self.config = config
        self.proxy_url = proxy_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.platforms = config.get("PLATFORMS", [])

    def _build_url(self, platform_id: str) -> str:
        """构建 API URL

        Args:
            platform_id: 平台 ID

        Returns:
            完整的 API URL
        """
        return f"{self.API_BASE_URL}?id={platform_id}&latest"

    def _get_proxies(self) -> Optional[Dict]:
        """获取代理配置

        Returns:
            代理字典或 None
        """
        if self.proxy_url:
            return {"http": self.proxy_url, "https": self.proxy_url}
        return None

    # ========== 同步方法 ==========

    def fetch_platform_sync(
        self,
        platform: Dict,
    ) -> Optional[Dict]:
        """同步抓取单个平台数据

        Args:
            platform: 平台配置字典，包含 id 和 name

        Returns:
            平台数据字典或 None
        """
        platform_id = platform["id"]
        platform_name = platform.get("name", platform_id)
        url = self._build_url(platform_id)

        logger.info(f"开始抓取: {platform_name} ({platform_id})")

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    proxies=self._get_proxies(),
                    headers=self.DEFAULT_HEADERS,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                status = data.get("status", "unknown")

                if status not in ["success", "cache"]:
                    raise ValueError(f"响应状态异常: {status}")

                logger.info(f"抓取成功: {platform_name} (状态: {status})")
                return {
                    "platform_id": platform_id,
                    "platform_name": platform_name,
                    "data": data,
                    "status": status,
                }

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = random.uniform(2, 5) + attempt * random.uniform(1, 2)
                    logger.warning(
                        f"抓取失败: {platform_name}, 错误: {e}, "
                        f"{wait_time:.2f}秒后重试 ({attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"抓取失败: {platform_name}, 错误: {e}")
                    return None

        return None

    def fetch_all_sync(
        self, request_interval: int = 1000
    ) -> Tuple[List[Dict], List[str]]:
        """同步抓取所有平台数据

        Args:
            request_interval: 请求间隔（毫秒）

        Returns:
            (成功的结果列表, 失败的平台ID列表)
        """
        results = []
        failed_platforms = []

        logger.info(f"开始同步抓取 {len(self.platforms)} 个平台")
        start_time = time.time()

        for i, platform in enumerate(self.platforms):
            result = self.fetch_platform_sync(platform)

            if result:
                results.append(result)
            else:
                failed_platforms.append(platform["id"])

            # 请求间隔
            if i < len(self.platforms) - 1:
                time.sleep(request_interval / 1000)

        duration = time.time() - start_time
        logger.info(
            f"同步抓取完成: 成功 {len(results)}/{len(self.platforms)}, "
            f"耗时 {duration:.2f}秒"
        )

        return results, failed_platforms

    # ========== 异步方法 ==========

    async def fetch_platform_async(
        self,
        session: aiohttp.ClientSession,
        platform: Dict,
    ) -> Optional[Dict]:
        """异步抓取单个平台数据

        Args:
            session: aiohttp 会话
            platform: 平台配置字典

        Returns:
            平台数据字典或 None
        """
        platform_id = platform["id"]
        platform_name = platform.get("name", platform_id)
        url = self._build_url(platform_id)

        logger.info(f"开始异步抓取: {platform_name} ({platform_id})")

        for attempt in range(self.max_retries + 1):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    proxy=self.proxy_url,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    status = data.get("status", "unknown")
                    if status not in ["success", "cache"]:
                        raise ValueError(f"响应状态异常: {status}")

                    logger.info(f"异步抓取成功: {platform_name} (状态: {status})")
                    return {
                        "platform_id": platform_id,
                        "platform_name": platform_name,
                        "data": data,
                        "status": status,
                    }

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    wait_time = random.uniform(2, 5) + attempt * random.uniform(1, 2)
                    logger.warning(
                        f"异步抓取超时: {platform_name}, "
                        f"{wait_time:.2f}秒后重试 ({attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"异步抓取超时: {platform_name}")
                    return None

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = random.uniform(2, 5) + attempt * random.uniform(1, 2)
                    logger.warning(
                        f"异步抓取失败: {platform_name}, 错误: {e}, "
                        f"{wait_time:.2f}秒后重试 ({attempt + 1}/{self.max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"异步抓取失败: {platform_name}, 错误: {e}")
                    return None

        return None

    async def fetch_all_async(self) -> Tuple[List[Dict], List[str]]:
        """异步并发抓取所有平台数据

        Returns:
            (成功的结果列表, 失败的平台ID列表)
        """
        logger.info(f"开始异步并发抓取 {len(self.platforms)} 个平台")
        start_time = time.time()

        # 配置连接器，限制并发连接数
        connector = aiohttp.TCPConnector(
            limit=10, limit_per_host=5  # 最大并发连接数  # 每个主机的最大连接数
        )

        async with aiohttp.ClientSession(
            headers=self.DEFAULT_HEADERS, connector=connector
        ) as session:
            # 创建所有任务
            tasks = [
                self.fetch_platform_async(session, platform)
                for platform in self.platforms
            ]

            # 并发执行
            results_raw = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        results = []
        failed_platforms = []

        for i, result in enumerate(results_raw):
            if isinstance(result, Exception):
                logger.error(f"平台 {self.platforms[i]['id']} 抓取异常: {result}")
                failed_platforms.append(self.platforms[i]["id"])
            elif result is None:
                failed_platforms.append(self.platforms[i]["id"])
            else:
                results.append(result)

        duration = time.time() - start_time
        logger.info(
            f"异步抓取完成: 成功 {len(results)}/{len(self.platforms)}, "
            f"耗时 {duration:.2f}秒"
        )

        return results, failed_platforms

    # ========== 统一接口 ==========

    def fetch_all(
        self, use_async: bool = True, request_interval: int = 1000
    ) -> Tuple[List[Dict], List[str]]:
        """抓取所有平台数据（自动选择同步或异步）

        Args:
            use_async: 是否使用异步模式
            request_interval: 同步模式下的请求间隔（毫秒）

        Returns:
            (成功的结果列表, 失败的平台ID列表)
        """
        if use_async:
            return asyncio.run(self.fetch_all_async())
        else:
            return self.fetch_all_sync(request_interval)
