"""
TrendRadar v3.0 模块测试脚本

测试新重构的模块功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from trendradar.core import (
    DataFetcher,
    count_word_frequency,
    detect_latest_new_titles,
    read_all_today_titles,
    save_titles_to_file,
)
from trendradar.utils import (
    ConfigValidator,
    init_app_logger,
    load_config,
    load_frequency_words,
)


def main():
    """主测试流程"""
    # 1. 初始化日志
    logger = init_app_logger(log_level="INFO", enable_file_log=True)
    logger.info("=" * 70)
    logger.info("TrendRadar v3.0 模块功能测试")
    logger.info("=" * 70)

    try:
        # 2. 加载并验证配置
        logger.info("\n[步骤 1] 加载配置文件...")
        config = load_config()

        logger.info("[步骤 2] 验证配置...")
        validator = ConfigValidator()
        validator.validate(config)
        logger.info("✅ 配置验证通过")

        # 3. 加载关键词 (使用 main.py 中的原始实现)
        logger.info("\n[步骤 3] 加载关键词配置...")
        # 暂时跳过关键词加载（需要使用 main.py 的实现）
        word_groups = []
        filter_words = []
        logger.info(f"⚠️  暂时跳过关键词加载（待 main.py 完全集成）")

        # 4. 创建数据抓取器
        logger.info("\n[步骤 4] 初始化数据抓取器...")
        fetcher = DataFetcher(
            config=config,
            proxy_url=config.get("DEFAULT_PROXY") if config.get("USE_PROXY") else None,
        )
        logger.info(f"✅ 将抓取 {len(fetcher.platforms)} 个平台")

        # 5. 抓取数据
        logger.info("\n[步骤 5] 开始抓取数据...")
        use_async = config.get("ENABLE_ASYNC", True)
        results, failed = fetcher.fetch_all(use_async=use_async)
        logger.info(f"✅ 抓取完成: 成功 {len(results)}/{len(fetcher.platforms)}")

        if failed:
            logger.warning(f"失败的平台: {', '.join(failed)}")

        # 6. 处理抓取结果并保存
        logger.info("\n[步骤 6] 处理并保存数据...")

        # 构建结果数据结构
        processed_results = {}
        id_to_name = {}

        for result in results:
            platform_id = result["platform_id"]
            platform_name = result["platform_name"]
            data = result["data"]

            id_to_name[platform_id] = platform_name

            # 提取新闻列表
            items = data.get("items", [])
            if items:
                processed_results[platform_id] = {}
                for item in items:
                    title = item.get("title", "")
                    if title:
                        processed_results[platform_id][title] = {
                            "ranks": [item.get("rank", 1)],
                            "url": item.get("url", ""),
                            "mobileUrl": item.get("mobileUrl", ""),
                        }

        # 保存到文件
        file_path = save_titles_to_file(processed_results, id_to_name, failed)
        logger.info(f"✅ 数据已保存: {file_path}")

        # 7. 读取当日所有数据
        logger.info("\n[步骤 7] 读取当日所有数据...")
        all_results, final_id_to_name, title_info = read_all_today_titles()
        total_titles = sum(len(v) for v in all_results.values())
        logger.info(f"✅ 读取完成: {len(all_results)} 个平台, {total_titles} 条标题")

        # 8. 关键词匹配
        logger.info("\n[步骤 8] 进行关键词匹配...")
        matched_news = count_word_frequency(
            results=all_results,
            word_groups=word_groups,
            filter_words=filter_words,
            id_to_name=final_id_to_name,
            title_info=title_info,
            rank_threshold=config.get("RANK_THRESHOLD", 5),
            weight_config=config.get("WEIGHT_CONFIG"),
        )
        logger.info(f"✅ 匹配到 {len(matched_news)} 条相关新闻")

        # 9. 显示前 10 条匹配结果
        if matched_news:
            logger.info("\n[步骤 9] 显示TOP 10匹配新闻:")
            logger.info("-" * 70)
            for i, news in enumerate(matched_news[:10], 1):
                logger.info(f"{i}. [{news['source_name']}] {news['title']}")
                logger.info(f"   排名: {news['ranks']}, 权重: {news['weight']:.2f}")
            logger.info("-" * 70)

        # 10. 检测新增标题
        logger.info("\n[步骤 10] 检测新增标题...")
        new_titles = detect_latest_new_titles()
        total_new = sum(len(v) for v in new_titles.values())
        logger.info(f"✅ 检测到 {total_new} 条新增标题")

        if new_titles:
            logger.info("新增标题示例:")
            shown = 0
            for platform_id, titles in new_titles.items():
                platform_name = id_to_name.get(platform_id, platform_id)
                for title in list(titles.keys())[:3]:  # 每个平台显示3条
                    logger.info(f"  [{platform_name}] {title}")
                    shown += 1
                    if shown >= 5:
                        break
                if shown >= 5:
                    break

        # 测试完成
        logger.info("\n" + "=" * 70)
        logger.info("✅ 所有模块测试完成！")
        logger.info("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
