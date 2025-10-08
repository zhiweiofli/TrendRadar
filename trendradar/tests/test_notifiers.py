"""
测试推送模块示例

演示如何使用 trendradar.notifiers 发送消息
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from trendradar.notifiers import (
    DingTalkNotifier,
    FeishuNotifier,
    TelegramNotifier,
    WeWorkNotifier,
)
from trendradar.utils import init_app_logger

# 初始化日志
logger = init_app_logger(log_level="INFO")


def test_feishu():
    """测试飞书推送"""
    logger.info("\n=== 测试飞书推送 ===")

    # 创建测试数据
    report_data = {
        "stats": [
            {
                "word": "AI技术",
                "count": 5,
                "titles": [
                    {
                        "title": "OpenAI发布GPT-5",
                        "source_name": "科技新闻",
                        "time_display": "10时30分 ~ 11时00分",
                        "count": 2,
                        "ranks": [1, 2],
                        "rank_threshold": 5,
                        "url": "https://example.com/news1",
                        "mobile_url": "",
                        "is_new": False,
                    },
                    {
                        "title": "Google推出新AI模型",
                        "source_name": "科技日报",
                        "time_display": "11时15分",
                        "count": 1,
                        "ranks": [3],
                        "rank_threshold": 5,
                        "url": "https://example.com/news2",
                        "mobile_url": "",
                        "is_new": True,
                    },
                ],
            }
        ],
        "new_titles": [],
        "failed_ids": [],
        "total_new_count": 0,
    }

    # 创建推送器（需要配置真实的webhook_url）
    # notifier = FeishuNotifier(webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/...")
    # success = notifier.send(
    #     report_data=report_data,
    #     report_type="测试报告",
    #     mode="daily"
    # )

    # 仅演示内容渲染
    logger.info("渲染飞书内容示例:")
    notifier = FeishuNotifier(webhook_url="mock_url")
    content = notifier.render_content(report_data, mode="daily")
    print(content)
    print("\n" + "=" * 70)

    return True


def test_dingtalk():
    """测试钉钉推送"""
    logger.info("\n=== 测试钉钉推送 ===")

    report_data = {
        "stats": [
            {
                "word": "科技新闻",
                "count": 3,
                "titles": [
                    {
                        "title": "苹果发布新iPhone",
                        "source_name": "科技媒体",
                        "time_display": "09时00分",
                        "count": 1,
                        "ranks": [1],
                        "rank_threshold": 5,
                        "url": "https://example.com/apple",
                        "mobile_url": "",
                        "is_new": False,
                    }
                ],
            }
        ],
        "new_titles": [],
        "failed_ids": [],
        "total_new_count": 0,
    }

    logger.info("渲染钉钉内容示例:")
    notifier = DingTalkNotifier(webhook_url="mock_url")
    content = notifier.render_content(report_data, mode="daily")
    print(content)
    print("\n" + "=" * 70)

    return True


def test_wework():
    """测试企业微信推送"""
    logger.info("\n=== 测试企业微信推送 ===")

    report_data = {
        "stats": [],
        "new_titles": [],
        "failed_ids": ["platform-001"],
        "total_new_count": 0,
    }

    logger.info("渲染企业微信内容示例:")
    notifier = WeWorkNotifier(webhook_url="mock_url")
    content = notifier.render_content(report_data, mode="daily")
    print(content)
    print("\n" + "=" * 70)

    return True


def test_telegram():
    """测试Telegram推送"""
    logger.info("\n=== 测试Telegram推送 ===")

    report_data = {
        "stats": [
            {
                "word": "热点新闻",
                "count": 2,
                "titles": [
                    {
                        "title": "全球气候峰会召开",
                        "source_name": "国际新闻",
                        "time_display": "14时30分",
                        "count": 1,
                        "ranks": [2],
                        "rank_threshold": 5,
                        "url": "https://example.com/climate",
                        "mobile_url": "",
                        "is_new": False,
                    }
                ],
            }
        ],
        "new_titles": [],
        "failed_ids": [],
        "total_new_count": 0,
    }

    logger.info("渲染Telegram内容示例:")
    notifier = TelegramNotifier(bot_token="mock_token", chat_id="mock_chat_id")
    content = notifier.render_content(report_data, mode="daily")
    print(content)
    print("\n" + "=" * 70)

    return True


def main():
    """主测试流程"""
    logger.info("=" * 70)
    logger.info("TrendRadar 推送模块测试")
    logger.info("=" * 70)

    try:
        # 测试各个推送器
        test_feishu()
        test_dingtalk()
        test_wework()
        test_telegram()

        logger.info("\n✅ 所有推送模块测试完成！")
        logger.info("\n提示：")
        logger.info("- 以上示例仅演示内容渲染")
        logger.info("- 实际发送需要配置真实的 webhook_url/bot_token")
        logger.info("- 参考 trendradar/notifiers/ 目录中的各推送器实现")

        return 0

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
