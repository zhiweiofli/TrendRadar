"""
测试数据抓取模块
"""

from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
import requests

from trendradar.core.fetcher import DataFetcher


class TestDataFetcher:
    """数据抓取器测试类"""

    def test_init(self, sample_config):
        """测试初始化"""
        fetcher = DataFetcher(sample_config)
        assert fetcher.config == sample_config
        assert len(fetcher.platforms) == 3
        assert fetcher.max_retries == 3
        assert fetcher.timeout == 10

    def test_init_with_proxy(self, sample_config):
        """测试带代理初始化"""
        fetcher = DataFetcher(sample_config, proxy_url="http://127.0.0.1:10086")
        assert fetcher.proxy_url == "http://127.0.0.1:10086"

    def test_build_url(self, sample_config):
        """测试 URL 构建"""
        fetcher = DataFetcher(sample_config)
        url = fetcher._build_url("baidu")
        assert "newsnow.busiyi.world" in url
        assert "id=baidu" in url
        assert "latest" in url

    def test_get_proxies_with_proxy(self, sample_config):
        """测试代理配置获取"""
        fetcher = DataFetcher(sample_config, proxy_url="http://127.0.0.1:10086")
        proxies = fetcher._get_proxies()
        assert proxies is not None
        assert proxies["http"] == "http://127.0.0.1:10086"
        assert proxies["https"] == "http://127.0.0.1:10086"

    def test_get_proxies_without_proxy(self, sample_config):
        """测试无代理配置"""
        fetcher = DataFetcher(sample_config)
        proxies = fetcher._get_proxies()
        assert proxies is None

    @patch("requests.get")
    def test_fetch_platform_sync_success(
        self, mock_get, sample_config, sample_platform, sample_api_response
    ):
        """测试同步抓取成功"""
        # Mock 响应
        mock_response = Mock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher(sample_config)
        result = fetcher.fetch_platform_sync(sample_platform)

        assert result is not None
        assert result["platform_id"] == "baidu"
        assert result["platform_name"] == "百度热搜"
        assert result["data"] == sample_api_response
        assert result["status"] == "success"

    @patch("requests.get")
    def test_fetch_platform_sync_failure(
        self, mock_get, sample_config, sample_platform
    ):
        """测试同步抓取失败"""
        mock_get.side_effect = requests.RequestException("网络错误")

        fetcher = DataFetcher(sample_config, max_retries=1)
        result = fetcher.fetch_platform_sync(sample_platform)

        assert result is None

    @patch("requests.get")
    def test_fetch_platform_sync_invalid_status(
        self, mock_get, sample_config, sample_platform
    ):
        """测试同步抓取 - 无效状态"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "error"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher(sample_config, max_retries=1)
        result = fetcher.fetch_platform_sync(sample_platform)

        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_platform_async_success(
        self, sample_config, sample_platform, sample_api_response
    ):
        """测试异步抓取成功"""
        # Mock aiohttp 响应
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=sample_api_response)
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)

        fetcher = DataFetcher(sample_config)
        result = await fetcher.fetch_platform_async(mock_session, sample_platform)

        assert result is not None
        assert result["platform_id"] == "baidu"
        assert result["platform_name"] == "百度热搜"
        assert result["data"] == sample_api_response

    @pytest.mark.asyncio
    async def test_fetch_platform_async_timeout(self, sample_config, sample_platform):
        """测试异步抓取超时"""
        import asyncio

        mock_session = AsyncMock()
        mock_session.get.side_effect = asyncio.TimeoutError()

        fetcher = DataFetcher(sample_config, max_retries=1)
        result = await fetcher.fetch_platform_async(mock_session, sample_platform)

        assert result is None

    @patch("requests.get")
    def test_fetch_all_sync(self, mock_get, sample_config, sample_api_response):
        """测试同步抓取所有平台"""
        mock_response = Mock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher(sample_config)
        results, failed = fetcher.fetch_all_sync(request_interval=100)

        assert len(results) == 3
        assert len(failed) == 0
        assert all(r["platform_id"] in ["baidu", "weibo", "zhihu"] for r in results)

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_fetch_all_async(
        self, mock_session_class, sample_config, sample_api_response
    ):
        """测试异步抓取所有平台"""
        # Mock aiohttp 会话和响应
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=sample_api_response)
        mock_response.raise_for_status = Mock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_session_class.return_value = mock_session

        fetcher = DataFetcher(sample_config)
        results, failed = await fetcher.fetch_all_async()

        assert len(results) == 3
        assert len(failed) == 0

    @patch("requests.get")
    def test_fetch_all_use_sync(self, mock_get, sample_config, sample_api_response):
        """测试统一接口 - 同步模式"""
        mock_response = Mock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        fetcher = DataFetcher(sample_config)
        results, failed = fetcher.fetch_all(use_async=False, request_interval=100)

        assert len(results) == 3
        assert len(failed) == 0
