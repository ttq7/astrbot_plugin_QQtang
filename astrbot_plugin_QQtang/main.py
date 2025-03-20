from astrbot.api.event import filter, AstrMessageEvent, EventMessageType
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import *
import random
from collections import defaultdict

@register(
    "qq_poke_reply",
    "ttq",
    "对戳一戳进行反击",
    "v1.1",
    "https://github.com/ttq7/astrbot_plugin_QQtang"
)
class QQPokeReplyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.poke_counts = defaultdict(int)
        self.config = context.get_plugin_config(self)

    @filter.event_message_type(EventMessageType.ALL)
    async def handle_poke(self, event: AstrMessageEvent):
        # 检查是否是QQ平台的戳一戳消息
        if event.get_platform_name() != "aiocqhttp":
            return

        # 检查消息链中是否包含Poke组件
        if not any(isinstance(msg, Poke) for msg in event.message_obj.message):
            return

        user_id = event.get_sender_id()
        self.poke_counts[user_id] += 1

        # 回戳处理
        await self.send_poke_back(event, user_id)

        # 回复消息处理
        reply_msgs = self.config.get("reply_messages", ["不要戳了", "好痛", "啊呀"])
        max_pokes = self.config.get("max_pokes_before_reply", 3)
        if self.poke_counts[user_id] <= max_pokes:
            await event.send(random.choice(reply_msgs))
        else:
            await event.send("戳死你的AstrBot！")
            self.poke_counts[user_id] = 0  # 重置计数

    async def send_poke_back(self, event: AstrMessageEvent, user_id):
        """发送回戳消息"""
        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
        assert isinstance(event, AiocqhttpMessageEvent)

        # 根据场景选择发送方式
        if event.get_group_id():
            await event.bot.api.call_action(
                'send_group_msg',
                group_id=event.get_group_id(),
                message=f'[CQ:poke,qq={user_id}]'
            )
        else:
            await event.bot.api.call_action(
                'send_private_msg',
                user_id=user_id,
                message=f'[CQ:poke,qq={user_id}]'
            )
