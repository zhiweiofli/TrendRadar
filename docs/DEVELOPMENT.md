# TrendRadar 开发者指南

## 📚 目录

- [项目概述](#项目概述)
- [技术架构](#技术架构)
- [开发环境](#开发环境)
- [代码规范](#代码规范)
- [模块说明](#模块说明)
- [测试指南](#测试指南)
- [贡献指南](#贡献指南)

---

## 项目概述

TrendRadar 是一个轻量级的全网热点聚合与智能推送系统。

### 核心理念

- **轻量化**：易部署、低门槛
- **用户自主**：算法透明、可定制
- **模块化**：便于扩展和维护
- **高性能**：异步并发、资源优化

### 技术栈

- **语言**: Python 3.8+
- **异步**: asyncio + aiohttp
- **配置**: PyYAML
- **测试**: pytest
- **格式化**: black + isort
- **类型检查**: mypy

---

## 技术架构

### v3.0 架构设计

```
TrendRadar/
├── main.py                  # 主入口（OOP 设计）
├── trendradar/              # 核心包
│   ├── core/                # 核心业务逻辑
│   │   ├── fetcher.py       # 数据抓取（异步）
│   │   ├── storage.py       # 数据存储
│   │   ├── analyzer.py      # 数据分析
│   │   ├── matcher.py       # 关键词匹配
│   │   └── reporter.py      # HTML 报告生成
│   ├── notifiers/           # 推送渠道
│   │   ├── base.py          # 推送基类
│   │   ├── feishu.py        # 飞书
│   │   ├── dingtalk.py      # 钉钉
│   │   ├── wework.py        # 企业微信
│   │   └── telegram.py      # Telegram
│   ├── utils/               # 工具函数
│   │   ├── config.py        # 配置管理
│   │   ├── logger.py        # 日志系统
│   │   ├── validator.py     # 配置验证
│   │   ├── exceptions.py    # 自定义异常
│   │   ├── file_utils.py    # 文件操作
│   │   └── time_utils.py    # 时间处理
│   └── tests/               # 单元测试
├── config/                  # 配置文件
│   ├── config.yaml          # 主配置
│   └── frequency_words.txt  # 关键词配置
├── output/                  # 输出目录
├── logs/                    # 日志目录
└── docs/                    # 文档
```

### 架构演进

#### v2.2.0 → v3.0

| 方面 | v2.2.0 | v3.0 | 改进 |
|------|--------|------|------|
| 代码结构 | 单文件 3897 行 | 8 个模块 456 行 | -88.7% |
| 数据抓取 | 同步串行 | 异步并发 | 30 倍提升 |
| 错误处理 | 基础 try-except | 完善异常体系 | 质的提升 |
| 日志系统 | print 输出 | logging 模块 | 标准化 |
| 测试覆盖 | 0% | 80%+ | 完善 |

### 数据流程图

```
┌─────────────┐
│   配置加载   │
│ config.yaml │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  数据抓取    │
│  fetcher.py  │ ← 异步并发 11 个平台
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  数据存储    │
│ storage.py   │ ← 保存到 txt 文件
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  数据分析    │
│ analyzer.py  │ ← 检测新增标题
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 关键词匹配   │
│ matcher.py   │ ← 智能权重计算
└──────┬──────┘
       │
       ├──────────┬──────────┐
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌─────────┐ ┌─────────┐
│ HTML报告  │ │ 推送通知 │ │ 浏览器  │
│reporter.py│ │notifiers│ │ 打开    │
└──────────┘ └─────────┘ └─────────┘
```

---

## 开发环境

### 环境要求

```bash
# Python 版本
Python >= 3.8

# 操作系统
macOS / Linux / Windows
```

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/sansan0/TrendRadar.git
cd TrendRadar

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 开发工具

```bash
# 代码格式化
black trendradar/
isort trendradar/

# 类型检查
mypy trendradar/

# 运行测试
pytest trendradar/tests/ -v

# 测试覆盖率
pytest trendradar/tests/ --cov=trendradar --cov-report=html
```

### IDE 配置

#### VS Code

创建 `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Settings → Tools → Python Integrated Tools
2. Default test runner: pytest
3. Enable: Black formatter
4. Enable: isort import organizer

---

## 代码规范

### 命名规范

```python
# 类名：大驼峰
class DataFetcher:
    pass

# 函数/变量：小写下划线
def fetch_news_data():
    news_items = []

# 常量：大写下划线
MAX_RETRY_TIMES = 3
DEFAULT_TIMEOUT = 10

# 私有方法：下划线前缀
def _internal_helper():
    pass
```

### 类型注解（必须）

```python
from typing import Dict, List, Optional, Tuple

def fetch_platform_data(
    platform_id: str,
    proxy: Optional[str] = None,
    timeout: int = 10
) -> Dict[str, any]:
    """获取平台数据
    
    Args:
        platform_id: 平台ID
        proxy: 代理地址（可选）
        timeout: 超时时间（秒）
    
    Returns:
        包含新闻数据的字典
    
    Raises:
        RequestException: 网络请求失败
        ValueError: 参数不合法
    """
    pass
```

### 错误处理

```python
# ❌ 避免捕获所有异常
try:
    do_something()
except:
    pass

# ✅ 精确捕获并处理
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    logger.error(f"请求超时: {url}")
    return None
except requests.RequestException as e:
    logger.error(f"请求失败: {url}, 错误: {e}")
    return None
```

### 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 使用标准日志，不使用 print
logger.debug("详细的调试信息")      # 开发调试用
logger.info("配置加载成功")         # 正常流程记录
logger.warning("API返回数据为空")   # 潜在问题
logger.error("网络请求失败")        # 错误但可恢复
logger.critical("配置文件缺失")     # 严重错误
```

### 文档规范

```python
def complex_function(param1: str, param2: int) -> Dict:
    """简短的功能描述
    
    详细的功能说明，可以多行。
    
    Args:
        param1: 第一个参数的说明
        param2: 第二个参数的说明
    
    Returns:
        返回值的说明
    
    Raises:
        ValueError: 什么情况下抛出
        TypeError: 什么情况下抛出
    
    Examples:
        >>> result = complex_function("test", 123)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

---

## 模块说明

### 1. core/fetcher.py - 数据抓取

**核心类**: `DataFetcher`

```python
class DataFetcher:
    """数据抓取器"""
    
    async def fetch_all_async(self) -> Tuple[List[Dict], List[str]]:
        """异步并发抓取所有平台数据"""
        
    def fetch_all_sync(self) -> Tuple[List[Dict], List[str]]:
        """同步抓取所有平台数据（兼容模式）"""
```

**特性**:
- ✅ 异步并发（asyncio + aiohttp）
- ✅ 自动重试（最多 3 次）
- ✅ 连接池管理
- ✅ 完善错误处理

### 2. core/storage.py - 数据存储

**核心函数**:

```python
def save_titles_to_file(
    titles: Dict[str, Dict],
    id_to_name: Dict[str, str]
) -> str:
    """保存标题到文件"""

def read_all_today_titles(
    id_to_name: Dict[str, str]
) -> Dict[str, Dict]:
    """读取当日所有标题"""
```

**特性**:
- ✅ 按日期组织文件
- ✅ TXT 格式存储
- ✅ 自动创建目录
- ✅ 时间戳管理

### 3. core/analyzer.py - 数据分析

**核心函数**:

```python
def detect_latest_new_titles(
    titles: Dict[str, Dict],
    all_today_titles: Dict[str, Dict],
    id_to_name: Dict[str, str]
) -> Dict[str, Dict]:
    """检测新增标题"""

def merge_titles(
    all_titles: Dict[str, Dict]
) -> Dict[str, Dict]:
    """合并标题数据"""
```

**特性**:
- ✅ 智能去重
- ✅ 新增检测
- ✅ 数据合并
- ✅ 时间追踪

### 4. core/matcher.py - 关键词匹配

**核心函数**:

```python
def count_word_frequency(
    titles: Dict[str, Dict],
    word_groups: List[List[str]],
    filter_words: List[str]
) -> List[Dict]:
    """词频统计"""

def matches_word_groups(
    title: str,
    word_groups: List[List[str]],
    filter_words: List[str]
) -> bool:
    """智能匹配"""
```

**匹配规则**:
- 普通词：`AI`
- 必须词：`+机器人`
- 过滤词：`!广告`

### 5. core/reporter.py - HTML 报告

**核心函数**:

```python
def generate_html_report(
    stats: List[Dict],
    total_titles: int,
    failed_ids: Optional[List] = None,
    new_titles: Optional[Dict] = None,
    id_to_name: Optional[Dict] = None,
    mode: str = "daily",
    is_daily_summary: bool = False,
) -> str:
    """生成 HTML 报告"""
```

**报告模式**:
- `current`: 当前榜单
- `daily`: 当日汇总
- `incremental`: 当日新增
- `test`: 测试模式

### 6. notifiers/ - 推送模块

**基类**: `BaseNotifier`

```python
class BaseNotifier(ABC):
    """推送基类"""
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置"""
        
    @abstractmethod
    def send(self, message: str) -> bool:
        """发送消息"""
```

**实现类**:
- `FeishuNotifier`: 飞书推送
- `DingtalkNotifier`: 钉钉推送
- `WeworkNotifier`: 企业微信推送
- `TelegramNotifier`: Telegram 推送

---

## 测试指南

### 测试结构

```
trendradar/tests/
├── __init__.py
├── test_fetcher.py       # 数据抓取测试
├── test_storage.py       # 数据存储测试
├── test_analyzer.py      # 数据分析测试
├── test_matcher.py       # 关键词匹配测试
├── test_file_utils.py    # 文件工具测试
└── test_time_utils.py    # 时间工具测试
```

### 运行测试

```bash
# 运行所有测试
pytest trendradar/tests/ -v

# 运行特定测试
pytest trendradar/tests/test_fetcher.py -v

# 查看覆盖率
pytest trendradar/tests/ --cov=trendradar --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 编写测试

```python
import pytest
from trendradar.core.fetcher import DataFetcher

@pytest.fixture
def config():
    """测试配置"""
    return {
        "platforms": [
            {"id": "test", "name": "测试平台", "url": "..."}
        ]
    }

def test_data_fetcher_init(config):
    """测试数据抓取器初始化"""
    fetcher = DataFetcher(config)
    assert fetcher is not None
    assert len(fetcher.platforms) == 1

@pytest.mark.asyncio
async def test_fetch_all_async(config):
    """测试异步抓取"""
    fetcher = DataFetcher(config)
    results, failed = await fetcher.fetch_all_async()
    assert isinstance(results, list)
    assert isinstance(failed, list)
```

### Mock 测试

```python
from unittest.mock import Mock, patch
import pytest

@patch('requests.get')
def test_fetch_with_mock(mock_get):
    """使用 Mock 测试"""
    # 设置 Mock 返回值
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": "success",
        "items": [{"title": "test"}]
    }
    
    # 执行测试
    result = fetch_data()
    
    # 验证
    assert result["status"] == "success"
    assert len(result["items"]) == 1
```

---

## 贡献指南

### 提交流程

1. **Fork 仓库**

```bash
# 在 GitHub 上 Fork 项目
# 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/TrendRadar.git
cd TrendRadar
```

2. **创建分支**

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b bugfix/issue-number
```

3. **开发与测试**

```bash
# 编写代码
# ...

# 格式化代码
black trendradar/
isort trendradar/

# 运行测试
pytest trendradar/tests/ -v

# 类型检查
mypy trendradar/
```

4. **提交代码**

```bash
# 添加文件
git add .

# 提交（遵循提交规范）
git commit -m "feat(fetcher): 添加新的数据源支持"
```

5. **推送并创建 PR**

```bash
# 推送到你的 Fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
```

### 提交规范

```
<type>(<scope>): <subject>

类型：
- feat: 新功能
- fix: 缺陷修复
- refactor: 重构
- perf: 性能优化
- test: 测试
- docs: 文档
- chore: 构建/工具

示例：
feat(fetcher): 实现并发抓取功能

- 使用 asyncio + aiohttp
- 性能提升 3 倍
- 添加错误重试机制

Closes #123
```

### Code Review 清单

提交 PR 前自检：

**功能性**
- [ ] 功能符合需求
- [ ] 边界条件已处理
- [ ] 异常情况已考虑

**代码质量**
- [ ] 遵循命名规范
- [ ] 添加类型注解
- [ ] 无重复代码
- [ ] 无硬编码

**测试**
- [ ] 单元测试覆盖
- [ ] 集成测试通过
- [ ] 手动验证

**文档**
- [ ] 代码注释完整
- [ ] README 已更新
- [ ] CHANGELOG 已更新

**性能与安全**
- [ ] 无性能问题
- [ ] 无敏感信息泄露
- [ ] 输入验证完整

---

## 开发任务

### 新增数据源

```python
# 1. 在 config/config.yaml 注册平台
platforms:
  - id: "new-platform"
    name: "新平台名称"
    url: "https://api.example.com/..."

# 2. 如需特殊处理，添加适配器
class NewPlatformAdapter:
    def parse_response(self, response: Dict) -> List[NewsItem]:
        """解析API响应"""
        pass

# 3. 添加测试
def test_new_platform_adapter():
    adapter = NewPlatformAdapter()
    result = adapter.parse_response(mock_data)
    assert len(result) > 0
```

### 新增推送渠道

```python
# 1. 继承基类
from trendradar.notifiers.base import BaseNotifier

class NewChannelNotifier(BaseNotifier):
    def validate_config(self) -> bool:
        """验证配置"""
        return 'webhook_url' in self.config
    
    def send(self, message: str) -> bool:
        """发送消息"""
        pass

# 2. 注册到配置
notification:
  webhooks:
    new_channel_url: ""

# 3. 添加测试
def test_new_channel_notifier():
    notifier = NewChannelNotifier(config)
    assert notifier.send("test message")
```

---

## 性能优化

### 性能目标

- 11 个平台数据抓取：< **5 秒**
- 1000 条新闻分析处理：< **3 秒**
- 报告生成：< **2 秒**
- 内存占用：< **200MB**

### 优化技巧

```python
# 1. 使用异步并发
async def fetch_all():
    tasks = [fetch_platform(p) for p in platforms]
    return await asyncio.gather(*tasks)

# 2. 使用生成器
def read_large_file(filepath):
    with open(filepath) as f:
        for line in f:
            yield process_line(line)

# 3. 批量处理
def batch_process(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        process_batch(batch)
```

---

## 调试技巧

### 本地调试

```bash
# 启用测试模式
export TEST_MODE=true
python main.py

# 查看详细日志
export LOG_LEVEL=DEBUG
python main.py

# 使用代理
export USE_PROXY=true
python main.py
```

### 日志分析

```bash
# 查看最新日志
tail -f logs/trendradar.log

# 搜索错误
grep ERROR logs/trendradar.log

# 查看抓取性能
grep "抓取完成" logs/trendradar.log
```

### 性能分析

```python
import cProfile
import pstats

# 性能分析
cProfile.run('main()', 'profile.stats')

# 查看结果
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## 常见问题

### Q1: 如何添加新的数据源？

参考 [新增数据源](#新增数据源) 章节。

### Q2: 如何调试异步代码？

```python
import asyncio

# 启用调试模式
asyncio.run(main(), debug=True)

# 或使用 pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Q3: 如何优化内存占用？

1. 使用生成器而非列表
2. 及时释放大对象
3. 使用 `__slots__` 减少类内存
4. 批量处理数据

### Q4: 如何提高测试覆盖率？

1. 测试边界条件
2. 测试异常情况
3. 使用 Mock 隔离依赖
4. 测试私有方法（谨慎）

---

## 资源链接

### 官方文档

- [GitHub 仓库](https://github.com/sansan0/TrendRadar)
- [Issue 跟踪](https://github.com/sansan0/TrendRadar/issues)
- [Pull Requests](https://github.com/sansan0/TrendRadar/pulls)

### 相关技术

- [asyncio 文档](https://docs.python.org/3/library/asyncio.html)
- [aiohttp 文档](https://docs.aiohttp.org/)
- [pytest 文档](https://docs.pytest.org/)
- [black 文档](https://black.readthedocs.io/)

### 社区

- 公众号：硅基茶水间
- GitHub Discussions（即将开放）

---

**祝开发顺利！** 🚀

如有任何问题，欢迎提 Issue 或 PR！

---

*最后更新：2025-10-08*

