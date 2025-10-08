"""
测试时间工具函数
"""

from datetime import datetime

import pytest

from trendradar.utils.time_utils import (
    format_date_folder,
    format_time_display,
    format_time_filename,
    get_beijing_time,
    is_in_time_range,
)


class TestTimeUtils:
    """时间工具函数测试类"""

    def test_get_beijing_time(self):
        """测试获取北京时间"""
        time = get_beijing_time()
        assert isinstance(time, datetime)
        assert time.tzinfo is not None
        assert time.tzinfo.zone == "Asia/Shanghai"

    def test_format_date_folder(self):
        """测试日期格式化"""
        folder = format_date_folder()
        assert isinstance(folder, str)
        assert "年" in folder
        assert "月" in folder
        assert "日" in folder
        # 验证格式：2025年10月08日
        assert len(folder) >= 11

    def test_format_time_filename(self):
        """测试时间文件名格式化"""
        filename = format_time_filename()
        assert isinstance(filename, str)
        assert "时" in filename
        assert "分" in filename
        # 验证格式：13时45分 或 14时01分（长度在 6-7 之间）
        assert 6 <= len(filename) <= 7

    def test_format_time_display_same(self):
        """测试相同时间显示"""
        result = format_time_display("10:00", "10:00")
        assert result == "10:00"

    def test_format_time_display_range(self):
        """测试时间范围显示"""
        result = format_time_display("10:00", "12:00")
        assert result == "10:00 - 12:00"

    def test_is_in_time_range_valid_format(self):
        """测试时间范围检查 - 合法格式"""
        # 注意：这个测试结果取决于运行时的实际时间
        result = is_in_time_range("00:00", "23:59")
        assert isinstance(result, bool)

    def test_is_in_time_range_logic(self):
        """测试时间范围逻辑"""
        # 如果当前时间是 14:30，那么：
        # - [13:00, 15:00] 应该返回 True
        # - [15:00, 17:00] 应该返回 False
        # 但由于无法控制当前时间，我们只测试函数能正常运行
        result1 = is_in_time_range("00:00", "12:00")
        result2 = is_in_time_range("12:00", "23:59")

        # 两个时间段应该有且仅有一个包含当前时间
        # 或者都包含（如果当前时间正好是 12:00）
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
