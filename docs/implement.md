# TrendRadar v3.0 实施计划

## 文档信息

| 项目 | 内容 |
|------|------|
| 计划名称 | TrendRadar v3.0 重构实施计划 |
| 计划版本 | v1.0 |
| 创建日期 | 2025-10-08 |
| 计划周期 | 4-5 周 |
| 负责人 | 开发团队 |

## 一、总体策略

### 1.1 核心原则

1. **渐进式重构**：分阶段进行，每个阶段保持系统可用
2. **向后兼容**：确保用户无感知升级
3. **测试先行**：每个模块都要有充分的测试覆盖
4. **文档同步**：代码和文档同步更新

### 1.2 质量保证

- 每个阶段都有明确的验收标准
- 每次提交都要通过 CI/CD 检查
- 关键节点进行代码审查
- 定期进行性能测试

### 1.3 风险控制

- 保持主分支稳定
- 功能在分支开发和测试
- 使用 feature flag 控制新功能
- 准备回滚方案

## 二、阶段一：基础重构

### 项目结构调整

#### 目标
建立模块化基础，完成第一批模块拆分

#### 任务清单

**1: 创建目录结构**

```bash
# 创建项目目录
mkdir -p trendradar/{core,notifiers,utils,tests}

# 创建 __init__.py 文件
touch trendradar/__init__.py
touch trendradar/core/__init__.py
touch trendradar/notifiers/__init__.py
touch trendradar/utils/__init__.py
touch trendradar/tests/__init__.py
```

**2: 提取工具函数**

1. **创建 utils/time_utils.py**
```python
"""时间处理工具函数"""
import pytz
from datetime import datetime

def get_beijing_time() -> datetime:
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))

def format_date_folder() -> str:
    """格式化日期文件夹"""
    return get_beijing_time().strftime("%Y年%m月%d日")

def format_time_filename() -> str:
    """格式化时间文件名"""
    return get_beijing_time().strftime("%H时%M分")
```

2. **创建 utils/file_utils.py**
```python
"""文件操作工具函数"""
from pathlib import Path

def ensure_directory_exists(directory: str) -> None:
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_output_path(subfolder: str, filename: str) -> str:
    """获取输出路径"""
    from .time_utils import format_date_folder
    date_folder = format_date_folder()
    output_dir = Path("output") / date_folder / subfolder
    ensure_directory_exists(str(output_dir))
    return str(output_dir / filename)
```

3. **创建 utils/config.py**
```python
"""配置管理"""
import os
import yaml
from pathlib import Path
from typing import Dict

def load_config() -> Dict:
    """加载配置文件"""
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")
    
    if not Path(config_path).exists():
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # 构建配置字典...
    return config_data
```

**3: 提取数据抓取模块**

1. **创建 core/fetcher.py**
```python
"""数据抓取模块"""
import requests
from typing import Dict, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DataFetcher:
    """数据抓取器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.platforms = config.get('PLATFORMS', [])
    
    def fetch_platform(self, platform: Dict) -> Optional[Dict]:
        """抓取单个平台数据"""
        try:
            response = requests.get(
                platform['url'],
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"抓取失败: {platform['name']}, {e}")
            return None
    
    def fetch_all(self) -> List[Dict]:
        """抓取所有平台数据"""
        results = []
        for platform in self.platforms:
            data = self.fetch_platform(platform)
            if data:
                results.append(data)
        return results
```

**验收标准**：
- [ ] 目录结构创建完成
- [ ] 工具函数提取并测试通过
- [ ] main.py 能正常导入新模块
- [ ] 原有功能完全正常

---

### 日志系统 + 测试框架

#### 目标
建立日志和测试基础设施

#### 任务清单

**1: 实现日志系统**

1. **创建 utils/logger.py**
```python
"""日志系统配置"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO"
) -> logging.Logger:
    """配置日志系统
    
    Args:
        name: 日志名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """获取 Logger 实例"""
    return logging.getLogger(name)
```

