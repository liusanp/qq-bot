from telegram import Message
from src.server.models.res_model import ResModel
from src.utils.config import get as get_config
import requests
import logging
from botpy import logging

_log = logging.get_logger()
url = f"{get_config('server_host')}:{get_config('server_port')}/handleMsg"

headers = {
    'Content-Type': 'application/json'
}


async def route_message(message: Message) -> ResModel:
    _log.info(message)
    res = ResModel(content="服务暂时不可用，请稍后再试。")
    # payload = message.__str__().replace('"', '').replace("'", '"').replace('"None"', 'None').replace('None', '"None"')
    # # print('payload', payload)
    # response = requests.request("POST", url, headers=headers, data=payload)
    # if response.status_code == 200:
    #     res_json = response.json()
    #     print(res_json)
    #     if res_json['code'] == 0:
    #         if res_json['data']['media']:
    #             try:
    #                 res_json = {}
    #             except Exception as e:
    #                 return ResModel(content="服务暂时不可用，请稍后再试。")
    #         return ResModel(media=res_json['data']['media'], content=res_json['data']['content'], msg_type=res_json['data']['msg_type'])
    return res
