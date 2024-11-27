from src.server.base_ability import Video
from src.utils.config import get as get_config
from botpy import logging
import re
import os
from src.utils.snowflake import generate_id
from src.utils.video_util import down_video


_log = logging.get_logger()


class DownVideo(Video):
    
    def __init__(self) -> None:
        super().__init__()
        
    def get_help(self):
        return "发送【下载视频：https://视频网站/video/BV1Qz4y1M7Vn】，下载视频。"
    
    async def get_response(self, message):
        self.message = message
        snowflake_id = generate_id()
        try:
            match = re.match(r'^下载视频[：:](.*)', message['content'])
            video_url = match.group(1)
            # print(f'video_url: {video_url}')
            video_path = f'./data/{snowflake_id}.mp4'
            title, desc, _, thumbnail = down_video(video_url, snowflake_id)
            has_up, url = self.uploader.upload(video_path)
            if has_up:
                os.remove(video_path)
                media_id = await self.upload_media(url, 2)
                return self.get_res(msg_type=7, media_id=media_id)
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
        except Exception as e:
            _log.error(e)
            return self.get_res(content="服务不可用，请稍后再试。")
        