2. **在各模块中使用日志**
```python
# 示例：在 core/fetcher.py 中
from ..utils.logger import get_logger

logger = get_logger(__name__)

def fetch_platform(self, platform: Dict) -> Optional[Dict]:
    logger.info(f"开始抓取: {platform['name']}")
    try:
        # ...
        logger.info(f"抓取成功: {platform['name']}")
        return data
    except Exception as e:
        logger.error(f"抓取失败: {platform['name']}, {e}")
        return None
```

**2: 搭建测试框架**

1. **安装测试依赖**
```bash
# requirements-dev.txt
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.21.0
pytest-mock==3.11.1
black==23.7.0
mypy==1.4.1
isort==5.12.0
```

2. **创建 pytest 配置**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=trendradar
    --cov-report=html
    --cov-report=term-missing
```

3. **创建测试配置**
```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_config():
    """测试用配置"""
    return {
        'PLATFORMS': [
            {'id': 'baidu', 'name': '百度热搜'}
        ],
        'RANK_THRESHOLD': 5
    }

@pytest.fixture
def temp_output_dir(tmp_path):
    """临时输出目录"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

4. **编写第一批测试**
```python
# tests/test_time_utils.py
from trendradar.utils.time_utils import (
    get_beijing_time,
    format_date_folder,
    format_time_filename
)

def test_get_beijing_time():
    """测试获取北京时间"""
    time = get_beijing_time()
    assert time.tzinfo is not None
    assert time.tzinfo.zone == 'Asia/Shanghai'

def test_format_date_folder():
    """测试日期格式化"""
    folder = format_date_folder()
    assert '年' in folder
    assert '月' in folder
    assert '日' in folder

def test_format_time_filename():
    """测试时间格式化"""
    filename = format_time_filename()
    assert '时' in filename
    assert '分' in filename
```

```python
# tests/test_fetcher.py
import pytest
from unittest.mock import Mock, patch
from trendradar.core.fetcher import DataFetcher

def test_data_fetcher_init(sample_config):
    """测试 DataFetcher 初始化"""
    fetcher = DataFetcher(sample_config)
    assert fetcher.config == sample_config
    assert len(fetcher.platforms) == 1

@patch('requests.get')
def test_fetch_platform_success(mock_get, sample_config):
    """测试成功抓取平台数据"""
    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {'data': []}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    fetcher = DataFetcher(sample_config)
    platform = {'name': '测试平台', 'url': 'http://test.com'}
    result = fetcher.fetch_platform(platform)
    
    assert result is not None
    assert 'data' in result

@patch('requests.get')
def test_fetch_platform_failure(mock_get, sample_config):
    """测试抓取失败"""
    mock_get.side_effect = Exception("网络错误")
    
    fetcher = DataFetcher(sample_config)
    platform = {'name': '测试平台', 'url': 'http://test.com'}
    result = fetcher.fetch_platform(platform)
    
    assert result is None
```

**3: 配置 CI/CD**

1. **创建 GitHub Actions 工作流**
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=trendradar --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

**验收标准**：
- [ ] 日志系统配置完成
- [ ] 日志文件正常生成
- [ ] 测试框架运行正常
- [ ] 测试覆盖率 ≥ 30%
- [ ] CI/CD 自动运行

---

### 并发抓取实现

#### 目标
实现异步并发抓取，性能提升 3-5 倍

#### 任务清单

**1: 实现异步抓取**

1. **创建异步版本的 DataFetcher**
```python
# core/fetcher.py (新增异步方法)
import asyncio
import aiohttp
from typing import List, Dict, Optional

class DataFetcher:
    """数据抓取器（同时支持同步和异步）"""
    
    async def fetch_platform_async(
        self,
        session: aiohttp.ClientSession,
        platform: Dict
    ) -> Optional[Dict]:
        """异步抓取单个平台数据"""
        logger.info(f"开始异步抓取: {platform['name']}")
        
        try:
            async with session.get(
                platform['url'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"抓取成功: {platform['name']}")
                return data
        except asyncio.TimeoutError:
            logger.error(f"抓取超时: {platform['name']}")
            return None
        except Exception as e:
            logger.error(f"抓取失败: {platform['name']}, {e}")
            return None
    
    async def fetch_all_async(self) -> List[Dict]:
        """异步抓取所有平台数据"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_platform_async(session, platform)
                for platform in self.platforms
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤掉失败的结果
            valid_results = [
                r for r in results
                if r is not None and not isinstance(r, Exception)
            ]
            
            logger.info(f"异步抓取完成: 成功 {len(valid_results)}/{len(self.platforms)}")
            return valid_results
    
    def fetch_all_sync(self) -> List[Dict]:
        """同步抓取（原有方法）"""
        return self.fetch_all()  # 保留原实现
