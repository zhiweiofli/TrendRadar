"""
核心业务逻辑模块
"""

from .analyzer import (
    calculate_statistics,
    detect_latest_new_titles,
    process_source_data,
)
from .fetcher import DataFetcher
from .matcher import (
    calculate_news_weight,
    count_word_frequency,
    format_rank_display,
    matches_word_groups,
)
from .reporter import generate_html_report, prepare_report_data, render_html_content
from .storage import parse_file_titles, read_all_today_titles, save_titles_to_file

__all__ = [
    # fetcher
    "DataFetcher",
    # storage
    "save_titles_to_file",
    "parse_file_titles",
    "read_all_today_titles",
    # analyzer
    "process_source_data",
    "detect_latest_new_titles",
    "calculate_statistics",
    # matcher
    "calculate_news_weight",
    "matches_word_groups",
    "format_rank_display",
    "count_word_frequency",
    # reporter
    "prepare_report_data",
    "generate_html_report",
    "render_html_content",
]
