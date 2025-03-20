from astrbot.api.all import *
import random
from collections import defaultdict
import time

@register("simple_poke_reply", "Your Name", "简洁版戳一戳回复插件", "1.0.0")
class SimplePokeReply(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.user_poke_counts = defaultdict(int)
        self.poke_timeout = 180  # 3分钟超时
        self.default_responses = ["不要戳啦", "痛痛！", "再戳就咬你！"]
        self.super_reply = "戳死你的AstrBot！"

    @event_message_type(EventMessageType.ALL)
    async def handle_poke(self, event: AstrMessageEvent):
        # 检查是否是QQ平台的戳一戳
        if event.get_platform_name() != "aiocqhttp":
            return

        if not any(isinstance(msg, Poke) for msg in event.message_obj.message):
            return

        user_id = event.get_sender_id()
        now = time.time()

        # 清理超时记录
        if user_id in self.user_poke_counts:
            self.user_poke_counts[user_id] = [
                t for t in self.user_poke_counts[user_id] if now - t < self.poke_timeout
            ]

        # 记录戳击时间
        self.user_poke_counts[user_id].append(now)
        count = len(self.user_poke_counts[user_id])

        # 回复处理
        if count <= len(self.default_responses):
            await event.send(self.default_responses[count-1])
        else:
            await self.send_super_reply(event, user_id)
            self.user_poke_counts[user_id] = []  # 重置计数

    async def send_super_reply(self, event: AstrMessageEvent, user_id: str):
        # 发送反击消息
        await event.send(self.super_reply)
        
        # 发送10次回戳
        if event.get_platform_name() == "aiocqhttp":
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
            assert isinstance(event, AiocqhttpMessageEvent)
            client = event.bot
            group_id = event.get_group_id()
            
            for _ in range(10):
                try:
                    await client.api.call_action(
                        'send_poke',
                        user_id=user_id,
                        group_id=group_id if group_id else None
                    )
                except Exception as e:
                    pass