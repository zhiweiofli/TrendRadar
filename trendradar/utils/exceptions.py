"""
自定义异常类
"""


class TrendRadarError(Exception):
    """TrendRadar 基础异常类"""

    pass


class ConfigError(TrendRadarError):
    """配置错误

    用于配置文件格式错误、缺少必需字段等场景
    """

    def __init__(self, message: str, solution: str = ""):
        """初始化配置错误

        Args:
            message: 错误信息
            solution: 解决方案提示
        """
        self.message = message
        self.solution = solution
        super().__init__(self.message)

    def __str__(self) -> str:
        """格式化错误信息"""
        if self.solution:
            return f"{self.message}\n\n解决方案：{self.solution}"
        return self.message


class FetchError(TrendRadarError):
    """数据抓取错误"""

    pass


class ValidationError(TrendRadarError):
    """数据验证错误"""

    pass


class NotificationError(TrendRadarError):
    """通知推送错误"""

    pass
