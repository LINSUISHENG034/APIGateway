# src/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 确保数据目录存在
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 数据库文件路径
db_path = os.path.join(data_dir, 'providers.db')

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 添加此函数来初始化数据库表
def init_db():
    # 导入所有模型，确保它们被注册到Base.metadata
    from src.models.provider import ProviderConfig
    # 创建所有表
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()