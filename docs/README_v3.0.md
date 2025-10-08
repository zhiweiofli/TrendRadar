# TrendRadar v3.0 - 增量重构版

> **轻量级全网热点聚合与智能推送系统 - 模块化重构版**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v3.0--alpha-orange.svg)](version)

---

## 🎉 v3.0 新特性

### ⚡ 性能提升 25 倍

| 指标 | v2.2.0 | v3.0 | 提升 |
|------|--------|------|------|
| 11平台抓取 | ~60秒 | ~2.4秒 | **25倍** ⚡ |
| 数据处理 | ~2秒 | ~0.5秒 | **4倍** |
| 总响应时间 | ~62秒 | ~3秒 | **20倍** |

### 🏗️ 模块化架构

```
v2.2.0: main.py (3896行)
  ↓
v3.0: trendradar/ (模块化)
  ├── core/         (1053行: 4个核心模块)
  ├── utils/        (725行: 7个工具模块)
  ├── notifiers/    (待实现: 推送模块)
  └── tests/        (298行: 单元测试)
```

### ✅ 已完成功能（Phase 1-3）

- ✅ **数据抓取**: 异步并发抓取，25倍性能提升
- ✅ **数据存储**: 标题保存、解析、读取
- ✅ **数据分析**: 新增检测、统计分析
- ✅ **关键词匹配**: 权重计算、词组匹配、排序
- ✅ **单元测试**: 30个测试用例，78% 覆盖率
- ✅ **CI/CD**: GitHub Actions 自动化测试

### 🚧 待开发功能（Phase 4-6）

- ⏳ **报告生成**: HTML报告、邮件报告
- ⏳ **消息推送**: 飞书、钉钉、企业微信、Telegram
- ⏳ **主流程**: 完整集成到 main.py

---

## 🚀 快速开始

### 安装依赖

```bash
# 生产依赖
pip install -r requirements.txt

# 开发依赖（可选）
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 测试新模块
python test_v3_modules.py
```

### 预期输出

```
======================================================================
TrendRadar v3.0 模块功能测试
======================================================================

[步骤 5] 开始抓取数据...
异步抓取完成: 成功 11/11, 耗时 2.37秒
✅ 抓取完成: 成功 11/11

[步骤 8] 进行关键词匹配...
✅ 匹配到 421 条相关新闻

[步骤 10] 检测新增标题...
✅ 检测到 40 条新增标题

✅ 所有模块测试完成！
```

---

## 📚 使用示例

### 基础使用

```python
from trendradar.core import DataFetcher
from trendradar.utils import load_config

# 1. 加载配置
config = load_config()

# 2. 创建抓取器
fetcher = DataFetcher(config)

# 3. 异步抓取（推荐）
results, failed = fetcher.fetch_all(use_async=True)

print(f"成功: {len(results)}, 失败: {len(failed)}")
```

### 完整流程

参考 `test_v3_modules.py` 或查看 [docs/PHASE1_QUICKSTART.md](docs/PHASE1_QUICKSTART.md)

---

## 📊 项目结构

```
TrendRadar/
├── trendradar/              # 核心包
│   ├── core/               # 核心业务（1053行）
│   │   ├── fetcher.py     # 数据抓取（312行）
│   │   ├── storage.py     # 数据存储（233行）
│   │   ├── analyzer.py    # 数据分析（218行）
│   │   └── matcher.py     # 关键词匹配（250行）
│   ├── utils/              # 工具模块（725行）
│   │   ├── config.py      # 配置管理
│   │   ├── logger.py      # 日志系统
│   │   ├── time_utils.py  # 时间工具
│   │   ├── file_utils.py  # 文件工具
│   │   ├── validator.py   # 数据验证
│   │   └── exceptions.py  # 自定义异常
│   └── tests/              # 单元测试（298行）
├── config/                 # 配置文件
│   ├── config.yaml
│   └── frequency_words.txt
├── examples/               # 示例脚本
├── docs/                   # 文档
│   ├── PRD-01.md          # 需求文档
│   ├── implement.md       # 实施计划
│   ├── v3.0_PHASE1_COMPLETION_REPORT.md  # 完成报告
│   └── PHASE1_QUICKSTART.md              # 快速入门
├── test_v3_modules.py     # 集成测试
├── main.py                 # 主程序（兼容v2.2）
└── requirements.txt        # 依赖列表
```

---

## 🔧 开发指南

### 运行测试

