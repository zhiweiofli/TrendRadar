# TrendRadar v3.0 Phase 1-3 快速入门

> **本指南帮助你快速上手新重构的 v3.0 模块**

---

## 🚀 快速测试

### 运行测试脚本

```bash
# 1. 确保依赖已安装
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. 运行模块测试
python test_v3_modules.py
```

### 预期输出

```
======================================================================
TrendRadar v3.0 模块功能测试
======================================================================

[步骤 1] 加载配置文件...
✅ 配置验证通过

[步骤 4] 初始化数据抓取器...
✅ 将抓取 11 个平台

[步骤 5] 开始抓取数据...
异步抓取完成: 成功 11/11, 耗时 2.37秒
✅ 抓取完成: 成功 11/11

[步骤 8] 进行关键词匹配...
✅ 匹配到 421 条相关新闻

✅ 所有模块测试完成！
```

---

## 📚 模块使用示例

### 1. 数据抓取（DataFetcher）

```python
from trendradar.core import DataFetcher
from trendradar.utils import load_config

# 加载配置
config = load_config()

# 创建抓取器
fetcher = DataFetcher(config)

# 异步抓取（推荐）
results, failed = fetcher.fetch_all(use_async=True)

# 同步抓取
results, failed = fetcher.fetch_all(use_async=False)
```

### 2. 数据存储（storage）

```python
from trendradar.core import save_titles_to_file, read_all_today_titles

# 保存数据
file_path = save_titles_to_file(
    results=processed_results,
    id_to_name=platform_names,
    failed_ids=failed_platforms
)

# 读取当日所有数据
all_results, id_to_name, title_info = read_all_today_titles()
```

### 3. 数据分析（analyzer）

```python
from trendradar.core import detect_latest_new_titles, calculate_statistics

# 检测新增标题
new_titles = detect_latest_new_titles()

# 计算统计信息
stats = calculate_statistics(all_results, title_info)
print(f"总平台: {stats['total_platforms']}")
print(f"总标题: {stats['total_titles']}")
```

### 4. 关键词匹配（matcher）

```python
from trendradar.core import count_word_frequency
from trendradar.utils import load_frequency_words

# 加载关键词
word_groups, filter_words = load_frequency_words()

# 匹配新闻
matched_news = count_word_frequency(
    results=all_results,
    word_groups=word_groups,
    filter_words=filter_words,
    id_to_name=id_to_name,
    title_info=title_info,
    rank_threshold=5
)

# 显示TOP 10
for i, news in enumerate(matched_news[:10], 1):
    print(f"{i}. [{news['source_name']}] {news['title']}")
    print(f"   排名: {news['ranks']}, 权重: {news['weight']:.2f}")
```

---

## 🏗️ 项目结构

```
TrendRadar/
├── trendradar/                  # 核心包
│   ├── __init__.py
│   ├── core/                    # 核心业务模块
│   │   ├── __init__.py         (导出所有核心函数)
│   │   ├── fetcher.py          (数据抓取, 312行)
│   │   ├── storage.py          (数据存储, 233行)
│   │   ├── analyzer.py         (数据分析, 218行)
│   │   └── matcher.py          (关键词匹配, 250行)
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── config.py           (配置管理)
│   │   ├── logger.py           (日志系统)
│   │   ├── time_utils.py       (时间工具)
│   │   ├── file_utils.py       (文件工具)
│   │   ├── validator.py        (验证器)
│   │   └── exceptions.py       (自定义异常)
│   ├── notifiers/               # 推送模块（待实现）
│   │   └── __init__.py
│   └── tests/                   # 单元测试
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_fetcher.py
│       ├── test_file_utils.py
│       └── test_time_utils.py
├── config/                      # 配置文件
│   ├── config.yaml
│   └── frequency_words.txt
├── examples/                    # 示例脚本
│   ├── README.md
│   └── simple_fetch_example.py
├── docs/                        # 文档
│   ├── PRD-01.md               (需求文档)
│   ├── implement.md            (实施计划)
│   ├── v3.0_PHASE1_COMPLETION_REPORT.md  (完成报告)
│   └── PHASE1_QUICKSTART.md    (本文档)
├── test_v3_modules.py          # 集成测试脚本
├── main.py                      # 主程序（兼容v2.2）
├── requirements.txt             # 生产依赖
├── requirements-dev.txt         # 开发依赖
└── pytest.ini                   # pytest 配置
```

