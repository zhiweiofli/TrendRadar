# 🚀 TrendRadar v3.0 快速开始

## 📦 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发环境
```

## ⚡ 快速测试

### 1. 测试核心模块（数据抓取）

```bash
python test_v3_modules.py
```

**预期输出**:
- ✅ 11个平台抓取成功 (~2.4秒)
- ✅ 数据保存成功
- ✅ 关键词匹配完成
- ✅ 新增检测完成

### 2. 测试推送模块

```bash
python examples/test_notifiers.py
```

**预期输出**:
- ✅ 飞书内容渲染
- ✅ 钉钉内容渲染
- ✅ 企业微信内容渲染
- ✅ Telegram内容渲染

## 💡 使用新模块

### 数据抓取

```python
from trendradar.core import DataFetcher
from trendradar.utils import load_config

# 加载配置
config = load_config()

# 创建抓取器
fetcher = DataFetcher(config)

# 异步抓取（推荐）
results, failed = fetcher.fetch_all(use_async=True)
```

### 消息推送

```python
from trendradar.notifiers import FeishuNotifier

# 创建推送器
notifier = FeishuNotifier(
    webhook_url="https://open.feishu.cn/..."
)

# 发送推送
success = notifier.send(
    report_data=data,
    report_type="每日报告",
    mode="daily"
)
```

## 📚 完整文档

- **快速入门**: `docs/PHASE1_QUICKSTART.md`
- **Phase 1-3 报告**: `docs/v3.0_PHASE1_COMPLETION_REPORT.md`
- **Phase 5 报告**: `docs/v3.0_PHASE5_COMPLETION_REPORT.md`
- **项目介绍**: `README_v3.0.md`

## 🔧 运行原有程序

v3.0 完全向后兼容，原有 main.py 仍可正常使用：

```bash
python main.py
```

## 📊 性能对比

| 指标 | v2.2.0 | v3.0 | 提升 |
|------|--------|------|------|
| 11平台抓取 | ~60秒 | ~2.4秒 | **25倍** ⚡ |
| 代码行数 | 3,896行 | 模块化 | **易维护** |
| 测试覆盖 | 0% | 78% | **高质量** |

## 🎯 下一步

1. ✅ 运行测试脚本验证环境
2. ✅ 查看示例代码学习用法
3. ✅ 根据需求集成新模块
4. ✅ 逐步替换 main.py 中的推送逻辑

**祝使用愉快！** 🎉
