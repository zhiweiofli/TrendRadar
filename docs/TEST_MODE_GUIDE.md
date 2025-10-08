# Test Mode Usage Guide

## Overview

Test mode is a debugging feature that helps you verify news fetch functionality and troubleshoot issues. When enabled, it provides detailed logging and debug information without sending notifications.

## How to Enable Test Mode

### Method 1: Using config.yaml

Edit `config/config.yaml`:

```yaml
app:
  test_mode: true  # Enable test mode
```

### Method 2: Using Environment Variable

```bash
export TEST_MODE=true
python main.py
```

### Method 3: Using GitHub Actions Secret

1. Go to your repository Settings → Secrets and variables → Actions
2. Add a new secret named `TEST_MODE` with value `true`
3. The workflow will automatically use this setting

## Test Mode Features

When test mode is enabled:

1. **🔍 Detailed Debug Logging**
   - Shows detailed crawl information for each platform
   - Displays request/response details
   - Shows retry attempts and failures

2. **📊 Crawl Statistics**
   - Number of news items fetched per platform
   - Failed platforms list
   - Total news count

3. **📄 Enhanced HTML Report**
   - Orange gradient header (instead of purple) to indicate test mode
   - Debug information section at the top
   - Shows "🧪 测试模式" as report type
   - All standard news analysis features

4. **🚫 Automatic Notification Disable**
   - All webhook notifications are disabled
   - Prevents test data from being sent to production channels

5. **📱 GitHub Pages Integration**
   - Automatically publishes test results to GitHub Pages
   - Generates `index.html` with test mode indicator
   - Updates with each test run

## Example Output

### Console Output

```
============================================================
🧪 测试模式已启用（TEST_MODE=True）
============================================================
📋 测试模式说明:
  - 显示详细的调试信息
  - 显示每个平台的抓取详情
  - 生成包含调试信息的HTML报告
  - 禁用通知推送
============================================================

配置的监控平台: ['今日头条', '百度热搜', '华尔街见闻', ...]
开始爬取数据，请求间隔 1000 毫秒

============================================================
🔍 测试模式 - 详细抓取信息:
============================================================
请求 toutiao 成功: 50 条新闻
请求 baidu 成功: 30 条新闻
...

============================================================
📊 测试模式 - 抓取结果统计:
============================================================
  今日头条 (toutiao): 50 条新闻
  百度热搜 (baidu): 30 条新闻
  ❌ 失败的平台: weibo
============================================================
```

### HTML Report Features

The generated HTML report will have:
- Orange gradient header indicating test mode
- "🧪 测试模式" label in report type
- Debug information box with:
  - Test mode explanation
  - Features list
  - Total news count
  - Platform statistics

## Use Cases

### 1. Debugging Configuration Issues

```bash
# Enable test mode to see detailed logs
export TEST_MODE=true
python main.py
```

Check the console output for:
- Configuration loading errors
- Platform connection issues
- Data parsing problems

### 2. Verifying News Sources

Test mode helps verify that all configured news sources are working:
- Shows which platforms succeed/fail
- Displays the number of news items per platform
- Helps identify rate limiting or API issues

### 3. Testing Keyword Matching

Use test mode to verify your `frequency_words.txt` configuration:
- See which news items match your keywords
- Verify filtering is working correctly
- Check if new keywords are effective

### 4. GitHub Pages Preview

Enable test mode to preview how reports will look on GitHub Pages:
- See the visual design
- Check mobile responsiveness
- Verify all links work correctly

## Best Practices

1. **Always use test mode when making config changes**
   ```bash
   # Before production
   TEST_MODE=true python main.py
   ```

2. **Check test mode output before enabling notifications**
   - Verify data quality
   - Confirm platforms are working
   - Review keyword matches

3. **Use test mode for troubleshooting**
   - Network issues
   - Platform API changes
   - Parsing errors

4. **Disable test mode in production**
   ```yaml
   app:
     test_mode: false  # Production setting
   ```

## Disabling Test Mode

### Method 1: Edit config.yaml

```yaml
app:
  test_mode: false
```

### Method 2: Remove Environment Variable

```bash
unset TEST_MODE
```

### Method 3: Remove GitHub Secret

1. Go to repository Settings → Secrets and variables → Actions
2. Delete the `TEST_MODE` secret

## Troubleshooting

### Test Mode Not Working

1. **Check config file**
   ```bash
   grep test_mode config/config.yaml
   ```

2. **Check environment variable**
   ```bash
   echo $TEST_MODE
   ```

3. **Verify logs show test mode activation**
   - Look for "🧪 测试模式已启用" in output

### No Debug Information

- Ensure you're looking at the correct output (stdout, not log files)
- Check that TEST_MODE is actually set to `true` (not `True` or `1`)

### GitHub Pages Not Updating

- Check that GitHub Actions has write permissions
- Verify workflow runs successfully
- Check the `index.html` file in repository root

## Related Documentation

- [Main README](../readme.md)
- [Configuration Guide](../config/config.yaml)
- [Frequency Words Guide](../config/frequency_words.txt)
