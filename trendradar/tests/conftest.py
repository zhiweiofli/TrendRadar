"""
pytest 配置文件和通用 fixtures
"""

from pathlib import Path
from typing import Dict

import pytest


@pytest.fixture
def sample_config() -> Dict:
    """测试用配置"""
    return {
        "VERSION_CHECK_URL": "https://example.com/version",
        "SHOW_VERSION_UPDATE": True,
        "TEST_MODE": True,
        "REQUEST_INTERVAL": 1000,
        "REPORT_MODE": "current",
        "RANK_THRESHOLD": 5,
        "USE_PROXY": False,
        "DEFAULT_PROXY": "",
        "ENABLE_CRAWLER": True,
        "ENABLE_ASYNC": True,
        "ENABLE_NOTIFICATION": False,
        "WEIGHT_CONFIG": {
            "RANK_WEIGHT": 0.6,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.1,
        },
        "PLATFORMS": [
            {"id": "baidu", "name": "百度热搜"},
            {"id": "weibo", "name": "微博热搜"},
            {"id": "zhihu", "name": "知乎热榜"},
        ],
    }


@pytest.fixture
def sample_platform() -> Dict:
    """测试用单个平台配置"""
    return {"id": "baidu", "name": "百度热搜"}


@pytest.fixture
def sample_api_response() -> Dict:
    """模拟 API 响应数据"""
    return {
        "status": "success",
        "data": {
            "id": "baidu",
            "name": "百度热搜",
            "items": [
                {
                    "title": "测试新闻1",
                    "url": "https://example.com/1",
                    "rank": 1,
                    "hot": 100000,
                },
                {
                    "title": "测试新闻2",
                    "url": "https://example.com/2",
                    "rank": 2,
                    "hot": 50000,
                },
            ],
        },
    }


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """临时输出目录"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_frequency_words() -> Dict[str, int]:
    """测试用关键词字典"""
    return {
        "AI": 3,
        "科技": 2,
        "教育": 2,
        "经济": 1,
    }