```

2. **添加配置开关**
```yaml
# config/config.yaml
crawler:
  enable_async: true  # 是否启用异步抓取
  request_interval: 1000
```

3. **在 main.py 中使用**
```python
def main():
    config = load_config()
    fetcher = DataFetcher(config)
    
    # 根据配置选择同步或异步
    if config.get('ENABLE_ASYNC', True):
        results = asyncio.run(fetcher.fetch_all_async())
    else:
        results = fetcher.fetch_all_sync()
```

**2: 添加性能测试**

```python
# tests/test_performance.py
import pytest
import time
from trendradar.core.fetcher import DataFetcher

@pytest.mark.asyncio
async def test_async_performance(sample_config):
    """测试异步抓取性能"""
    fetcher = DataFetcher(sample_config)
    
    start = time.time()
    results = await fetcher.fetch_all_async()
    duration = time.time() - start
    
    assert len(results) > 0
    assert duration < 30  # 应该在30秒内完成

def test_sync_performance(sample_config):
    """测试同步抓取性能"""
    fetcher = DataFetcher(sample_config)
    
    start = time.time()
    results = fetcher.fetch_all_sync()
    duration_sync = time.time() - start
    
    # 记录性能数据用于对比
    pytest.benchmark_sync_duration = duration_sync
```

**3: 优化错误处理**

```python
# core/fetcher.py 增强错误处理
from tenacity import retry, stop_after_attempt, wait_exponential

class DataFetcher:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def fetch_platform_async_with_retry(
        self,
        session: aiohttp.ClientSession,
        platform: Dict
    ) -> Optional[Dict]:
        """带重试的异步抓取"""
        return await self.fetch_platform_async(session, platform)
```

**验收标准**：
- [ ] 异步抓取功能实现
- [ ] 性能提升 ≥ 60%
- [ ] 单平台失败不影响整体
- [ ] 错误处理完善
- [ ] 测试覆盖率 ≥ 60%

---

## 三、阶段二：稳定性提升

### 错误处理 + 配置验证

#### 目标
增强系统健壮性和用户体验

#### 任务清单

**1、: 精细化异常处理**

```python
# utils/exceptions.py
"""自定义异常类"""

class TrendRadarError(Exception):
    """基础异常类"""
    pass

class ConfigError(TrendRadarError):
    """配置错误"""
    def __init__(self, message: str, solution: str = ""):
        self.message = message
        self.solution = solution
        super().__init__(self.message)

class FetchError(TrendRadarError):
    """数据抓取错误"""
    pass

class ValidationError(TrendRadarError):
    """数据验证错误"""
    pass
```

**2、: 配置验证器**

```python
# utils/validator.py
"""配置验证"""
from typing import Dict
import re
from .exceptions import ConfigError

