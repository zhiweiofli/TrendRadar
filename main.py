#!/usr/bin/env python3
# coding=utf-8
"""
TrendRadar v3.0 - 全网热点聚合与智能推送系统

主程序入口，集成所有重构后的模块
"""

import os
import sys
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入核心模块
from trendradar.core import (
    DataFetcher,
    save_titles_to_file,
    read_all_today_titles,
    detect_latest_new_titles,
    count_word_frequency,
    generate_html_report,
)

# 导入推送模块
from trendradar.notifiers import (
    FeishuNotifier,
    DingTalkNotifier,
    WeWorkNotifier,
    TelegramNotifier,
)

# 导入工具模块
from trendradar.utils import (
    load_config,
    load_frequency_words,
    init_app_logger,
    get_beijing_time,
    format_date_folder,
    ConfigValidator,
)
from trendradar.utils.exceptions import ConfigError, FetchError

# 版本信息
VERSION = "3.0.0"

# 初始化日志
logger = init_app_logger(log_level="INFO")


class TrendRadarApp:
    """TrendRadar 主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.config = None
        self.validator = ConfigValidator()
        self.fetcher = None
        self.word_groups = []
        self.filter_words = []
        
        # 环境检测
        self.is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        self.is_docker = self._detect_docker()
        
        # 初始化配置
        self._load_config()
        self._setup_components()
    
    def _detect_docker(self) -> bool:
        """检测是否在 Docker 容器中"""
        return (
            os.environ.get("DOCKER_CONTAINER") == "true" or
            os.path.exists("/.dockerenv")
        )
    
    def _load_config(self):
        """加载并验证配置"""
        try:
            logger.info("=" * 70)
            logger.info(f"TrendRadar v{VERSION} 启动中...")
            logger.info("=" * 70)
            
            # 加载配置
            self.config = load_config()
            logger.info(f"✅ 配置文件加载成功")
            
            # 验证配置
            self.validator.validate(self.config)
            logger.info(f"✅ 配置验证通过")
            
            # 加载关键词
            word_data = load_frequency_words()
            # load_frequency_words 返回 (processed_groups, filter_words)
            if isinstance(word_data, tuple) and len(word_data) == 2:
                self.word_groups, self.filter_words = word_data
            else:
                # 兼容性处理
                self.word_groups = word_data if isinstance(word_data, list) else []
                self.filter_words = []
            logger.info(f"✅ 关键词配置加载完成: {len(self.word_groups)} 个词组")
            
        except ConfigError as e:
            logger.error(f"❌ 配置错误: {e.message}")
            if e.solution:
                logger.error(f"💡 解决方案: {e.solution}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}", exc_info=True)
            sys.exit(1)
    
    def _setup_components(self):
        """设置核心组件"""
        # 设置代理
        proxy_url = None
        if not self.is_github_actions and self.config.get("USE_PROXY"):
            proxy_url = self.config.get("DEFAULT_PROXY")
            logger.info(f"🌐 使用代理: {proxy_url}")
        
        # 创建数据抓取器
        self.fetcher = DataFetcher(
            config=self.config,
        )
        logger.info("✅ 数据抓取器初始化完成")
    
    def _fetch_data(self) -> Tuple[Dict, Dict, List]:
        """抓取数据"""
        logger.info("=" * 70)
        logger.info("开始数据抓取...")
        logger.info("=" * 70)
        
        # 检查是否启用异步
        enable_async = self.config.get("crawler", {}).get("enable_async", True)
        
        if enable_async:
            logger.info("⚡ 使用异步并发抓取")
            # fetch_all 返回 (results_list, failed_list)
            # results_list 是 List[Dict]，每个Dict包含 platform_id 和 data 字段
            results_list, failed = self.fetcher.fetch_all(use_async=True)
        else:
            logger.info("🐌 使用同步顺序抓取")
            results_list, failed = self.fetcher.fetch_all(use_async=False)
        
        # 将列表转换为字典，并提取正确的数据
        results = {}
        for item in results_list:
            if isinstance(item, dict) and "platform_id" in item:
                platform_id = item["platform_id"]
                # 从 API 响应中提取标题数据
                api_data = item.get("data", {})
                
                # API 返回格式: {"status": "success", "items": [...]}
                # 需要将 items 数组转换为字典格式 {title: {ranks: [idx], url: ...}}
                items = api_data.get("items", [])
                titles_dict = {}
                
                for idx, news_item in enumerate(items):
                    title = news_item.get("title", "")
                    url = news_item.get("url", "")
                    mobile_url = news_item.get("mobileUrl", "")
                    
                    if title:
                        titles_dict[title] = {
                            "ranks": [idx + 1],  # 排名从 1 开始
                            "url": url,
                            "mobileUrl": mobile_url
                        }
                
                results[platform_id] = titles_dict
            elif isinstance(item, tuple) and len(item) == 2:
                # 兼容元组格式 (platform_id, titles_dict)
                platform_id, titles_dict = item
                results[platform_id] = titles_dict
        
        # 准备 id_to_name 映射
        id_to_name = {p["id"]: p["name"] for p in self.config["PLATFORMS"]}
        
        logger.info(f"✅ 抓取完成: 成功 {len(results)}/{len(self.config['PLATFORMS'])}, 失败 {len(failed)}")
        
        return results, id_to_name, failed
    
    def _save_and_process_data(
        self,
        results: Dict,
        id_to_name: Dict,
        failed: List
    ) -> Tuple[Dict, Dict, Dict]:
        """保存并处理数据"""
        # 保存到文件
        output_file = save_titles_to_file(results, id_to_name, failed)
        logger.info(f"💾 数据已保存: {output_file}")
        
        # 读取当日所有数据
        current_platform_ids = [p["id"] for p in self.config["PLATFORMS"]]
        all_results, final_id_to_name, title_info = read_all_today_titles(
            current_platform_ids=current_platform_ids
        )
        
        logger.info(f"📚 读取当日数据: {len(all_results)} 个平台, {sum(len(titles) for titles in all_results.values())} 条标题")
        
        # 检测新增
        new_titles = detect_latest_new_titles(current_platform_ids)
        new_count = sum(len(titles) for titles in new_titles.values())
        logger.info(f"🆕 检测到 {new_count} 条新增标题")
        
        return all_results, title_info, new_titles
    
    def _analyze_and_match(
        self,
        all_results: Dict,
        id_to_name: Dict,
        title_info: Dict,
        new_titles: Dict
    ) -> Tuple[List[Dict], int]:
        """分析并匹配关键词"""
        logger.info("=" * 70)
        logger.info("开始关键词匹配...")
        logger.info("=" * 70)
        
        mode = self.config.get("REPORT_MODE", "daily")
        rank_threshold = self.config.get("RANK_THRESHOLD", 10)
        
        # 读取权重配置（从配置字典中获取，config.py 已处理向后兼容）
        weight_config = self.config.get("WEIGHT_CONFIG")
        if weight_config:
            logger.info(f"📊 权重配置: 排名{weight_config['RANK_WEIGHT']:.1%} | 频次{weight_config['FREQUENCY_WEIGHT']:.1%} | 热度{weight_config['HOTNESS_WEIGHT']:.1%}")
        else:
            weight_config = None  # 使用默认值
        
        stats = count_word_frequency(
            results=all_results,
            word_groups=self.word_groups,
            filter_words=self.filter_words,
            id_to_name=id_to_name,
            title_info=title_info,
            rank_threshold=rank_threshold,
            weight_config=weight_config,
        )
        
        # count_word_frequency 返回的是扁平的新闻列表
        # 需要转换为词组格式以兼容报告生成
        if stats and isinstance(stats, list):
            # stats 是新闻列表，按词组重新组织
            total_matched = len(stats)
            
            # 按词组重新组织（简化处理：所有新闻归为一个组）
            if total_matched > 0:
                stats = [{
                    "word": "热点新闻",
                    "count": total_matched,
                    "titles": stats  # 直接使用列表
                }]
            else:
                stats = []
        else:
            total_matched = 0
            stats = []
        
        logger.info(f"✅ 匹配完成: {total_matched} 条相关新闻")
        
        return stats, total_matched
    
    def _generate_html_report(
        self,
        stats: List[Dict],
        total_titles: int,
        failed: List,
        new_titles: Dict,
        id_to_name: Dict
    ) -> str:
        """生成 HTML 报告"""
        mode = self.config.get("REPORT_MODE", "daily")
        
        try:
            html_file = generate_html_report(
                stats=stats,
                total_titles=total_titles,
                failed_ids=failed,
                new_titles=new_titles,
                id_to_name=id_to_name,
                mode=mode,
                is_daily_summary=True
            )
            
            logger.info(f"📄 HTML报告已生成: {html_file}")
            return html_file
        except Exception as e:
            logger.error(f"❌ HTML报告生成失败: {e}", exc_info=True)
            return None
    
    def _send_notifications(
        self,
        stats: List[Dict],
        failed: List,
        new_titles: Dict,
        id_to_name: Dict
    ):
        """发送推送通知"""
        if not self.config.get("ENABLE_NOTIFICATION"):
            logger.info("⏭  通知功能已禁用")
            return
        
        logger.info("=" * 70)
        logger.info("开始推送通知...")
        logger.info("=" * 70)
        
        # 准备报告数据
        from trendradar.core.reporter import prepare_report_data
        
        mode = self.config.get("REPORT_MODE", "daily")
        report_data = prepare_report_data(stats, failed, new_titles, id_to_name, mode)
        report_type = "每日汇总报告"
        
        # 检查是否有内容
        if not report_data.get("stats"):
            logger.info("📭 没有匹配的新闻，跳过推送")
            return
        
        # 获取代理设置
        proxy_url = None
        if not self.is_github_actions and self.config.get("USE_PROXY"):
            proxy_url = self.config.get("DEFAULT_PROXY")
        
        success_count = 0
        
        # 飞书推送
        feishu_url = self.config.get("WEBHOOKS", {}).get("feishu_url")
        if feishu_url:
            try:
                from trendradar.notifiers.feishu import FeishuNotifier
                notifier = FeishuNotifier(
                    webhook_url=feishu_url,
                    proxy_url=proxy_url
                )
                if notifier.send(report_data, report_type, mode=mode):
                    success_count += 1
            except Exception as e:
                logger.error(f"飞书推送失败: {e}")
        
        # 钉钉推送
        dingtalk_url = self.config.get("WEBHOOKS", {}).get("dingtalk_url")
        if dingtalk_url:
            try:
                from trendradar.notifiers.dingtalk import DingTalkNotifier
                notifier = DingTalkNotifier(
                    webhook_url=dingtalk_url,
                    proxy_url=proxy_url
                )
                if notifier.send(report_data, report_type, mode=mode):
                    success_count += 1
            except Exception as e:
                logger.error(f"钉钉推送失败: {e}")
        
        # 企业微信推送
        wework_url = self.config.get("WEBHOOKS", {}).get("wework_url")
        if wework_url:
            try:
                from trendradar.notifiers.wework import WeWorkNotifier
                notifier = WeWorkNotifier(
                    webhook_url=wework_url,
                    proxy_url=proxy_url
                )
                if notifier.send(report_data, report_type, mode=mode):
                    success_count += 1
            except Exception as e:
                logger.error(f"企业微信推送失败: {e}")
        
        # Telegram推送
        telegram_token = self.config.get("WEBHOOKS", {}).get("telegram_bot_token")
        telegram_chat_id = self.config.get("WEBHOOKS", {}).get("telegram_chat_id")
        if telegram_token and telegram_chat_id:
            try:
                from trendradar.notifiers.telegram import TelegramNotifier
                notifier = TelegramNotifier(
                    bot_token=telegram_token,
                    chat_id=telegram_chat_id,
                    proxy_url=proxy_url
                )
                if notifier.send(report_data, report_type, mode=mode):
                    success_count += 1
            except Exception as e:
                logger.error(f"Telegram推送失败: {e}")
        
        if success_count > 0:
            logger.info(f"✅ 推送完成: {success_count} 个渠道成功")
        else:
            logger.warning("⚠️  所有推送渠道失败或未配置")
    
    def _open_browser(self, html_file: str):
        """打开浏览器查看报告"""
        if self.is_github_actions or self.is_docker:
            logger.info(f"📄 HTML报告: {html_file}")
            return
        
        try:
            file_url = "file://" + str(Path(html_file).resolve())
            webbrowser.open(file_url)
            logger.info(f"🌐 已在浏览器中打开: {file_url}")
        except Exception as e:
            logger.error(f"打开浏览器失败: {e}")
    
    def run(self):
        """运行主流程"""
        try:
            # 显示环境信息
            now = get_beijing_time()
            logger.info(f"⏰ 北京时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"📊 报告模式: {self.config.get('REPORT_MODE', 'daily')}")
            logger.info(f"🖥️  运行环境: {'GitHub Actions' if self.is_github_actions else 'Docker' if self.is_docker else '本地'}")
            
            # 1. 抓取数据
            results, id_to_name, failed = self._fetch_data()
            
            # 2. 保存并处理数据
            all_results, title_info, new_titles = self._save_and_process_data(
                results, id_to_name, failed
            )
            
            # 3. 分析并匹配
            stats, total_matched = self._analyze_and_match(
                all_results, id_to_name, title_info, new_titles
            )
            
            # 4. 生成 HTML 报告
            total_titles = sum(len(titles) for titles in all_results.values())
            html_file = self._generate_html_report(
                stats, total_titles, failed, new_titles, id_to_name
            )
            
            # 5. 发送推送通知
            self._send_notifications(stats, failed, new_titles, id_to_name)
            
            # 6. 打开浏览器
            #if html_file:
            #    self._open_browser(html_file)
            
            # 完成
            logger.info("=" * 70)
            logger.info("✅ TrendRadar 运行完成！")
            logger.info("=" * 70)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  用户中断")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ 运行失败: {e}", exc_info=True)
            sys.exit(1)


def main():
    """主函数"""
    try:
        app = TrendRadarApp()
        app.run()
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
