# src/models/provider.py
from sqlalchemy import Column, Integer, String, Boolean
from src.config.database import Base
from src.utils.logger import get_logger

logger = get_logger("src.models.provider")

class ProviderConfig(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    api_url = Column(String(200))
    api_key = Column(String(100))
    port = Column(Integer, unique=True)
    is_active = Column(Boolean, default=False)
    
    def __init__(self, name, api_url, api_key, port):
        logger.debug(f"Initializing ProviderConfig with name={name}, api_url={api_url}, api_key={api_key}, port={port}")
        self.name = name       # 服务商名称
        self.api_url = api_url # 目标API地址
        self.api_key = api_key # 认证密钥
        self.port = port       # 监听端口
        self.is_active = False # 运行状态
        logger.debug("ProviderConfig initialized successfully")
