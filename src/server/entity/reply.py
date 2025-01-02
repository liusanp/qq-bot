from sqlalchemy import Column, Integer, String
from src.server.entity.base import Base

class Reply(Base):
    __tablename__ = 'reply'

    id = Column('id', Integer, primary_key=True)
    msg_id = Column('msg_id', Integer),
    msg_type = Column('msg_type', Integer, default=1, comment="回复消息类型：1文本"),
    content = Column('content', String, default=''),
    create_time = Column('create_time', Integer),
    

    def __repr__(self):
        return f"<Reply(id={self.id}, content={self.content[:10]})>"