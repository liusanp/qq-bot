from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.utils.config import get as get_config

# 创建数据库连接
DATABASE_URL = get_config("mysql")
engine = create_engine(DATABASE_URL, echo=True)

# 创建基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)