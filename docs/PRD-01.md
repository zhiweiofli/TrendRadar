# TrendRadar v3.0 产品需求文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | TrendRadar |
| 版本号 | v3.0 |
| 文档版本 | PRD-01 |
| 创建日期 | 2025-10-08 |
| 文档状态 | 规划中 |
| 负责人 | 开发团队 |

## 一、背景与目标

### 1.1 项目背景

TrendRadar 是一个开源的全网热点聚合与智能推送系统，自 2025 年 5 月发布以来：
- 获得 **1000+ GitHub Stars**
- 被多个知名平台推荐（小众软件、阮一峰周刊、LinuxDo 社区）
- 用户覆盖投资者、自媒体人、企业管理者等多个群体
- 经过 2 个月快速迭代，从 v1.0 演进到 v2.2.0

### 1.2 当前问题（基于 SWOT 分析）

#### 代码架构问题
- **单文件过大**：main.py 超过 3800 行，违背单一职责原则
- **耦合度高**：数据采集、分析、推送逻辑混杂
- **缺乏抽象**：大量硬编码字符串和魔法数字
- **测试不足**：没有单元测试和集成测试

#### 性能与扩展性
- **串行抓取**：11 个平台串行获取，耗时 30-60 秒
- **内存占用**：所有数据加载到内存，无优化
- **无缓存机制**：重复数据每次都重新处理
- **日志系统简陋**：只用 print 输出，生产环境监控困难

#### 数据依赖风险
- **单一依赖**：完全依赖 newsnow API
- **无降级方案**：API 失效则系统不可用
- **数据验证不足**：对 API 返回缺乏充分校验

#### 安全性考虑
- **Webhook 暴露**：虽有提醒但缺乏技术防护
- **无认证机制**：任何人获取 URL 可推送
- **输入未校验**：配置文件缺乏格式验证

### 1.3 产品目标

**主要目标**：
1. **提升代码质量**：模块化架构，可测试性强，易于维护
2. **增强系统性能**：并发抓取，响应速度提升 3-5 倍
3. **提高稳定性**：完善错误处理，增加监控告警
4. **扩展核心价值**：为未来的 AI 分析、数据服务打基础

**用户价值**：
- 更快的数据更新速度
- 更稳定的服务质量
- 更友好的错误提示
- 更丰富的功能扩展

## 二、MVP 范围定义

### 2.1 P0 - 必须实现（代码质量提升）

#### P0.1 模块化重构
**目标**：将 main.py 拆分为清晰的模块结构

**详细需求**：

1. **目录结构**
```
trendradar/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── fetcher.py      # 数据抓取模块
│   ├── analyzer.py     # 数据分析模块
│   ├── matcher.py      # 关键词匹配模块
│   └── reporter.py     # 报告生成模块
├── notifiers/
│   ├── __init__.py
│   ├── base.py         # 推送基类
│   ├── feishu.py       # 飞书推送
│   ├── dingtalk.py     # 钉钉推送
│   ├── wework.py       # 企业微信推送
│   └── telegram.py     # Telegram推送
├── utils/
│   ├── __init__.py
│   ├── config.py       # 配置管理
│   ├── logger.py       # 日志系统
│   ├── time_utils.py   # 时间处理
│   └── file_utils.py   # 文件操作
└── tests/
    ├── __init__.py
    ├── conftest.py     # pytest配置
    ├── test_fetcher.py
    ├── test_analyzer.py
    └── test_notifiers.py
```

2. **模块职责**
   - `core/fetcher.py`：负责从各平台抓取数据
   - `core/analyzer.py`：负责数据分析和权重计算
   - `core/matcher.py`：负责关键词匹配逻辑
   - `core/reporter.py`：负责生成 HTML/TXT 报告
   - `notifiers/`：各推送渠道的独立实现
   - `utils/`：通用工具函数

3. **兼容性要求**
   - main.py 保留作为入口点
   - 用户升级无感知
   - 配置文件格式不变

**验收标准**：
- [ ] 所有模块拆分完成
- [ ] main.py 改为调用各模块
- [ ] 功能完全正常
- [ ] 性能无明显下降

#### P0.2 日志系统升级
**目标**：使用标准 logging 模块替换 print

**详细需求**：

1. **日志配置**
```python
# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """配置日志系统"""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/trendradar.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

2. **日志级别使用规范**
   - DEBUG：详细的调试信息
   - INFO：正常流程记录
   - WARNING：潜在问题
   - ERROR：错误但可恢复
   - CRITICAL：严重错误

3. **迁移策略**
   - 第一阶段：新代码使用 logger
   - 第二阶段：逐步替换现有 print
   - 第三阶段：完全移除 print

**验收标准**：
- [ ] 日志系统配置完成
- [ ] 日志文件正常生成和轮转
- [ ] 核心流程都有日志记录
- [ ] print 替换率 ≥ 80%

#### P0.3 并发抓取实现
**目标**：使用 asyncio 实现并发抓取，性能提升 3-5 倍

**详细需求**：

1. **异步抓取实现**
```python
import asyncio
import aiohttp

