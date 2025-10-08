# TrendRadar v3.0 升级指南

## 概述

TrendRadar v3.0 是一个重大版本更新，进行了全面的架构重构和性能优化。本文档将指导你从 v2.x 顺利升级到 v3.0。

## 🎯 升级收益

- ⚡ **性能提升 3 倍**：异步并发抓取，11 个平台从 60 秒降至 20 秒
- 📝 **完善的日志系统**：便于问题排查和监控
- ✅ **配置自动验证**：启动时检查配置，友好的错误提示
- 🧪 **完整的测试覆盖**：更稳定可靠
- 🔧 **更好的错误处理**：自动重试，优雅降级

## 📋 升级前准备

### 1. 备份数据

```bash
# 备份配置文件
cp config/config.yaml config/config.yaml.backup
cp config/frequency_words.txt config/frequency_words.txt.backup

# 备份输出数据（可选）
cp -r output output_backup
```

### 2. 检查 Python 版本

v3.0 支持 Python 3.8 - 3.11：

```bash
python --version
# 或
python3 --version
```

如果版本过低，请先升级 Python。

## 🚀 升级步骤

### 方式一：Git 拉取（推荐）

如果你是通过 Git 克隆的项目：

```bash
# 1. 进入项目目录
cd TrendRadar

# 2. 拉取最新代码
git pull origin master

# 3. 安装新依赖
pip install -r requirements.txt

# 4. 运行测试（可选但推荐）
pip install -r requirements-dev.txt
pytest trendradar/tests/ -v

# 5. 启动程序
python main.py
```

### 方式二：手动下载

如果你是手动下载的：

```bash
# 1. 下载最新版本
# 访问 https://github.com/sansan0/TrendRadar/releases

# 2. 解压到新目录
unzip TrendRadar-v3.0.zip

# 3. 复制配置文件
cp old_trendradar/config/config.yaml TrendRadar-v3.0/config/
cp old_trendradar/config/frequency_words.txt TrendRadar-v3.0/config/

# 4. 进入新目录并安装依赖
cd TrendRadar-v3.0
pip install -r requirements.txt

# 5. 启动程序
python main.py
```

## ⚙️ 配置变更

### 新增配置项

在 `config/config.yaml` 中新增了异步开关：

```yaml
crawler:
  enable_async: true  # 是否启用异步并发抓取，默认 true
```

**建议**：
- 首次升级：保持 `enable_async: true`，享受 3 倍性能提升
- 遇到问题：可临时设置为 `false` 切换回同步模式

### 配置文件验证

v3.0 会在启动时自动验证配置：

```bash
python main.py
```

如果配置有误，会看到类似提示：

```
❌ 配置错误：权重总和必须为 1.0，当前为 0.95

📝 解决方案：
请调整三个权重值，使其总和等于 1.0

📖 详细文档：
https://github.com/sansan0/TrendRadar#配置指南
```

## 🔍 验证升级

### 1. 功能测试

```bash
# 启动程序
python main.py

# 查看日志输出
# 应该看到：
# - "开始异步并发抓取 11 个平台"（如果启用异步）
# - "异步抓取完成: 成功 11/11, 耗时 20.xx秒"
```

### 2. 性能对比

观察日志中的抓取时间：

```
# v2.2.0（同步模式）
INFO - 抓取完成: 耗时 60.xx秒

# v3.0（异步模式）
INFO - 异步抓取完成: 成功 11/11, 耗时 20.xx秒
```

### 3. 运行测试（可选）

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest trendradar/tests/ -v

# 应该看到：
# ====== 30 passed in 10.xx seconds ======
```

## 🐛 常见问题

### Q1: 升级后报错 "No module named 'aiohttp'"

**原因**：未安装新依赖

**解决**：
```bash
pip install -r requirements.txt
# 或
pip install aiohttp==3.9.5
```

### Q2: 异步模式下抓取失败

**现象**：看到大量 "异步抓取失败" 日志

**解决**：
```yaml
# 临时切换回同步模式
crawler:
  enable_async: false
```

然后提交 Issue 报告问题。

### Q3: 配置验证失败

**现象**：启动时提示配置错误

**解决**：
1. 仔细阅读错误提示和解决方案
2. 对照 `config/config.yaml` 修复问题
3. 如果不确定，可以使用备份的配置文件

### Q4: GitHub Actions 中如何使用 v3.0？

**回答**：GitHub Actions 完全支持 asyncio 和 aiohttp，无需特殊配置。

在 workflow 中：
```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt

- name: Run TrendRadar
  run: python main.py
```

## 📊 性能监控

### 查看日志

v3.0 会在 `logs/` 目录生成详细日志：

```bash
# 查看最新日志
tail -f logs/trendradar.log

# 搜索错误
grep ERROR logs/trendradar.log

# 查看抓取性能
grep "抓取完成" logs/trendradar.log
```

### 性能指标

正常情况下应该看到：

```
INFO - 异步抓取完成: 成功 11/11, 耗时 15-25秒
```

如果耗时超过 30 秒或成功率低于 90%，请检查：
1. 网络连接
2. API 服务状态
3. 日志中的错误信息

## 🔄 回滚方案

如果升级后遇到严重问题，可以快速回滚：

### Git 用户

```bash
# 回滚到上一个版本
git checkout v2.2.0

# 恢复配置（如果有修改）
cp config/config.yaml.backup config/config.yaml

# 重新安装依赖
pip install -r requirements.txt
```

### 手动下载用户

```bash
# 切换回旧版本目录
cd old_trendradar

# 启动
python main.py
```

## 🆘 获取帮助

如果升级过程中遇到问题：

1. **查看文档**：
   - 主文档：`README.md`
   - 开发规范：`.cursorrules`
   - 实施计划：`docs/implement.md`

2. **提交 Issue**：
   - GitHub Issues: https://github.com/sansan0/TrendRadar/issues
   - 请提供：
     - 错误信息
     - 日志文件
     - Python 版本
     - 操作系统

3. **社区支持**：
   - 公众号：硅基茶水间

## 🎯 下一步

升级成功后，你可以：

1. **体验性能提升**：对比升级前后的抓取速度
2. **查看日志**：了解系统运行状况
3. **调整配置**：根据需要优化权重和通知
4. **参与贡献**：提交 PR 或反馈建议

---

**祝升级顺利！** 🎉

如有任何问题，欢迎通过 GitHub Issues 联系我们。

