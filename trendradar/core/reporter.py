"""
HTML 报告生成模块

提供 HTML 报告的准备、渲染和生成功能
"""
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.file_utils import get_output_path, clean_title, html_escape
from ..utils.time_utils import get_beijing_time, format_time_filename
from ..utils.logger import get_logger
from ..utils.config import load_frequency_words, load_config
from .matcher import format_rank_display, matches_word_groups

logger = get_logger(__name__)

# 加载全局配置（用于报告生成）
_config = load_config()


def prepare_report_data(
    stats: List[Dict],
    failed_ids: Optional[List] = None,
    new_titles: Optional[Dict] = None,
    id_to_name: Optional[Dict] = None,
    mode: str = "daily",
) -> Dict:
    """准备报告数据
    
    Args:
        stats: 统计数据列表
        failed_ids: 失败的平台ID列表
        new_titles: 新增标题字典
        id_to_name: ID到名称的映射
        mode: 报告模式
    
    Returns:
        包含处理后数据的字典
    """
    processed_new_titles = []

    # 在增量模式下隐藏新增新闻区域
    hide_new_section = mode == "incremental"

    # 只有在非隐藏模式下才处理新增新闻部分
    if not hide_new_section:
        filtered_new_titles = {}
        if new_titles and id_to_name:
            word_groups, filter_words = load_frequency_words()
            for source_id, titles_data in new_titles.items():
                filtered_titles = {}
                for title, title_data in titles_data.items():
                    if matches_word_groups(title, word_groups, filter_words):
                        filtered_titles[title] = title_data
                if filtered_titles:
                    filtered_new_titles[source_id] = filtered_titles

        if filtered_new_titles and id_to_name:
            for source_id, titles_data in filtered_new_titles.items():
                source_name = id_to_name.get(source_id, source_id)
                source_titles = []

                for title, title_data in titles_data.items():
                    url = title_data.get("url", "")
                    mobile_url = title_data.get("mobileUrl", "")
                    ranks = title_data.get("ranks", [])

                    processed_title = {
                        "title": title,
                        "source_name": source_name,
                        "time_display": "",
                        "count": 1,
                        "ranks": ranks,
                        "rank_threshold": _config.get("RANK_THRESHOLD", 10),
                        "url": url,
                        "mobile_url": mobile_url,
                        "is_new": True,
                    }
                    source_titles.append(processed_title)

                if source_titles:
                    processed_new_titles.append(
                        {
                            "source_id": source_id,
                            "source_name": source_name,
                            "titles": source_titles,
                        }
                    )

    processed_stats = []
    for stat in stats:
        if stat["count"] <= 0:
            continue

        processed_titles = []
        for title_data in stat["titles"]:
            # 计算时间显示
            first_time = title_data.get("first_time", "")
            last_time = title_data.get("last_time", "")
            
            if first_time and last_time:
                if first_time == last_time:
                    time_display = first_time
                else:
                    time_display = f"{first_time}～{last_time}"
            else:
                time_display = ""
            
            processed_title = {
                "title": title_data.get("title", ""),
                "source_name": title_data.get("source_name", title_data.get("platform_name", "")),
                "time_display": time_display,
                "count": title_data.get("count", 1),
                "ranks": title_data.get("ranks", []),
                "rank_threshold": 10,  # 默认阈值
                "url": title_data.get("url", ""),
                "mobile_url": title_data.get("mobileUrl", ""),
                "is_new": title_data.get("is_new", False),
            }
            processed_titles.append(processed_title)

        processed_stats.append(
            {
                "word": stat["word"],
                "count": stat["count"],
                "percentage": stat.get("percentage", 0),
                "titles": processed_titles,
            }
        )

    return {
        "stats": processed_stats,
        "new_titles": processed_new_titles,
        "failed_ids": failed_ids or [],
        "total_new_count": sum(
            len(source["titles"]) for source in processed_new_titles
        ),
    }


