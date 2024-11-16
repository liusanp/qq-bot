from src.client.models.res_model import ResModel
from botpy.message import C2CMessage, GroupMessage, BaseMessage
from src.utils.ability_factory import ability_factory
from pydub import AudioSegment
import os
import pilk


class BaseAbility():
    def __init__(self) -> None:
        self.uploader = ability_factory('upload', Upload)
        
    def get_res(self, msg_type=0, media_id=None, content=None):
        """拼装返回

        Args:
            msg_type (int, optional): 消息类型：0 是文本，2 是 markdown， 3 ark，4 embed，7 media 富媒体
            media_id (_type_, optional): _description_. Defaults to None.
            content (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        res = ResModel(media=media_id, msg_type=msg_type, content=content)
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
        
        if isinstance(self.message, C2CMessage):
            media_id = await self.message._api.post_c2c_file(
                openid=self.message.author.user_openid, 
                file_type=file_type,
                url=file_url
            )
        elif isinstance(self.message, GroupMessage):
            media_id = await self.message._api.post_group_file(
                group_openid=self.message.group_openid, 
                file_type=file_type,
                url=file_url
            )
        return media_id


class Chat(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    def get_response(self, message: BaseMessage):
        self.message = message
        return self.get_res(f'接收到消息：{message.content}')


class Audio(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    async def get_response(self, message: BaseMessage):
        self.message = message
        return self.get_res(f'接收到消息：{message.content}')
    
    def get_model_list(self):
        return []
        
    
class Upload:
    def upload(self, file_path):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