class ConfigValidator:
    """配置验证器"""
    
    def validate(self, config: Dict) -> None:
        """验证配置文件"""
        self._check_required_keys(config)
        self._validate_weights(config)
        self._validate_platforms(config)
        self._validate_webhooks(config)
    
    def _check_required_keys(self, config: Dict) -> None:
        """检查必需字段"""
        required_keys = ['app', 'crawler', 'report', 'notification', 'platforms']
        for key in required_keys:
            if key not in config:
                raise ConfigError(
                    f"配置缺少必需字段: {key}",
                    f"请在 config.yaml 中添加 {key} 配置项"
                )
    
    def _validate_weights(self, config: Dict) -> None:
        """验证权重配置"""
        weights = config.get('weight', {})
        weight_sum = sum([
            weights.get('rank_weight', 0),
            weights.get('frequency_weight', 0),
            weights.get('hotness_weight', 0)
        ])
        
        if abs(weight_sum - 1.0) > 0.01:
            raise ConfigError(
                f"权重总和必须为 1.0，当前为 {weight_sum}",
                "请检查 config.yaml 中的 weight 配置"
            )
    
    def _validate_webhooks(self, config: Dict) -> None:
        """验证 Webhook URL"""
        webhooks = config.get('notification', {}).get('webhooks', {})
        
        for key, url in webhooks.items():
            if url and not url.startswith(('http://', 'https://')):
                raise ConfigError(
                    f"Webhook URL 格式错误: {key}",
                    f"{key} 必须以 http:// 或 https:// 开头"
                )
```

**3、: 数据验证与友好提示**

```python
# core/validator.py
"""数据验证"""
from typing import Dict, List
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DataValidator:
    """数据验证器"""
    
    def validate_news_item(self, item: Dict) -> bool:
        """验证单条新闻数据"""
        required_fields = ['title', 'url']
        
        for field in required_fields:
            if field not in item or not item[field]:
                logger.warning(f"新闻数据缺少字段: {field}")
                return False
        
        return True
    
    def validate_and_clean(self, items: List[Dict]) -> List[Dict]:
        """验证并清洗数据"""
        valid_items = []
        invalid_count = 0
        
        for item in items:
            if self.validate_news_item(item):
                # 清洗数据
                item['title'] = self._clean_title(item['title'])
                valid_items.append(item)
            else:
                invalid_count += 1
        
        if invalid_count > 0:
            logger.warning(f"发现 {invalid_count} 条无效数据")
        
        return valid_items
    
    def _clean_title(self, title: str) -> str:
        """清洗标题"""
        # 去除多余空格
        title = ' '.join(title.split())
        # 限制长度
        if len(title) > 200:
            title = title[:197] + '...'
        return title
```

**验收标准**：
- [ ] 所有网络请求有异常处理
- [ ] 配置启动时自动验证
- [ ] 错误提示清晰友好
- [ ] 数据验证规则完善

---

## 四、阶段三：文档与发布

### Week 5: 文档完善 + 发布准备

#### 任务清单

**1、: 更新文档**
- [ ] 更新 README.md
- [ ] 更新 .cursorrules
- [ ] 编写升级指南
- [ ] 更新 CHANGELOG.md

**2、: 性能测试**
- [ ] 压力测试
- [ ] 内存泄漏检查
- [ ] 并发测试

**3、: 发布准备**
- [ ] 版本号更新
- [ ] 打标签
- [ ] 发布说明编写

**4、: 正式发布**
- [ ] 合并到 master
- [ ] GitHub Release
- [ ] 公告发布

---

## 五、开发规范

### 5.1 每日开发流程

```bash
# 1. 拉取最新代码
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发并提交
# ... 编写代码 ...
git add .
git commit -m "feat(scope): description"

# 4. 推送并创建 PR
git push origin feature/your-feature-name
# 在 GitHub 上创建 Pull Request
```

### 5.2 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `docs`: 文档更新
- `chore`: 构建/工具变动

**示例**：
```
feat(fetcher): 实现异步并发抓取

- 使用 asyncio + aiohttp
- 性能提升 3 倍
- 添加重试机制

