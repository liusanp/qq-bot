from botpy.message import BaseMessage
from src.utils.ability_factory import ability_factory
from src.client.base_ability import Chat, Audio
from src.client.models.res_model import ResModel
import re
from src.utils.config import get as get_config


chat_instanse = ability_factory('chat', Chat)
audio_instanse = ability_factory('audio', Audio)


async def route_message(message: BaseMessage) -> ResModel:
    content = message.content.strip()
    if content == "帮助" or content == '/help':
        msg = get_config("help_info")
        return chat_instanse.get_res(content=msg)
    elif content == '/audio':
        return chat_instanse.get_res(content=audio_instanse.get_help())
    elif re.match(r'^说[（\(](.*?)[）\)][：:](.*)', content):
        return await audio_instanse.get_response(message)
    else:
        return chat_instanse.get_response(message)