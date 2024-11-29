

class ResModel():
    
    # 消息类型：0 是文本，2 是 markdown， 3 ark，4 embed，7 media 富媒体
    # 媒体类型：1 图片，2 视频，3 语音，4 文件（暂不开放）
    # 资源格式要求 图片：png/jpg，视频：mp4，语音：silk
    def __init__(self, media=None, content=None, msg_type=0, file_type=1):
        self.media = media
        self.content = content
        self.msg_type = msg_type
        self.file_type = file_type
    
    def to_dict(self):
        return {
            'media': self.media,
            'content': self.content,
            'msg_type': self.msg_type,
            'file_type': self.file_type
        }