from src.utils.config import get as get_config, set as set_config
import botpy
from botpy import logging
from botpy.message import C2CMessage, GroupMessage
from botpy.manage import C2CManageEvent, GroupManageEvent
from src.client.router import route_message


_log = logging.get_logger()


class MainClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
        set_config("qqbot.name", self.robot.name)
        
    # ===== c2c =====
    async def on_friend_add(self, event: C2CManageEvent):
        _log.info("用户添加机器人：" + str(event))
        await self.api.post_c2c_message(
            openid=event.openid,
            msg_type=0,
            event_id=event.event_id,
            content="回复帮助或者/help查看操作说明",
        )

    async def on_friend_del(self, event: C2CManageEvent):
        _log.info("用户删除机器人：" + str(event))

    async def on_c2c_msg_reject(self, event: C2CManageEvent):
        _log.info("用户关闭机器人主动消息：" + str(event))

    async def on_c2c_msg_receive(self, event: C2CManageEvent):
        _log.info("用户打开机器人主动消息：" + str(event))
    
    async def on_c2c_message_create(self, message: C2CMessage):
        _log.info(message)
        res = await route_message(message)
        try:
            await message._api.post_c2c_message(
                openid=message.author.user_openid, 
                msg_type=res.msg_type, 
                msg_id=message.id, 
                content=res.content,
                media=res.media
            )
        except Exception as e:
            _log.error(e)
            await message._api.post_c2c_message(
                openid=message.author.user_openid, 
                msg_type=0, msg_id=message.id, 
                content="服务不可用，请稍后再试。"
            )
        
    # async def on_c2c_message_create(self, message: C2CMessage):
    #     file_url = ""  # 这里需要填写上传的资源Url
    #     uploadMedia = await message._api.post_c2c_file(
    #         openid=message.author.user_openid, 
    #         file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
    #         url=file_url # 文件Url
    #     )

    #     # 资源上传后，会得到Media，用于发送消息
    #     await message._api.post_c2c_message(
    #         openid=message.author.user_openid,
    #         msg_type=7,  # 7表示富媒体类型
    #         msg_id=message.id, 
    #         media=uploadMedia
    #     )
        
    # ===== group =====
    async def on_group_add_robot(self, event: GroupManageEvent):
        _log.info("机器人被添加到群聊：" + str(event))
        await self.api.post_group_message(
            group_openid=event.group_openid,
            msg_type=0,
            event_id=event.event_id,
            content="回复帮助或者/help查看操作说明",
        )

    async def on_group_del_robot(self, event: GroupManageEvent):
        _log.info("机器人被移除群聊：" + str(event))

    async def on_group_msg_reject(self, event: GroupManageEvent):
        _log.info("群聊关闭机器人主动消息：" + str(event))

    async def on_group_msg_receive(self, event: GroupManageEvent):
        _log.info("群聊打开机器人主动消息：" + str(event))
        
    async def on_group_at_message_create(self, message: GroupMessage):
        _log.info(message)
        res = await route_message(message)
        try:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=res.msg_type, 
                msg_id=message.id,
                content=res.content,
                media=res.media
            )
        except Exception as e:
            _log.error(e)
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, msg_id=message.id,
                content="服务不可用，请稍后再试。"
            )
        
    # async def on_group_at_message_create(self, message: GroupMessage):
    #     file_url = ""  # 这里需要填写上传的资源Url
    #     uploadMedia = await message._api.post_group_file(
    #         group_openid=message.group_openid, 
    #         file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
    #         url=file_url # 文件Url
    #     )

    #     # 资源上传后，会得到Media，用于发送消息
    #     await message._api.post_group_message(
    #         group_openid=message.group_openid,
    #         msg_type=7,  # 7表示富媒体类型
    #         msg_id=message.id, 
    #         media=uploadMedia
    #     )


if __name__ == "__main__":
    # 打开所有公域事件的监听
    intents = botpy.Intents.default()
    client = MainClient(intents=intents, is_sandbox=True)
    client.run(appid=get_config("qqbot.appid"), secret=get_config("qqbot.secret"))