def generate_html_report(
    stats: List[Dict],
    total_titles: int,
    failed_ids: Optional[List] = None,
    new_titles: Optional[Dict] = None,
    id_to_name: Optional[Dict] = None,
    mode: str = "daily",
    is_daily_summary: bool = False,
) -> str:
    """生成HTML报告
    
    Args:
        stats: 统计数据列表
        total_titles: 总标题数
        failed_ids: 失败的平台ID列表
        new_titles: 新增标题字典
        id_to_name: ID到名称的映射
        mode: 报告模式
        is_daily_summary: 是否为当日汇总
    
    Returns:
        HTML文件路径
    """
    if is_daily_summary:
        if mode == "test":
            filename = "测试报告.html"
        elif mode == "current":
            filename = "当前榜单汇总.html"
        elif mode == "incremental":
            filename = "当日增量.html"
        else:
            filename = "当日汇总.html"
    else:
        filename = f"{format_time_filename()}.html"

    file_path = get_output_path("html", filename)

    report_data = prepare_report_data(stats, failed_ids, new_titles, id_to_name, mode)

    html_content = render_html_content(
        report_data, total_titles, is_daily_summary, mode
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if is_daily_summary:
        root_file_path = Path("index.html")
        with open(root_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    logger.info(f"HTML报告已生成: {file_path}")
    return file_path


def render_html_content(
    report_data: Dict,
    total_titles: int,
    is_daily_summary: bool = False,
    mode: str = "daily",
) -> str:
    """渲染HTML内容
    
    Args:
        report_data: 报告数据
        total_titles: 总标题数
        is_daily_summary: 是否为当日汇总
        mode: 报告模式
    
    Returns:
        HTML字符串
    """
    # 由于 HTML 模板非常长（~800行），保持在 main.py 的实现
    # 这里暂时重用 main.py 的实现
    # TODO: 后续可以考虑使用模板引擎（如 Jinja2）来管理 HTML
    
    from pathlib import Path
    import sys
    
    # 临时导入 main.py 的 render_html_content
    # 这是一个过渡方案，避免直接复制 800 行 HTML 模板代码
    main_backup_path = Path(__file__).parent.parent.parent / "main_v2.2.0_backup.py"
    
    if main_backup_path.exists():
        # 动态导入 main_v2.2.0_backup.py 的 render_html_content
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_backup", main_backup_path)
        main_backup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_backup)
        
        return main_backup.render_html_content(report_data, total_titles, is_daily_summary, mode)
    else:
        # 如果备份不存在，使用简化版 HTML
        logger.warning("main_v2.2.0_backup.py 不存在，使用简化版 HTML")
        return _render_simple_html(report_data, total_titles, mode)


def _render_simple_html(
    report_data: Dict,
    total_titles: int,
    mode: str = "daily"
) -> str:
    """渲染简化版 HTML（备用方案）"""
    now = get_beijing_time()
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrendRadar - 热点新闻分析</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5; 
        }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 2px solid #4f46e5; padding-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-item {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat-label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
        .stat-value {{ font-size: 24px; font-weight: 600; color: #4f46e5; }}
        .word-group {{ margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 6px; }}
        .word-header {{ font-size: 18px; font-weight: 600; color: #333; margin-bottom: 15px; }}
        .news-item {{ margin: 10px 0; padding: 10px; border-left: 3px solid #4f46e5; background: #f8f9fa; }}
        .news-title {{ font-size: 14px; color: #333; }}
        .news-meta {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 TrendRadar 热点新闻分析</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">报告类型</div>
                <div class="stat-value">{mode}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">新闻总数</div>
                <div class="stat-value">{total_titles}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">生成时间</div>
                <div class="stat-value">{now.strftime("%H:%M")}</div>
            </div>
        </div>
'''
    
    # 添加统计数据
    if report_data.get("stats"):
        for i, stat in enumerate(report_data["stats"], 1):
            word = html_escape(stat["word"])
            count = stat["count"]
            
            html += f'''
        <div class="word-group">
            <div class="word-header">{i}. {word} ({count} 条)</div>
'''
            
            for j, title_data in enumerate(stat["titles"][:10], 1):  # 只显示前10条
                title = html_escape(title_data["title"])
                source = html_escape(title_data["source_name"])
                
                html += f'''
            <div class="news-item">
                <div class="news-title">{j}. {title}</div>
                <div class="news-meta">来源: {source}</div>
            </div>
'''
            
            html += '        </div>\n'
    
    html += f'''
        <div class="footer">
            <p>由 TrendRadar v3.0 生成 · {now.strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><a href="https://github.com/sansan0/TrendRadar" target="_blank">GitHub 开源项目</a></p>
        </div>
    </div>
</body>
</html>'''
    
    return html

