"""
关键词匹配模块

负责关键词匹配、权重计算和词频统计
"""

from typing import Dict, List, Optional, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)


def calculate_news_weight(
    title_data: Dict, rank_threshold: int = 5, weight_config: Optional[Dict] = None
) -> float:
    """计算新闻权重，用于排序

    Args:
        title_data: 标题数据，包含 ranks, count 等
        rank_threshold: 排名高亮阈值
        weight_config: 权重配置 {RANK_WEIGHT, FREQUENCY_WEIGHT, HOTNESS_WEIGHT}

    Returns:
        计算出的权重值
    """
    if weight_config is None:
        weight_config = {
            "RANK_WEIGHT": 0.6,
            "FREQUENCY_WEIGHT": 0.3,
            "HOTNESS_WEIGHT": 0.1,
        }

    ranks = title_data.get("ranks", [])
    if not ranks:
        return 0.0

    count = title_data.get("count", len(ranks))

    # 排名权重：Σ(11 - min(rank, 10)) / 出现次数
    rank_scores = []
    for rank in ranks:
        score = 11 - min(rank, 10)
        rank_scores.append(score)

    rank_weight = sum(rank_scores) / len(ranks) if ranks else 0

    # 频次权重：min(出现次数, 10) × 10
    frequency_weight = min(count, 10) * 10

    # 热度加成：高排名次数 / 总出现次数 × 100
    high_rank_count = sum(1 for rank in ranks if rank <= rank_threshold)
    hotness_ratio = high_rank_count / len(ranks) if ranks else 0
    hotness_weight = hotness_ratio * 100

    total_weight = (
        rank_weight * weight_config["RANK_WEIGHT"]
        + frequency_weight * weight_config["FREQUENCY_WEIGHT"]
        + hotness_weight * weight_config["HOTNESS_WEIGHT"]
    )

    return total_weight


def matches_word_groups(
    title: str, word_groups: List[Dict], filter_words: List[str]
) -> bool:
    """检查标题是否匹配词组规则

    Args:
        title: 标题文本
        word_groups: 词组列表，每个词组包含 required, normal 字段
        filter_words: 过滤词列表

    Returns:
        是否匹配
    """
    # 如果没有配置词组，则匹配所有标题（支持显示全部新闻）
    if not word_groups:
        return True

    title_lower = title.lower()

    # 过滤词检查
    if any(filter_word.lower() in title_lower for filter_word in filter_words):
        return False

    # 词组匹配检查
    for group in word_groups:
        required_words = group.get("required", [])
        normal_words = group.get("normal", [])

        # 必须词检查
        if required_words:
            all_required_present = all(
                req_word.lower() in title_lower for req_word in required_words
            )
            if not all_required_present:
                continue

        # 普通词检查
        if normal_words:
            any_normal_present = any(
                normal_word.lower() in title_lower for normal_word in normal_words
            )
            if not any_normal_present:
                continue

        return True

    return False


def format_rank_display(ranks: List[int], rank_threshold: int, format_type: str) -> str:
    """统一的排名格式化方法

    Args:
        ranks: 排名列表
        rank_threshold: 高排名阈值
        format_type: 格式类型 (html/feishu/dingtalk/wework/telegram)

    Returns:
        格式化后的排名显示
    """
    if not ranks:
        return ""

    unique_ranks = sorted(set(ranks))
    min_rank = unique_ranks[0]
    max_rank = unique_ranks[-1]

    # 根据格式类型选择高亮标记
    if format_type == "html":
        highlight_start = "<font color='red'><strong>"
        highlight_end = "</strong></font>"
    elif format_type == "feishu":
        highlight_start = "<font color='red'>**"
        highlight_end = "**</font>"
    elif format_type == "dingtalk":
        highlight_start = "**"
        highlight_end = "**"
    elif format_type == "wework":
        highlight_start = "**"
        highlight_end = "**"
    elif format_type == "telegram":
        highlight_start = "<b>"
        highlight_end = "</b>"
    else:
        highlight_start = "**"
        highlight_end = "**"

    # 高排名高亮显示
    if min_rank <= rank_threshold:
        if min_rank == max_rank:
            return f"{highlight_start}[{min_rank}]{highlight_end}"
        else:
            return f"{highlight_start}[{min_rank} - {max_rank}]{highlight_end}"
    else:
        if min_rank == max_rank:
            return f"[{min_rank}]"
        else:
            return f"[{min_rank} - {max_rank}]"


def count_word_frequency(
    results: Dict,
    word_groups: List[Dict],
    filter_words: List[str],
    id_to_name: Dict,
    title_info: Optional[Dict] = None,
    rank_threshold: int = 5,
    weight_config: Optional[Dict] = None,
) -> List[Dict]:
    """统计词频并返回匹配的新闻列表

    Args:
        results: 标题数据 {platform_id: {title: data}}
        word_groups: 词组列表
        filter_words: 过滤词列表
        id_to_name: 平台ID到名称的映射
        title_info: 标题详细信息
        rank_threshold: 排名高亮阈值
        weight_config: 权重配置

    Returns:
        匹配的新闻列表，按权重排序
    """
    if title_info is None:
        title_info = {}

    # 如果没有配置词组，创建一个包含所有新闻的虚拟词组
    if not word_groups:
        logger.info("频率词配置为空，将显示所有新闻")
        word_groups = [{"required": [], "normal": [], "group_key": "全部新闻"}]
        filter_words = []  # 清空过滤词，显示所有新闻

    matched_news = []

    for source_id, titles_data in results.items():
        source_name = id_to_name.get(source_id, source_id)

        for title, data in titles_data.items():
            # 检查是否匹配词组
            if matches_word_groups(title, word_groups, filter_words):
                # 获取标题详细信息
                info = {}
                if source_id in title_info and title in title_info[source_id]:
                    info = title_info[source_id][title]
                else:
                    # 使用基础数据
                    info = {
                        "ranks": data.get("ranks", []),
                        "count": 1,
                        "url": data.get("url", ""),
                        "mobileUrl": data.get("mobileUrl", ""),
                    }

                # 计算权重
                weight = calculate_news_weight(
                    info, rank_threshold=rank_threshold, weight_config=weight_config
                )

                matched_news.append(
                    {
                        "title": title,
                        "source_id": source_id,
                        "source_name": source_name,
                        "ranks": info.get("ranks", []),
                        "count": info.get("count", 1),
                        "first_time": info.get("first_time", ""),
                        "last_time": info.get("last_time", ""),
                        "url": info.get("url", ""),
                        "mobileUrl": info.get("mobileUrl", ""),
                        "weight": weight,
                    }
                )

    # 按权重排序（降序）
    matched_news.sort(key=lambda x: x["weight"], reverse=True)

    logger.info(f"匹配到 {len(matched_news)} 条新闻")
    return matched_news