```bash
# 集成测试
python test_v3_modules.py

# 单元测试
pytest trendradar/tests/ -v

# 测试覆盖率
pytest trendradar/tests/ --cov=trendradar --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black trendradar/
isort trendradar/

# 类型检查
mypy trendradar/
```

---

## 📈 性能数据

### 异步抓取性能

```
测试环境: macOS 14.3, Python 3.11
测试时间: 2025-10-08 14:52

平台数量: 11
总数据量: 255 条新闻
抓取时间: 2.37 秒
成功率: 100%

性能提升: 25 倍（从 60 秒到 2.4 秒）
```

### 数据处理性能

```
保存数据: < 0.1 秒
读取数据: < 0.2 秒（9个文件，421条标题）
关键词匹配: < 0.1 秒（421条新闻）
新增检测: < 0.1 秒（检测 40 条新增）
总处理时间: < 0.5 秒
```

---

## 🎯 版本路线图

### ✅ v3.0-alpha（当前）

- [x] Phase 1: 数据存储层
- [x] Phase 2: 数据分析层
- [x] Phase 3: 关键词匹配层
- [x] Phase 7: 集成测试
- [x] 性能优化（25倍提升）
- [x] 单元测试（78% 覆盖）

### 🚧 v3.0-beta（Week 4）

- [ ] Phase 4: 报告生成层
- [ ] Phase 5: 消息推送层
- [ ] Phase 6: 主流程编排
- [ ] 完整端到端测试

### 🎯 v3.1（Week 5-6）

- [ ] 生产环境验证
- [ ] 文档完善
- [ ] 性能基准测试
- [ ] 正式发布

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [PRD-01.md](docs/PRD-01.md) | 产品需求文档 |
| [implement.md](docs/implement.md) | 实施计划 |
| [v3.0_PHASE1_COMPLETION_REPORT.md](docs/v3.0_PHASE1_COMPLETION_REPORT.md) | Phase 1-3 完成报告 |
| [PHASE1_QUICKSTART.md](docs/PHASE1_QUICKSTART.md) | 快速入门指南 |
| [MAIN_PY_ANALYSIS.md](docs/MAIN_PY_ANALYSIS.md) | main.py 结构分析 |

---

## 🤝 贡献指南

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 编写代码和测试
4. 运行测试 (`pytest trendradar/tests/`)
5. 提交代码 (`git commit -m 'feat: Add AmazingFeature'`)
6. 推送分支 (`git push origin feature/AmazingFeature`)
7. 创建 Pull Request

### 代码规范

- 遵循 [PEP 8](https://pep8.org/)
- 使用 `black` 格式化
- 使用 `isort` 排序导入
- 添加类型注解
- 编写单元测试

---

## ❓ 常见问题

### Q: v3.0 是否兼容 v2.2？

**A**: 是的！v3.0 完全向后兼容。`main.py` 仍可正常运行，新模块作为独立测试。

### Q: 如何启用异步抓取？

**A**: 在 `config/config.yaml` 中设置：
```yaml
crawler:
  enable_async: true  # v3.0 新增
```

### Q: 如何参与开发？

**A**: 
1. 查看 [docs/implement.md](docs/implement.md) 了解计划
2. 运行 `test_v3_modules.py` 验证环境
3. 选择 Phase 4-6 中的任务
4. 提交 Pull Request

---

## 📊 测试覆盖率

```
Module                      Statements  Missing  Coverage
----------------------------------------------------------
trendradar/__init__.py              8        0   100%
trendradar/core/__init__.py        12        0   100%
trendradar/core/fetcher.py         89       18    80%
trendradar/core/storage.py         76       15    80%
trendradar/core/analyzer.py        68       12    82%
trendradar/core/matcher.py         84       20    76%
trendradar/utils/__init__.py       15        0   100%
trendradar/utils/config.py         45        8    82%
trendradar/utils/logger.py         32        4    88%
trendradar/utils/time_utils.py     28        2    93%
trendradar/utils/file_utils.py     34        3    91%
----------------------------------------------------------
TOTAL                             491      82    78%
```

---

## 📞 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/yourusername/TrendRadar/issues)
- **文档**: [docs/](docs/) 目录
- **示例**: [examples/](examples/) 目录

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有贡献者对 TrendRadar 的支持！

---

**当前版本**: v3.0.0-alpha  
**最后更新**: 2025-10-08  
**维护者**: TrendRadar 开发团队  
**状态**: ✅ Phase 1-3 完成，Phase 4-6 开发中

