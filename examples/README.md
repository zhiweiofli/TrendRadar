# TrendRadar v3.0 示例代码

本目录包含 TrendRadar v3.0 的使用示例。

## 运行示例

### 1. 简单数据抓取示例

展示如何使用新的模块化架构抓取热点数据：

```bash
cd /path/to/TrendRadar
python examples/simple_fetch_example.py
```

**功能**：
- 加载配置
- 初始化日志系统
- 使用异步并发抓取所有平台数据
- 显示抓取结果统计

**预期输出**：
```
2025-10-08 14:30:00 - trendradar - INFO - === TrendRadar v3.0 示例程序 ===
2025-10-08 14:30:00 - trendradar - INFO - 加载配置文件...
2025-10-08 14:30:00 - trendradar - INFO - 初始化数据抓取器...
2025-10-08 14:30:00 - trendradar - INFO - 准备抓取 11 个平台...
2025-10-08 14:30:00 - trendradar - INFO - 使用异步并发模式
2025-10-08 14:30:00 - trendradar.core.fetcher - INFO - 开始异步并发抓取 11 个平台
...
2025-10-08 14:30:20 - trendradar.core.fetcher - INFO - 异步抓取完成: 成功 11/11, 耗时 20.35秒
2025-10-08 14:30:20 - trendradar - INFO - 
============================================================
2025-10-08 14:30:20 - trendradar - INFO - 抓取完成！
2025-10-08 14:30:20 - trendradar - INFO - 成功: 11/11
```

## 更多示例（待添加）

### 2. 配置验证示例

展示如何使用配置验证器：

```python
from trendradar.utils import load_config, ConfigValidator

config = load_config()
validator = ConfigValidator()
validator.validate(config)  # 验证配置
```

### 3. 数据验证示例

展示如何验证和清洗数据：

```python
from trendradar.utils import DataValidator

validator = DataValidator()
valid_items = validator.validate_and_clean(news_items)
```

### 4. 自定义日志示例

展示如何配置日志系统：

```python
from trendradar.utils import setup_logger

logger = setup_logger(
    name="my_app",
    log_file="logs/my_app.log",
    level="DEBUG"
)
logger.debug("这是一条调试信息")
```

## 开发建议

1. **先运行示例**：了解基本用法
2. **阅读源码**：查看模块实现细节
3. **运行测试**：`pytest trendradar/tests/`
4. **参考文档**：查看 `docs/` 目录

## 需要帮助？

- 查看主文档：`../README.md`
- 开发规范：`../.cursorrules`
- 提交 Issue：https://github.com/sansan0/TrendRadar/issues