async def fetch_platform_async(
    session: aiohttp.ClientSession,
    platform: Dict
) -> Dict:
    """异步抓取单个平台数据"""
    try:
        async with session.get(
            platform['url'],
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return await response.json()
    except Exception as e:
        logger.error(f"抓取失败: {platform['name']}, {e}")
        return None

async def fetch_all_platforms(platforms: List[Dict]) -> List[Dict]:
    """并发抓取所有平台"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_platform_async(session, p)
            for p in platforms
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

2. **兼容性设计**
   - 保留同步版本作为备选
   - 提供配置开关切换
   - 异步版本默认启用

3. **错误处理**
   - 单个平台失败不影响整体
   - 超时自动重试（最多 3 次）
   - 失败平台记录日志

**验收标准**：
- [ ] 并发抓取功能实现
- [ ] 性能提升 ≥ 60%
- [ ] 错误处理完善
- [ ] 稳定性测试通过

#### P0.4 单元测试框架
**目标**：建立完善的测试体系，核心功能覆盖率 ≥ 60%

**详细需求**：

1. **测试框架选择**
   - pytest：主测试框架
   - pytest-cov：覆盖率统计
   - pytest-asyncio：异步测试支持
   - pytest-mock：Mock 支持

2. **测试用例设计**
```python
# tests/test_fetcher.py
import pytest
from trendradar.core.fetcher import DataFetcher

@pytest.fixture
def fetcher():
    return DataFetcher(config={})

def test_fetch_single_platform(fetcher):
    """测试单平台抓取"""
    result = fetcher.fetch_platform('baidu')
    assert result is not None
    assert 'data' in result

@pytest.mark.asyncio
async def test_fetch_all_platforms_async(fetcher):
    """测试并发抓取"""
    results = await fetcher.fetch_all_async()
    assert len(results) > 0
```

3. **CI/CD 集成**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest tests/ -v --cov=trendradar --cov-report=html
```

**验收标准**：
- [ ] 测试框架配置完成
- [ ] 核心模块测试覆盖率 ≥ 60%
- [ ] CI/CD 自动测试运行
- [ ] 覆盖率报告生成

### 2.2 P1 - 应该实现（稳定性提升）

#### P1.1 错误处理增强
**目标**：精细化异常处理，提升系统健壮性

**详细需求**：

1. **异常分类处理**
```python
# 网络异常
try:
    response = requests.get(url, timeout=10)
except requests.Timeout:
    logger.warning(f"请求超时: {url}")
    return None
except requests.ConnectionError:
    logger.error(f"连接失败: {url}")
    return None

# 数据异常
try:
    data = response.json()
except json.JSONDecodeError:
    logger.error(f"JSON解析失败: {url}")
    return None
```

2. **重试机制**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(url: str) -> Dict:
    """带重试的数据抓取"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

3. **错误上报**
   - 关键错误发送通知
   - 错误统计和分析
   - 定期错误报告

**验收标准**：
- [ ] 所有网络请求有异常处理
- [ ] 关键操作有重试机制
- [ ] 错误日志清晰可追溯

#### P1.2 配置验证
**目标**：启动时验证配置合法性，提供友好错误提示

**详细需求**：

1. **配置文件 Schema**
```python
from pydantic import BaseModel, validator

class WeightConfig(BaseModel):
    rank_weight: float
    frequency_weight: float
    hotness_weight: float
    
    @validator('*')
    def check_weight_range(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('权重必须在 0-1 之间')
        return v
    
    @validator('hotness_weight')
    def check_weight_sum(cls, v, values):
        total = v + values.get('rank_weight', 0) + values.get('frequency_weight', 0)
        if abs(total - 1.0) > 0.01:
            raise ValueError(f'权重总和必须为 1.0，当前为 {total}')
        return v
```

2. **启动检查清单**
   - 配置文件存在性
   - 必需字段完整性
   - 数值范围合法性
   - Webhook URL 格式正确性
   - 关键词文件格式正确性

3. **友好错误提示**
```python
try:
    config = load_config()
except ConfigError as e:
    print(f"""
    ❌ 配置错误：{e.message}
    
    📝 解决方案：
    {e.solution}
    
    📖 详细文档：
    https://github.com/sansan0/TrendRadar#配置指南
    """)
    sys.exit(1)
```

**验收标准**：
- [ ] 配置验证完整
- [ ] 错误提示清晰友好
- [ ] 启动检查覆盖所有关键配置

#### P1.3 数据验证
**目标**：对 API 返回数据进行格式验证

**详细需求**：

1. **API 响应校验**
```python
def validate_news_data(data: Dict) -> bool:
    """验证新闻数据格式"""
    required_fields = ['title', 'url', 'rank']
    
    if not isinstance(data, dict):
        logger.error("数据格式错误：不是字典类型")
        return False
    
    for field in required_fields:
        if field not in data:
            logger.error(f"缺少必需字段：{field}")
            return False
    
    return True
```

2. **数据清洗**
   - 标题去除特殊字符
   - URL 格式验证
   - 排名数值范围检查
   - 时间戳格式统一

3. **异常数据处理**
   - 记录异常数据日志
   - 统计异常数据比例
   - 超过阈值发送告警

**验收标准**：
- [ ] API 数据有完整校验
- [ ] 异常数据有日志记录
- [ ] 数据清洗规则完善

### 2.3 P2 - 可以实现（新功能扩展）

#### P2.1 SQLite 数据库存储
**目标**：结构化存储历史数据，支持查询和统计

**功能范围**：
- 新闻数据持久化
- 历史数据查询
- 热点趋势统计
- 数据迁移工具

**优先级**：低（v3.1 考虑）

#### P2.2 AI 分析功能
**目标**：智能新闻摘要和趋势预测

**功能范围**：
- 新闻自动摘要
- 情感分析
- 热点趋势预测
- 相关新闻聚合

**优先级**：中（v3.2 考虑）

#### P2.3 Web 管理界面
**目标**：可视化配置和数据展示

**功能范围**：
- 在线配置编辑
- 数据可视化展示
- 实时监控面板
- 用户权限管理

**优先级**：低（v3.3 考虑）

## 三、技术方案

### 3.1 技术栈

**核心依赖**：
- Python 3.8+
- requests / aiohttp（HTTP 客户端）
- PyYAML（配置管理）
- pytz（时区处理）

**开发依赖**：
- pytest（测试框架）
- pytest-cov（覆盖率）
- pytest-asyncio（异步测试）
- black（代码格式化）
- mypy（类型检查）
- tenacity（重试机制）
- pydantic（数据验证）

### 3.2 性能优化方案

**并发抓取**：
- 使用 asyncio 事件循环
- aiohttp 作为异步 HTTP 客户端
- 并发数控制在 10 以内
- 单平台超时 10 秒

**内存优化**：
- 流式处理大文件
- 及时释放不用的数据
- 使用生成器减少内存占用

**缓存策略**：
- 配置文件缓存（文件 MD5 校验）
- 关键词匹配结果缓存
- 权重计算结果缓存

### 3.3 安全方案

**敏感信息保护**：
- Webhook URL 加密存储
- 环境变量优先级最高
- 配置文件安全提示

**输入验证**：
- 配置文件格式验证
- API 返回数据验证
- 用户输入转义

**访问控制**：
- API 请求频率限制
- 失败次数限制
- IP 白名单（可选）

## 四、开发计划

### 4.1 里程碑

**M1: v3.0-alpha（Week 3）**
- ✅ 模块化重构完成
- ✅ 日志系统升级
- ✅ 并发抓取实现
- ✅ 测试覆盖率 ≥ 60%

**M2: v3.0-beta（Week 4）**
- ✅ 错误处理完善
- ✅ 配置验证完成
- ✅ 数据验证完成
- ✅ 稳定性测试通过

**M3: v3.0（Week 5）**
- ✅ 所有 P0/P1 完成
- ✅ 文档更新完成
- ✅ 发布公告准备

### 4.2 资源投入

**开发人力**：1-2 人
**开发周期**：4-5 周
**测试时间**：1 周
**文档编写**：随开发进行

## 五、风险与应对

### 5.1 技术风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 重构破坏现有功能 | 高 | 中 | 充分测试，灰度发布 |
| 异步改造复杂度高 | 中 | 中 | 保留同步版本，逐步迁移 |
| 性能提升不达预期 | 中 | 低 | 性能测试，优化瓶颈 |
| 第三方依赖问题 | 高 | 低 | 锁定版本，测试兼容性 |

### 5.2 进度风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 时间估算不足 | 中 | 中 | P2 功能可延后 |
| 测试时间不够 | 高 | 低 | 提前编写测试用例 |
| 人力资源不足 | 中 | 低 | 降低 P2 优先级 |

### 5.3 外部风险

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| newsnow API 变更 | 高 | 低 | 监控 API，准备降级方案 |
| 平台反爬加强 | 中 | 中 | 增加代理池，降低频率 |
| 用户接受度低 | 低 | 低 | 保持向后兼容，充分沟通 |

## 六、成功指标

### 6.1 技术指标
- ✅ 测试覆盖率 ≥ 60%
- ✅ 数据抓取时间 < 30 秒
- ✅ 代码复杂度降低 50%
- ✅ 内存占用 < 200MB

### 6.2 质量指标
- ✅ 生产环境 Bug < 5 个/月
- ✅ 系统可用性 > 99%
- ✅ 错误处理覆盖率 100%
- ✅ 文档完整度 > 90%

### 6.3 用户指标
- ✅ 用户升级率 > 80%
- ✅ GitHub Star 增长率保持
- ✅ Issue 响应时间 < 24 小时
- ✅ 用户满意度 > 4.5/5

## 七、附录

### 7.1 参考文档
- [Python 异步编程指南](https://docs.python.org/3/library/asyncio.html)
- [pytest 文档](https://docs.pytest.org/)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)

### 7.2 相关链接
- GitHub 仓库：https://github.com/sansan0/TrendRadar
- 项目文档：README.md
- 开发规范：.cursorrules
- 实施计划：docs/implement.md

### 7.3 版本历史
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| PRD-01 | 2025-10-08 | 初始版本创建 |

---

**文档维护者**：TrendRadar 开发团队  
**最后更新**：2025-10-08

