from botpy.message import BaseMessage
from src.utils.ability_factory import ability_factory
from src.server.base_ability import Chat, Audio, Image, Video
from src.server.models.res_model import ResModel
import re
from src.utils.config import get as get_config
from botpy import logging


_log = logging.get_logger()
chat_instanse = ability_factory('chat', Chat)
audio_instanse = ability_factory('audio', Audio)
image_instanse = ability_factory('image', Image)
video_instanse = ability_factory('video', Video)


async def route_message(message) -> ResModel:
    # qq图片消息
    # {'author': "{'user_openid': 'F935FB07BA019B34F0515FE538DED412'}", 'content': '', 'id': 'ROBOT1.0_tfg3h2bBP9tiVUtoJ8Eikkn72.7xp9o-gBaH0KqTrt5ICfcRXvTNxpIFLCEwbpRpWv0IcK0wdAWhqqnYjWPcRA!!', 'message_reference': "{'message_id': None}", 'mentions': '[]', 'attachments': "[{'content_type': 'image/jpeg', 'filename': 'D04DDB5E822B20CB05D77EE7DAD52D52.jpg', 'height': 959, 'width': 959, 'id': None, 'size': 131960, 'url': 'https://multimedia.nt.qq.com.cn/download?appid=1406&fileid=EhQF3Xnijsp3IK2KcmpHzZPMa15-6Bj4hggg_goo_uDjn5euigMyBHByb2RaEJWFf3OmI4-5qo5fnEocoBQ&rkey=CAQSKDhbt4PfkGhOKQkaRv3hyHe0htgqZrUz8RkKqK0s34OHJk7c0FqFrG4&spec=0'}]", 'msg_seq': 'None', 'timestamp': '2024-12-17T14:31:54+08:00', 'event_id': 'C2C_MESSAGE_CREATE:ylx4hblorpgmi0s3lkv9gpcffmdmvtadknldb913yj7fuohchhcigml0xmisoz2'}
    _log.info(message)
    content = message['content'].strip()
    attr = message['attachments']
    if not content and attr and len(attr) > 0:
        return await image_instanse.get_response_change_style(message)
    if content == "帮助" or content == '/help':
        msg = get_config("help_info")
        return chat_instanse.get_res(content=msg)
    elif content == '/audio':
        return chat_instanse.get_res(content=audio_instanse.get_help())
    elif re.match(r'^说[（\(](.*?)[）\)][：:](.*)', content):
        return await audio_instanse.get_response(message)
    elif content == '/image':
        return image_instanse.get_res(content=image_instanse.get_help())
    elif re.match(r'^画(?:\s*[\(（](\d{1,2}[:：]\d{1,2})[\)）])?\s*[：:](.+)', content):
        return await image_instanse.get_response(message)
    elif content == '/video':
        return video_instanse.get_res(content=video_instanse.get_help())
    elif re.match(r'^下载视频[：:](.*)', content):
        return await video_instanse.get_response(message)
    else:
        if get_config("enable_chat"):
            return await chat_instanse.get_response(message)
        else:
            msg = get_config("help_info")
            return chat_instanse.get_res(content=msg)