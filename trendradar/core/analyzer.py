"""
数据分析模块

负责数据的处理、分析和统计
"""

from pathlib import Path
from typing import Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.time_utils import format_date_folder

logger = get_logger(__name__)


def process_source_data(
    source_id: str,
    title_data: Dict,
    time_info: str,
    all_results: Dict,
    title_info: Dict,
) -> None:
    """处理来源数据，合并重复标题

    Args:
        source_id: 平台ID
        title_data: 标题数据
        time_info: 时间信息
        all_results: 累计结果（会被修改）
        title_info: 标题详细信息（会被修改）
    """
    if source_id not in all_results:
        # 首次出现的平台
        all_results[source_id] = title_data

        if source_id not in title_info:
            title_info[source_id] = {}

        for title, data in title_data.items():
            ranks = data.get("ranks", [])
            url = data.get("url", "")
            mobile_url = data.get("mobileUrl", "")

            title_info[source_id][title] = {
                "first_time": time_info,
                "last_time": time_info,
                "count": 1,
                "ranks": ranks,
                "url": url,
                "mobileUrl": mobile_url,
            }
    else:
        # 已存在的平台，合并数据
        for title, data in title_data.items():
            ranks = data.get("ranks", [])
            url = data.get("url", "")
            mobile_url = data.get("mobileUrl", "")

            if title not in all_results[source_id]:
                # 新标题
                all_results[source_id][title] = {
                    "ranks": ranks,
                    "url": url,
                    "mobileUrl": mobile_url,
                }
                title_info[source_id][title] = {
                    "first_time": time_info,
                    "last_time": time_info,
                    "count": 1,
                    "ranks": ranks,
                    "url": url,
                    "mobileUrl": mobile_url,
                }
            else:
                # 已存在的标题，合并排名
                existing_data = all_results[source_id][title]
                existing_ranks = existing_data.get("ranks", [])
                existing_url = existing_data.get("url", "")
                existing_mobile_url = existing_data.get("mobileUrl", "")

                # 合并排名
                merged_ranks = existing_ranks.copy()
                for rank in ranks:
                    if rank not in merged_ranks:
                        merged_ranks.append(rank)

                all_results[source_id][title] = {
                    "ranks": merged_ranks,
                    "url": existing_url or url,
                    "mobileUrl": existing_mobile_url or mobile_url,
                }

                # 更新标题信息
                title_info[source_id][title]["last_time"] = time_info
                title_info[source_id][title]["ranks"] = merged_ranks
                title_info[source_id][title]["count"] += 1
                if not title_info[source_id][title].get("url"):
                    title_info[source_id][title]["url"] = url
                if not title_info[source_id][title].get("mobileUrl"):
                    title_info[source_id][title]["mobileUrl"] = mobile_url


def detect_latest_new_titles(current_platform_ids: Optional[List[str]] = None) -> Dict:
    """检测当日最新批次的新增标题

    Args:
        current_platform_ids: 当前监控的平台ID列表，None表示不过滤

    Returns:
        新增标题字典 {platform_id: {title: data}}
    """
    from .storage import parse_file_titles  # 避免循环导入

    date_folder = format_date_folder()
    txt_dir = Path("output") / date_folder / "txt"

    if not txt_dir.exists():
        logger.warning(f"当日目录不存在: {txt_dir}")
        return {}

    files = sorted([f for f in txt_dir.iterdir() if f.suffix == ".txt"])
    if len(files) < 2:
        logger.info("文件数量不足，无法检测新增")
        return {}

    # 解析最新文件
    latest_file = files[-1]
    logger.info(f"检测新增: 最新文件 {latest_file.name}")
    latest_titles, _ = parse_file_titles(latest_file)

    # 如果指定了当前平台列表，过滤最新文件数据
    if current_platform_ids is not None:
        filtered_latest_titles = {}
        for source_id, title_data in latest_titles.items():
            if source_id in current_platform_ids:
                filtered_latest_titles[source_id] = title_data
        latest_titles = filtered_latest_titles

    # 汇总历史标题（按平台过滤）
    historical_titles = {}
    for file_path in files[:-1]:
        historical_data, _ = parse_file_titles(file_path)

        # 过滤历史数据
        if current_platform_ids is not None:
            filtered_historical_data = {}
            for source_id, title_data in historical_data.items():
                if source_id in current_platform_ids:
                    filtered_historical_data[source_id] = title_data
            historical_data = filtered_historical_data

        for source_id, titles_data in historical_data.items():
            if source_id not in historical_titles:
                historical_titles[source_id] = set()
            for title in titles_data.keys():
                historical_titles[source_id].add(title)

    # 找出新增标题
    new_titles = {}
    total_new = 0
    for source_id, latest_source_titles in latest_titles.items():
        historical_set = historical_titles.get(source_id, set())
        source_new_titles = {}

        for title, title_data in latest_source_titles.items():
            if title not in historical_set:
                source_new_titles[title] = title_data

        if source_new_titles:
            new_titles[source_id] = source_new_titles
            total_new += len(source_new_titles)

    logger.info(f"检测到 {total_new} 条新增标题")
    return new_titles


def calculate_statistics(all_results: Dict, title_info: Dict) -> Dict:
    """计算统计信息

    Args:
        all_results: 所有标题数据
        title_info: 标题详细信息

    Returns:
        统计信息字典
    """
    total_platforms = len(all_results)
    total_titles = sum(len(titles) for titles in all_results.values())

    # 计算每个平台的标题数
    platform_counts = {}
    for platform_id, titles in all_results.items():
        platform_counts[platform_id] = len(titles)

    # 计算出现频率最高的标题
    title_frequencies = {}
    for platform_id in all_results:
        if platform_id in title_info:
            for title, info in title_info[platform_id].items():
                count = info.get("count", 1)
                if count > 1:
                    if title not in title_frequencies:
                        title_frequencies[title] = 0
                    title_frequencies[title] += count

    stats = {
        "total_platforms": total_platforms,
        "total_titles": total_titles,
        "platform_counts": platform_counts,
        "frequent_titles": title_frequencies,
    }

    logger.info(f"统计完成: {total_platforms} 个平台, {total_titles} 条标题")
    return stats
