from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
import httpx
import json


@register("http_bridge", "FlyModeZ", "", "0.1.2")
class HttpBridge(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        
        self.http_endpoint = config.get("http_endpoint")

    async def initialize(self):
        self.client = httpx.AsyncClient(http2=True, timeout=10.0)
        logger.info("HTTP 客户端已初始化。")

    async def terminate(self):
        if self.client:
            await self.client.aclose()
            logger.info("HTTP 客户端已关闭。")

    # @filter.event_message_type(filter.EventMessageType.ALL, priority=10)
    @filter.command("fm")
    async def bridge(self, event: AstrMessageEvent, content: str):
        event.stop_event()

        payload = {
            "user": event.unified_msg_origin,
            "text": content
        }

        async with self.client.stream("POST", self.http_endpoint, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield event.plain_result(data.get("text"))
