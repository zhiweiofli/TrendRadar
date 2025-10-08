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
    now = get_beijing_time()
    
    # 获取标题和时间
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    if mode == "test":
        title = "🧪 测试报告"
        subtitle = time_str
    elif mode == "current":
        title = "📊 当前榜单汇总"
        subtitle = time_str
    elif mode == "incremental":
        title = "🆕 当日新增"
        subtitle = time_str
    else:
        title = "📊 当日汇总"
        subtitle = time_str
    
    test_mode_class = "test-mode" if mode == "test" else ""
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点新闻分析</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" integrity="sha512-BNaRQnYJYiPSqHHDb58B0yaPfCu+Wgds8Gp/gU33kqBtgNS4tSPHuGibyoeqMV/TJlSKda6FXzoEyYGjTe+vXA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            margin: 0; 
            padding: 16px; 
            background: #fafafa;
            color: #333;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        }}
        
        .header {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 32px 24px;
            text-align: center;
            position: relative;
        }}
        
        .header.test-mode {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .save-btn {{
            position: absolute;
            top: 16px;
            right: 16px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .save-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.4);
        }}
        
        .title {{
            font-size: 24px;
            font-weight: 700;
            margin: 0 0 8px;
        }}
        
        .subtitle {{
            font-size: 14px;
            opacity: 0.95;
            margin: 0;
        }}
        
        .content {{
            padding: 24px;
        }}
        
        .section {{
            margin-bottom: 32px;
        }}
        
        .section:last-child {{
            margin-bottom: 0;
        }}
        
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            margin: 0 0 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .section-count {{
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }}
        
        .news-item {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }}
        
        .news-item:hover {{
            background: #f3f4f6;
            border-color: #e5e7eb;
            transform: translateY(-1px);
        }}
        
        .news-item:last-child {{
            margin-bottom: 0;
        }}
        
        .news-title {{
            font-size: 15px;
            font-weight: 500;
            color: #1f2937;
            margin: 0 0 8px;
            line-height: 1.5;
        }}
        
        .news-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .news-title a:hover {{
            color: #4f46e5;
        }}
        
        .news-meta {{
            font-size: 13px;
            color: #6b7280;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .rank-list {{
            display: inline-flex;
            flex-wrap: wrap;
            gap: 4px;
        }}
        
        .rank {{
            display: inline-block;
            background: #e0e7ff;
            color: #4338ca;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .rank.hot {{
            background: #fef2f2;
            color: #dc2626;
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .badge.new {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .badge.multiple {{
            background: #dbeafe;
            color: #2563eb;
        }}
        
        .source-group {{
            margin-bottom: 24px;
        }}
        
        .source-title {{
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin: 0 0 12px;
            padding-left: 12px;
            border-left: 3px solid #4f46e5;
        }}
        
        .empty {{
            text-align: center;
            padding: 48px 24px;
            color: #9ca3af;
        }}
        
        .empty-icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}
        
        .empty-text {{
            font-size: 14px;
        }}
        
        .stats {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .stat-row:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6b7280;
        }}
        
        .stat-value {{
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
        }}
        
        @media (max-width: 600px) {{
            body {{
                padding: 8px;
            }}
            
            .container {{
                border-radius: 8px;
            }}
            
            .header {{
                padding: 24px 16px;
            }}
            
            .title {{
                font-size: 20px;
            }}
            
            .content {{
                padding: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header {test_mode_class}">
            <button class="save-btn" onclick="saveAsImage()">保存为图片</button>
            <h1 class="title">{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        
        <div class="content" id="content">
'''
    
    # 统计信息
    total_matched = sum(len(stat.get("titles", [])) for stat in report_data.get("stats", []))
    total_new = sum(len(source.get("titles", [])) for source in report_data.get("new_titles", []))
    
    html += f'''
            <div class="stats">
                <div class="stat-row">
                    <span class="stat-label">📊 总标题数</span>
                    <span class="stat-value">{total_titles}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">🎯 匹配新闻</span>
                    <span class="stat-value">{total_matched}</span>
                </div>
'''
    
    if not report_data.get("hide_new_section", False):
        html += f'''
                <div class="stat-row">
                    <span class="stat-label">🆕 新增新闻</span>
                    <span class="stat-value">{total_new}</span>
                </div>
'''
    
    html += '''
            </div>
'''
    
    # 匹配的新闻
    if report_data.get("stats"):
        for stat in report_data["stats"]:
            word = stat.get("word", "未分类")
            titles = stat.get("titles", [])
            count = len(titles)
            
            html += f'''
            <div class="section">
                <div class="section-title">
                    <span>🔥 {word}</span>
                    <span class="section-count">{count} 条</span>
                </div>
'''
            
            for title_data in titles:
                title = title_data.get("title", "")
                source = title_data.get("source_name", "")
                time_display = title_data.get("time_display", "")
                url = title_data.get("url", "")
                ranks = title_data.get("ranks", [])
                count = title_data.get("count", 1)
                is_new = title_data.get("is_new", False)
                rank_threshold = title_data.get("rank_threshold", 10)
                
                # 生成排名列表
                rank_html = ""
                if ranks:
                    rank_html = '<div class="rank-list">'
                    for rank in ranks[:5]:  # 最多显示5个排名
                        rank_class = "rank hot" if rank <= rank_threshold else "rank"
                        rank_html += f'<span class="{rank_class}">{rank}</span>'
                    if len(ranks) > 5:
                        rank_html += f'<span class="rank">+{len(ranks)-5}</span>'
                    rank_html += '</div>'
                
                # 生成标题链接
                if url:
                    title_html = f'<a href="{url}" target="_blank">{title}</a>'
                else:
                    title_html = title
                
                html += f'''
                <div class="news-item">
                    <div class="news-title">{title_html}</div>
                    <div class="news-meta">
                        <span class="meta-item">📰 {source}</span>
'''
                
                if time_display:
                    html += f'                        <span class="meta-item">⏰ {time_display}</span>\n'
                
                if rank_html:
                    html += f'                        <span class="meta-item">{rank_html}</span>\n'
                
                if count > 1:
                    html += f'                        <span class="badge multiple">出现 {count} 次</span>\n'
                
                if is_new:
                    html += '                        <span class="badge new">NEW</span>\n'
                
                html += '''
                    </div>
                </div>
'''
            
            html += '''
            </div>
'''
    else:
        html += '''
            <div class="empty">
                <div class="empty-icon">📭</div>
                <div class="empty-text">暂无匹配的新闻</div>
            </div>
'''
    
    # 新增新闻
    if not report_data.get("hide_new_section", False) and report_data.get("new_titles"):
        html += '''
            <div class="section">
                <div class="section-title">
                    <span>🆕 新增新闻</span>
                </div>
'''
        
        for source in report_data["new_titles"]:
            source_name = source.get("source_name", "")
            titles = source.get("titles", [])
            
            if titles:
                html += f'''
                <div class="source-group">
                    <div class="source-title">{source_name}</div>
'''
                
                for title_data in titles:
                    title = title_data.get("title", "")
                    url = title_data.get("url", "")
                    ranks = title_data.get("ranks", [])
                    rank_threshold = title_data.get("rank_threshold", 10)
                    
                    # 生成排名
                    rank_html = ""
                    if ranks:
                        rank_html = '<div class="rank-list">'
                        for rank in ranks[:5]:
                            rank_class = "rank hot" if rank <= rank_threshold else "rank"
                            rank_html += f'<span class="{rank_class}">{rank}</span>'
                        rank_html += '</div>'
                    
                    # 生成标题链接
                    if url:
                        title_html = f'<a href="{url}" target="_blank">{title}</a>'
                    else:
                        title_html = title
                    
                    html += f'''
                    <div class="news-item">
                        <div class="news-title">{title_html}</div>
                        <div class="news-meta">
                            <span class="meta-item">📰 {source_name}</span>
'''
                    
                    if rank_html:
                        html += f'                            <span class="meta-item">{rank_html}</span>\n'
                    
                    html += '''
                            <span class="badge new">NEW</span>
                        </div>
                    </div>
'''
                
                html += '''
                </div>
'''
        
        html += '''
            </div>
'''
    
    html += '''
        </div>
    </div>
    
    <script>
        function saveAsImage() {
            const content = document.getElementById('content');
            const button = document.querySelector('.save-btn');
            
            button.textContent = '生成中...';
            button.disabled = true;
            
            html2canvas(content, {
                backgroundColor: '#ffffff',
                scale: 2,
                logging: false,
            }).then(canvas => {
                const link = document.createElement('a');
                link.download = '热点新闻_' + new Date().getTime() + '.png';
                link.href = canvas.toDataURL();
                link.click();
                
                button.textContent = '保存为图片';
                button.disabled = false;
            }).catch(error => {
                console.error('生成图片失败:', error);
                button.textContent = '保存失败';
                setTimeout(() => {
                    button.textContent = '保存为图片';
                    button.disabled = false;
                }, 2000);
            });
        }}
    </script>
</body>
</html>
'''
    
    return html


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

