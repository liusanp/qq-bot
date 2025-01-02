from sqlalchemy import Column, Integer, String
from src.server.entity.base import Base

class Message(Base):
    __tablename__ = 'message'

    id = Column('id', Integer, primary_key=True)
    msg_id = Column('msg_id', String, default=''),
    msg_type = Column('msg_type', String, default=''),
    to_user_name = Column('to_user_name', String, default=''),
    from_user_name = Column('from_user_name', String, default=''),
    content = Column('content', String, default=''),
    reply = Column('reply', String, default=''),
    reply_type = Column('reply_type', String, default=''),
    create_time = Column('create_time', Integer),
    ready = Column('ready', Integer, default=0),
    request_time = Column('request_time', Integer, default=0),
    

    def __repr__(self):
        return f"<Message(id={self.id}, content={self.content[:10]})>"