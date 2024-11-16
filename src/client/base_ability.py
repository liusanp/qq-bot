from src.client.models.res_model import ResModel
from botpy.message import C2CMessage, GroupMessage, BaseMessage
from src.utils.ability_factory import ability_factory


class BaseAbility():
    def __init__(self) -> None:
        self.uploader = ability_factory('upload', Upload)


class Chat(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    def get_response(self, message: BaseMessage):
        self.message = message
        return self.get_res(f'接收到消息：{message.content}')
    
    def get_res(self, content):
        res = ResModel(content=content)
        return res


class Audio(BaseAbility):
    def __init__(self) -> None:
        super().__init__()
        
    def get_response(self, message: BaseMessage):
        self.message = message
        return self.get_res(f'接收到消息：{message.content}')
    
    def get_model_list(self):
        return []
    
    def get_res(self, media_id):
        res = ResModel(media=media_id, msg_type=7)
        return res
    
    async def upload_media(self, file_url):
        media_id = await self.message._api.post_group_file(
            group_openid=self.message.group_openid, 
            file_type=3, # 文件类型要对应上，具体支持的类型见方法说明
            url=file_url # 文件Url
        )
        return media_id
        
    
class Upload:
    def upload(self, file_path):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
