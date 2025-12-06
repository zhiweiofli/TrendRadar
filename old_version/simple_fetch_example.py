"""
TrendRadar v3.0 简单使用示例

演示如何使用新的模块化架构进行数据抓取
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from trendradar.core import DataFetcher
from trendradar.utils import load_config, init_app_logger


def main():
    """主函数"""
    # 1. 初始化日志
    logger = init_app_logger(log_level="INFO", enable_file_log=False)
    logger.info("=== TrendRadar v3.0 示例程序 ===")
    
    # 2. 加载配置
    logger.info("加载配置文件...")
    config = load_config()
    # 打印 config
    logger.info("配置文件: %s", config)

    # 3. 创建数据抓取器
    logger.info("初始化数据抓取器...")
    fetcher = DataFetcher(
        config=config,
        proxy_url=config.get("DEFAULT_PROXY") if config.get("USE_PROXY") else None,
        max_retries=3,
        timeout=10
    )
    
    # 4. 抓取数据
    logger.info(f"准备抓取 {len(fetcher.platforms)} 个平台...")
    
    # 使用异步模式（推荐）
    if config.get("ENABLE_ASYNC", True):
        logger.info("使用异步并发模式")
        results, failed = fetcher.fetch_all(use_async=True)
    else:
        logger.info("使用同步模式")
        results, failed = fetcher.fetch_all(use_async=False, request_interval=1000)
    
    # 5. 显示结果
    logger.info(f"\n{'='*60}")
    logger.info(f"抓取完成！")
    logger.info(f"成功: {len(results)}/{len(fetcher.platforms)}")
    
    if results:
        logger.info(f"\n成功抓取的平台：")
        for i, result in enumerate(results):
            platform_name = result["platform_name"]
            status = result["status"]
            data = result["data"]
            
            # 获取新闻列表（正确的字段是 items）
            items = data.get("items", [])
            items_count = len(items) if isinstance(items, list) else 0
            
            logger.info(f"  - {platform_name}: {items_count} 条新闻 (状态: {status})")
    
    if failed:
        logger.info(f"\n失败的平台 ID：")
        for platform_id in failed:
            logger.info(f"  - {platform_id}")
    
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()

