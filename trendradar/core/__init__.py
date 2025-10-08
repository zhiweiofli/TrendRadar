"""
核心业务逻辑模块
"""

from .fetcher import DataFetcher
from .storage import (
    save_titles_to_file,
    parse_file_titles,
    read_all_today_titles,
)
from .analyzer import (
    process_source_data,
    detect_latest_new_titles,
    calculate_statistics,
)
from .matcher import (
    calculate_news_weight,
    matches_word_groups,
    format_rank_display,
    count_word_frequency,
)
from .reporter import (
    prepare_report_data,
    generate_html_report,
    render_html_content,
)

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

