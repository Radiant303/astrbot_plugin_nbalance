import asyncio

import aiohttp

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter
from astrbot.api.star import Context, Star, register


@register("astrbot_plugin_nbalance", "Radiant303", "查询 NewAPI 用户余额", "v1.0.0")
class BalancePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 新的配置项
        self.api_config = self.config.get("api_config", "https://newapi.com").rstrip(
            "/"
        )
        self.userid = self.config.get("userid", "10001")
        self.token = self.config.get("token", "token")
        self.enable_llm_tool: bool = self.config.get("enable_llm_tool", False)

        self.session: aiohttp.ClientSession | None = None

    async def initialize(self):
        logger.info("BalancePlugin initialize called")

    async def terminate(self):
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("BalancePlugin 已卸载")

    def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    @filter.command("余额")
    async def balance(self, event: AstrMessageEvent):
        result = await self._query_balance()
        yield event.plain_result(result)

    @filter.llm_tool(name="query_balance")
    async def query_balance(self, event: AstrMessageEvent) -> MessageEventResult:
        """
        查询并返回当前配置的所有余额信息
        """
        if not self.enable_llm_tool:
            yield event.plain_result("余额查询 LLM 工具未启用")
            return

        result = await self._query_balance()
        yield event.plain_result(result)

    async def _query_balance(self) -> str:
        # 构建完整 URL
        url = f"{self.api_config}/api/user/self"

        # 构建请求头
        headers = {"New-API-User": self.userid, "Authorization": f"Bearer {self.token}"}

        self._ensure_session()

        try:
            async with self.session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    logger.warning(f"查询余额失败，HTTP {resp.status}")
                    return f"查询失败，状态码: {resp.status}"

                data = await resp.json()

                # 解析响应数据（根据常见的 NewAPI 返回格式）
                # 假设返回格式: {"success": true, "data": {"balance": 100, "used": 50, "total": 150}}
                if not data.get("success", True):
                    error_msg = data.get("message", "未知错误")
                    return f"查询失败: {error_msg}"

                user_data = data.get("data", {})

                # 提取余额信息（根据实际 API 返回调整字段名）
                balance = user_data.get("quota", "N/A")

                # 格式化输出 500000是newapi的汇率
                huilv = 500000
                result = f"{float(balance) / huilv:.2f}美元"

                return result

        except asyncio.TimeoutError:
            logger.error("查询余额超时")
            return "查询超时，请稍后重试"
        except aiohttp.ClientError as e:
            logger.error(f"网络请求错误: {e}")
            return f"网络错误: {str(e)}"
        except Exception as e:
            logger.error(f"查询余额异常: {type(e).__name__}: {e}")
            return f"查询异常: {str(e)}"
