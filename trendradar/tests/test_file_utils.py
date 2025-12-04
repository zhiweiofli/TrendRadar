"""
测试文件工具函数
"""

from pathlib import Path

import pytest

from trendradar.utils.file_utils import (
    clean_title,
    ensure_directory_exists,
    get_config_path,
    get_output_path,
    get_project_root,
)


class TestFileUtils:
    """文件工具函数测试类"""

    def test_ensure_directory_exists(self, tmp_path):
        """测试目录创建"""
        test_dir = tmp_path / "test" / "nested" / "directory"
        ensure_directory_exists(str(test_dir))
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_ensure_directory_exists_already_exists(self, tmp_path):
        """测试已存在目录"""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()
        # 不应该抛出异常
        ensure_directory_exists(str(test_dir))
        assert test_dir.exists()

    def test_get_output_path(self):
        """测试输出路径生成"""
        path = get_output_path("html", "test.html")
        assert isinstance(path, str)
        assert "output" in path
        assert "html" in path
        assert "test.html" in path
        assert "年" in path  # 日期文件夹

    def test_clean_title_basic(self):
        """测试基本标题清理"""
        title = "  测试标题  "
        result = clean_title(title)
        assert result == "测试标题"

    def test_clean_title_with_newlines(self):
        """测试带换行符的标题"""
        title = "测试\n标题\r\n内容"
        result = clean_title(title)
        assert "\n" not in result
        assert "\r" not in result
        assert result == "测试 标题 内容"

    def test_clean_title_multiple_spaces(self):
        """测试多空格处理"""
        title = "测试   多个    空格"
        result = clean_title(title)
        assert result == "测试 多个 空格"

    def test_clean_title_non_string(self):
        """测试非字符串输入"""
        result = clean_title(12345)
        assert result == "12345"

    def test_get_project_root(self):
        """测试获取项目根目录"""
        root = get_project_root()
        assert isinstance(root, Path)
        assert root.exists()
        # 应该包含 trendradar 目录
        assert (root / "trendradar").exists()

    def test_get_config_path_default(self):
        """测试获取默认配置路径"""
        config_path = get_config_path()
        assert isinstance(config_path, Path)
        assert config_path.name == "config.yaml"
        assert "config" in str(config_path)

    def test_get_config_path_custom(self):
        """测试获取自定义配置路径"""
        config_path = get_config_path("custom.yaml")
        assert config_path.name == "custom.yaml"
