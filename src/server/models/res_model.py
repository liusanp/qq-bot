

class ResModel():
    
    # 消息类型：0 是文本，2 是 markdown， 3 ark，4 embed，7 media 富媒体
    def __init__(self, media=None, content=None, msg_type=0):
        self.media = media
        self.content = content
        self.msg_type = msg_type
    
    def to_dict(self):
        return {
            'media': self.media,
            'content': self.content,
            'msg_type': self.msg_type
        }