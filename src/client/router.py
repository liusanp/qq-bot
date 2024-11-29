from botpy.message import BaseMessage, C2CMessage, GroupMessage
from src.server.models.res_model import ResModel
from src.utils.config import get as get_config
import requests


url = f"{get_config('server_host')}:{get_config('server_port')}/handleMsg"

headers = {
    'Content-Type': 'application/json'
}


async def route_message(message: BaseMessage) -> ResModel:
    res = ResModel(content="服务暂时不可用，请稍后再试。")
    payload = message.__str__().replace('"', '').replace("'", '"').replace('"None"', 'None').replace('None', '"None"')
    # print('payload', payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        res_json = response.json()
        print(res_json)
        if res_json['code'] == 0:
            if res_json['data']['media']:
                res_json = upload_media(message, res_json)
            return ResModel(media=res_json['data']['media'], content=res_json['data']['content'], msg_type=res_json['data']['msg_type'])
    return res
        

async def upload_media(message: BaseMessage, res_json):
    file_url = res_json['data']['media']  # 这里需要填写上传的资源Url
    file_type = res_json['data']['file_type']
    if isinstance(message, C2CMessage):
        uploadMedia = await message._api.post_c2c_file(
            openid=message.author.user_openid, 
            file_type=file_type, # 文件类型要对应上，具体支持的类型见方法说明
            url=file_url # 文件Url
        )
    elif isinstance(message, GroupMessage):
        uploadMedia = await message._api.post_group_file(
            group_openid=message.group_openid, 
            file_type=file_type, # 文件类型要对应上，具体支持的类型见方法说明
            url=file_url # 文件Url
        )
    res_json['data']['media'] = uploadMedia
    return res_json