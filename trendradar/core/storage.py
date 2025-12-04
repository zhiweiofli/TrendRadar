"""
数据存储模块

负责数据的保存、读取和解析
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.file_utils import clean_title, get_output_path
from ..utils.logger import get_logger
from ..utils.time_utils import format_date_folder, format_time_filename

logger = get_logger(__name__)


def save_titles_to_file(results: Dict, id_to_name: Dict, failed_ids: List[str]) -> str:
    """保存标题到文件

    Args:
        results: 标题数据字典 {platform_id: {title: info}}
        id_to_name: 平台ID到名称的映射
        failed_ids: 失败的平台ID列表

    Returns:
        保存的文件路径
    """
    file_path = get_output_path("txt", f"{format_time_filename()}.txt")
    logger.info(f"保存标题到文件: {file_path}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for id_value, title_data in results.items():
                # 写入平台标识：id | name 或 id
                name = id_to_name.get(id_value)
                if name and name != id_value:
                    f.write(f"{id_value} | {name}\n")
                else:
                    f.write(f"{id_value}\n")

                # 按排名排序标题
                sorted_titles = []
                for title, info in title_data.items():
                    cleaned_title = clean_title(title)
                    if isinstance(info, dict):
                        ranks = info.get("ranks", [])
                        url = info.get("url", "")
                        mobile_url = info.get("mobileUrl", "")
                    else:
                        ranks = info if isinstance(info, list) else []
                        url = ""
                        mobile_url = ""

                    rank = ranks[0] if ranks else 1
                    sorted_titles.append((rank, cleaned_title, url, mobile_url))

                sorted_titles.sort(key=lambda x: x[0])

                # 写入每条标题
                for rank, cleaned_title, url, mobile_url in sorted_titles:
                    line = f"{rank}. {cleaned_title}"

                    if url:
                        line += f" [URL:{url}]"
                    if mobile_url:
                        line += f" [MOBILE:{mobile_url}]"
                    f.write(line + "\n")

                f.write("\n")

            # 写入失败的ID
            if failed_ids:
                f.write("==== 以下ID请求失败 ====\n")
                for id_value in failed_ids:
                    f.write(f"{id_value}\n")

        logger.info(f"成功保存 {len(results)} 个平台的数据")
        return file_path

    except Exception as e:
        logger.error(f"保存文件失败: {e}", exc_info=True)
        raise


def parse_file_titles(file_path: Path) -> Tuple[Dict, Dict]:
    """解析单个txt文件的标题数据

    Args:
        file_path: 文件路径

    Returns:
        (titles_by_id, id_to_name) 元组
        - titles_by_id: {platform_id: {title: info}}
        - id_to_name: {platform_id: name}
    """
    titles_by_id = {}
    id_to_name = {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            sections = content.split("\n\n")

            for section in sections:
                if not section.strip() or "==== 以下ID请求失败 ====" in section:
                    continue

                lines = section.strip().split("\n")
                if len(lines) < 2:
                    continue

                # 解析平台标识：id | name 或 id
                header_line = lines[0].strip()
                if " | " in header_line:
                    parts = header_line.split(" | ", 1)
                    source_id = parts[0].strip()
                    name = parts[1].strip()
                    id_to_name[source_id] = name
                else:
                    source_id = header_line
                    id_to_name[source_id] = source_id

                titles_by_id[source_id] = {}

                # 解析每条标题
                for line in lines[1:]:
                    if line.strip():
                        try:
                            title_part = line.strip()
                            rank = None

                            # 提取排名
                            if (
                                ". " in title_part
                                and title_part.split(". ")[0].isdigit()
                            ):
                                rank_str, title_part = title_part.split(". ", 1)
                                rank = int(rank_str)

                            # 提取 MOBILE URL
                            mobile_url = ""
                            if " [MOBILE:" in title_part:
                                title_part, mobile_part = title_part.rsplit(
                                    " [MOBILE:", 1
                                )
                                if mobile_part.endswith("]"):
                                    mobile_url = mobile_part[:-1]

                            # 提取 URL
                            url = ""
                            if " [URL:" in title_part:
                                title_part, url_part = title_part.rsplit(" [URL:", 1)
                                if url_part.endswith("]"):
                                    url = url_part[:-1]

                            title = clean_title(title_part.strip())
                            ranks = [rank] if rank is not None else [1]

                            titles_by_id[source_id][title] = {
                                "ranks": ranks,
                                "url": url,
                                "mobileUrl": mobile_url,
                            }

                        except Exception as e:
                            logger.warning(f"解析标题行出错: {line}, 错误: {e}")

        logger.debug(f"解析文件 {file_path.name}: {len(titles_by_id)} 个平台")
        return titles_by_id, id_to_name

    except Exception as e:
        logger.error(f"读取文件失败: {file_path}, 错误: {e}")
        return {}, {}


def read_all_today_titles(
    current_platform_ids: Optional[List[str]] = None,
) -> Tuple[Dict, Dict, Dict]:
    """读取当天所有标题文件

    Args:
        current_platform_ids: 当前监控的平台ID列表，None表示不过滤

    Returns:
        (all_results, final_id_to_name, title_info) 元组
        - all_results: 合并后的所有标题数据
        - final_id_to_name: 平台ID到名称的映射
        - title_info: 标题的详细信息（时间、来源等）
    """
    from .analyzer import process_source_data  # 避免循环导入

    date_folder = format_date_folder()
    txt_dir = Path("output") / date_folder / "txt"

    if not txt_dir.exists():
        logger.warning(f"当日目录不存在: {txt_dir}")
        return {}, {}, {}

    all_results = {}
    final_id_to_name = {}
    title_info = {}

    files = sorted([f for f in txt_dir.iterdir() if f.suffix == ".txt"])
    logger.info(f"读取当日文件: {len(files)} 个")

    for file_path in files:
        time_info = file_path.stem

        titles_by_id, file_id_to_name = parse_file_titles(file_path)

        # 按平台ID过滤
        if current_platform_ids is not None:
            filtered_titles_by_id = {}
            filtered_id_to_name = {}

            for source_id, title_data in titles_by_id.items():
                if source_id in current_platform_ids:
                    filtered_titles_by_id[source_id] = title_data
                    if source_id in file_id_to_name:
                        filtered_id_to_name[source_id] = file_id_to_name[source_id]

            titles_by_id = filtered_titles_by_id
            file_id_to_name = filtered_id_to_name

        final_id_to_name.update(file_id_to_name)

        # 处理每个平台的数据
        for source_id, title_data in titles_by_id.items():
            process_source_data(
                source_id, title_data, time_info, all_results, title_info
            )

    logger.info(
        f"读取完成: {len(all_results)} 个平台, {sum(len(v) for v in all_results.values())} 条标题"
    )
    return all_results, final_id_to_name, title_info
