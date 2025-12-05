# 🚀 部署说明（方案 A）

## GitHub Pages 配置

本项目使用独立的 `gh-pages` 分支部署 GitHub Pages，避免主分支频繁 commit。

**首次设置步骤**：

1. 进入仓库 **Settings → Pages**
2. **Source** 选择：`Deploy from a branch`
3. **Branch** 选择：`gh-pages` / `/ (root)`
4. 点击 **Save**

## 数据存储策略

| 数据类型 | 存储位置 | 保留时间 | 说明 |
|---------|---------|---------|------|
| HTML 报告 | gh-pages 分支 | 永久（覆盖更新） | 用于 GitHub Pages 展示 |
| Output 数据 | GitHub Actions Artifacts | 7 天 | 可通过 Actions 页面下载 |
| 源代码 | main 分支 | 永久 | 仅在代码变更时提交 |

## 运行频率

- ⏰ **定时任务**：每小时运行一次（`cron: "0 * * * *"`）
- 📊 **页面更新**：每小时自动更新（通过 gh-pages 分支）
- 💾 **数据备份**：最近 7 天数据可在 Artifacts 中下载

## 查看历史数据

1. 进入仓库 **Actions** 页面
2. 选择 **Hot News Crawler** workflow
3. 点击具体的运行记录
4. 在 **Artifacts** 区域下载 `trend-reports-*` 文件

## 优势

✅ 主分支不再频繁提交，Git 历史保持清爽  
✅ GitHub Pages 仍然每小时更新  
✅ 历史数据有 7 天缓冲期  
✅ 避免 GitHub 页面 503 错误  
✅ 完全免费，无需第三方服务