---

## 🔧 开发工作流

### 1. 添加新功能

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 编写代码
# 在 trendradar/core/ 或 trendradar/utils/ 中添加

# 3. 添加测试
# 在 trendradar/tests/ 中添加测试

# 4. 运行测试
pytest trendradar/tests/ -v --cov=trendradar

# 5. 代码格式化
black trendradar/
isort trendradar/

# 6. 提交代码
git add .
git commit -m "feat(core): 添加新功能"
git push origin feature/new-feature
```

### 2. 调试技巧

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python test_v3_modules.py

# 查看最近的日志文件
tail -f logs/trendradar_*.log

# 测试单个模块
pytest trendradar/tests/test_fetcher.py -v

# 测试覆盖率
pytest trendradar/tests/ --cov=trendradar --cov-report=html
open htmlcov/index.html
```

---

## 📊 性能对比

| 指标 | v2.2.0 | v3.0 | 提升 |
|------|--------|------|------|
| 抓取时间 | ~60秒 | ~2.4秒 | **25倍** ⚡ |
| 数据处理 | ~2秒 | ~0.5秒 | **4倍** |
| 代码行数 | 3896行 | 1053行 (core) | **模块化** |
| 测试覆盖 | 0% | 78% | **新增** ✅ |

---

## ⚙️ 配置说明

### 启用异步抓取

在 `config/config.yaml` 中：

```yaml
crawler:
  enable_async: true  # v3.0 新增，性能提升 25 倍
  request_interval: 1000
  use_proxy: false
  default_proxy: "http://127.0.0.1:10086"
```

### 日志配置

```python
from trendradar.utils import init_app_logger

# 初始化日志（文件 + 控制台）
logger = init_app_logger(
    log_level="INFO",        # DEBUG/INFO/WARNING/ERROR
    enable_file_log=True,    # 是否写入文件
    log_dir="logs"           # 日志目录
)
```

---

## ❓ 常见问题

### Q1: 测试脚本运行失败？

**A**: 检查依赖安装：
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Q2: 异步抓取报错？

**A**: 确认 Python 版本 ≥ 3.8，并安装 aiohttp：
```bash
python --version  # 应该 ≥ 3.8
pip install aiohttp==3.9.5
```

### Q3: 如何集成到现有代码？

**A**: v3.0 完全向后兼容，现有 `main.py` 仍可正常运行：
```bash
# 旧版本（仍可用）
python main.py

# 新版本测试
python test_v3_modules.py
```

### Q4: 单元测试如何运行？

**A**: 
```bash
# 运行所有测试
pytest trendradar/tests/ -v

# 运行特定测试
pytest trendradar/tests/test_fetcher.py -v

# 查看覆盖率
pytest trendradar/tests/ --cov=trendradar --cov-report=term-missing
```

---

## 🎯 下一步

### Phase 4-6（v3.1 计划）

1. **Phase 4**: 报告生成层 (~1600行)
   - 提取 HTML 报告生成
   - 模板渲染逻辑

2. **Phase 5**: 消息推送层 (~342行)
   - 飞书、钉钉、企业微信推送
   - 统一推送接口

3. **Phase 6**: 主流程编排 (~685行)
   - 重构 `NewsAnalyzer`
   - 完整集成到 `main.py`

### 参与贡献

1. 查看 [PRD-01.md](PRD-01.md) 了解完整需求
2. 查看 [implement.md](implement.md) 了解实施计划
3. 运行 `test_v3_modules.py` 验证环境
4. 提交 Pull Request

---

## 📞 获取帮助

- **文档**: `docs/` 目录
- **示例**: `examples/` 目录
- **测试**: `trendradar/tests/` 目录
- **问题反馈**: GitHub Issues

---

**最后更新**: 2025-10-08  
**版本**: v3.0.0-alpha  
**状态**: ✅ Phase 1-3 完成

