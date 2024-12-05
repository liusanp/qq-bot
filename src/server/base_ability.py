from src.server.models.res_model import ResModel
from botpy.http import BotHttp, Route
from src.utils.ability_factory import ability_factory
from pydub import AudioSegment
import os
import pilk
from src.utils.config import get as get_config, set as set_config


class BaseAbility():
    def __init__(self) -> None:
        self.uploader = ability_factory('upload', Upload)
        self.translater = ability_factory('translate', Translate)
        self._http = BotHttp(timeout=300, app_id=get_config("qqbot.appid"), secret=get_config("qqbot.secret"))
        
    def get_help(self) -> str:
        return "能力操作说明"
        
    def get_res(self, msg_type=0, media_id=None, content=None, file_type=1) -> ResModel:
        """拼装返回

        Args:
            msg_type (int, optional): 消息类型：0 是文本，2 是 markdown， 3 ark，4 embed，7 media 富媒体
            media_id (_type_, optional): _description_. Defaults to None.
            content (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        res = ResModel(media=media_id, msg_type=msg_type, content=content, file_type=file_type)
        return res
    
    def convert_to_silk(self, media_path: str) -> str:
        """将输入的媒体文件转出为 silk, 并返回silk路径"""
        media = AudioSegment.from_file(f'{media_path}.mp3')
        silk_path = f'{media_path}.silk'
        pcm_path = f'{media_path}.pcm'
        media.export(pcm_path, 's16le', parameters=['-ar', str(media.frame_rate), '-ac', '1']).close()
        pilk.encode(pcm_path, silk_path, pcm_rate=media.frame_rate, tencent=True)
        os.remove(pcm_path)
        return silk_path
    
    async def upload_media(self, file_url, file_type=1):
        """上传媒体文件

        Args:
            file_url (_type_): _description_
            file_type (int, optional): 媒体类型：1 图片，2 视频，3 语音   资源格式要求 图片：png/jpg，视频：mp4，语音：silk

        Returns:
            _type_: _description_
        """
        event_id = self.message['event_id']
        self.message['file_type'] = file_type
        self.message['url'] = file_url
        if event_id.find('C2C') > -1:
            openid = self.message['author']['user_openid']
            route = Route("POST", "/v2/users/{openid}/files", openid=openid)
            media_id = await self._http.request(route=route, json=self.message)
            # media_id = await self.message._api.post_c2c_file(
            #     openid=self.message['author']['user_openid'], 
            #     file_type=file_type,
            #     url=file_url
            # )
        elif event_id.find('GROUP') > -1:
            group_openid=self.message['group_openid']
            route = Route("POST", "/v2/groups/{group_openid}/files", group_openid=group_openid)
            media_id = await self._http.request(route=route, json=self.message)
            # media_id = await self.message._api.post_group_file(
            #     group_openid=self.message['group_openid'], 
            #     file_type=file_type,
            #     url=file_url
            # )
        return media_id


class Chat(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    def get_response(self, message):
        self.message = message
        return self.get_res(f'接收到消息：{message["content"]}')


class Audio(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    async def get_response(self, message):
        self.message = message
        return self.get_res(f'接收到消息：{message["content"]}')
        
    
class Upload:
    def upload(self, file_path):
        raise NotImplementedError("This method should be overridden by subclasses.")
    

class Translate:
    def trans(self, src_text):
        if not get_config("enable_translate"):
            return src_text
        else:
            raise NotImplementedError("This method should be overridden by subclasses.")
    

class Image(BaseAbility):
    
    imgwh = {
        "1:1": "1024x1024",
        "1:2": "512x1024",
        "3:2": "768x512",
        "3:4": "768x1024",
        "16:9": "1024x576",
        "9:16": "576x1024",
    }
    
    def __init__(self) -> None:
        super().__init__()
        
    def get_wh_by_ratio(self, ratio="1:1"):
        if ratio not in self.imgwh:
            ratio = "1:1"
        whs = self.imgwh[ratio].split('x')
        return whs[0], whs[1]
        
    def get_response(self, message):
        self.message = message
        return self.get_res(f'接收到消息：{message["content"]}')
    
    
class Video(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    def get_response(self, message):
        self.message = message
        return self.get_res(f'接收到消息：{message["content"]}')