Closes #123
```

### 5.3 代码审查检查项

**提交 PR 前自检**：
- [ ] 代码符合规范（命名、类型注解）
- [ ] 单元测试覆盖
- [ ] 日志输出合理
- [ ] 文档已更新
- [ ] 性能无明显下降
- [ ] CI/CD 检查通过

**审查者检查项**：
- [ ] 代码逻辑正确
- [ ] 测试充分
- [ ] 无安全风险
- [ ] 性能可接受
- [ ] 文档清晰

---

## 六、里程碑与验收

### M1: v3.0-alpha（Week 3 结束）

**交付物**：
- [x] 模块化目录结构
- [x] 日志系统完整
- [x] 异步抓取功能
- [x] 测试覆盖率 ≥ 60%

**验收标准**：
- 功能完全正常
- 性能提升 ≥ 60%
- 所有测试通过
- 文档基本完善

### M2: v3.0-beta（Week 4 结束）

**交付物**：
- [x] 错误处理完善
- [x] 配置验证完成
- [x] 数据验证完成
- [x] 稳定性测试通过

**验收标准**：
- 异常情况处理完善
- 配置错误有友好提示
- 生产环境稳定运行 1 周
- Bug 数量 < 3 个

### M3: v3.0（Week 5 结束）

**交付物**：
- [x] 所有 P0/P1 完成
- [x] 文档更新完成
- [x] 发布公告准备

**验收标准**：
- 所有功能正常
- 性能达标
- 文档完整
- 用户反馈良好

---

## 七、风险应对

### 7.1 技术风险

**风险1：重构破坏现有功能**
- **应对措施**：
  - 充分的单元测试和集成测试
  - 保持双版本并存期
  - 灰度发布，逐步切换
  - 准备快速回滚方案

**风险2：异步改造复杂度高**
- **应对措施**：
  - 保留同步版本作为备选
  - 分步实现，先单个平台测试
  - 充分的性能测试
  - 社区征集反馈

**风险3：性能提升不达预期**
- **应对措施**：
  - 提前做性能基准测试
  - 识别性能瓶颈
  - 准备优化方案B
  - 必要时延后发布

### 7.2 进度风险

**风险1：时间估算不足**
- **应对措施**：
  - P2 功能可延后到 v3.1
  - 每周 review 进度
  - 及时调整计划
  - 核心功能优先

**风险2：测试时间不够**
- **应对措施**：
  - 测试用例提前编写
  - 自动化测试充分
  - 必要时延长测试周期
  - 社区测试者招募

### 7.3 外部风险

**风险1：newsnow API 变更**
- **应对措施**：
  - 监控 API 状态
  - 准备降级方案
  - 考虑多数据源
  - 与项目方沟通

**风险2：用户接受度低**
- **应对措施**：
  - 保持向后兼容
  - 充分沟通升级价值
  - 提供详细升级指南
  - 收集用户反馈快速迭代

---

## 八、资源需求

### 8.1 人力投入
- **主开发**：1-2 人
- **测试**：1 人（兼职）
- **文档**：随开发进行

### 8.2 时间投入
- **开发时间**：4 周
- **测试时间**：1 周
- **缓冲时间**：1 周
- **总计**：5-6 周

### 8.3 工具需求
- GitHub（代码托管、CI/CD）
- pytest（测试框架）
- codecov（覆盖率统计）
- 无额外成本

---

## 九、附录

### 9.1 参考资料
- [asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)
- [pytest 使用指南](https://docs.pytest.org/)
- [代码审查最佳实践](https://google.github.io/eng-practices/review/)

### 9.2 相关文档
- 产品需求：`docs/PRD-01.md`
- 开发规范：`.cursorrules`
- 项目文档：`README.md`

### 9.3 联系方式
- GitHub Issues：https://github.com/sansan0/TrendRadar/issues
- 公众号：硅基茶水间

---

**文档维护者**：TrendRadar 开发团队  
**最后更新**：2025-10-08  
**版本**：v1.0

