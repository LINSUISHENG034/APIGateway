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
    api_key = Column(String(200))  # 替换 authorization_header
    auth_type = Column(String(50), default="Bearer")  # 添加授权类型，默认为 Bearer
    port = Column(Integer, unique=True)
    is_active = Column(Boolean, default=False)
    
    def __init__(self, name, api_url, api_key, port, auth_type="Bearer"):
        logger.debug(f"Initializing ProviderConfig with name={name}, api_url={api_url}, port={port}")
        self.name = name                   # 服务商名称
        self.api_url = api_url             # 目标API地址
        self.api_key = api_key             # API密钥
        self.auth_type = auth_type         # 授权类型
        self.port = port                   # 监听端口
        self.is_active = True              # 运行状态
        logger.debug("ProviderConfig initialized successfully")
        
    @property
    def authorization_header(self):
        """根据 API Key 和授权类型构建授权头"""
        if not self.api_key:
            return None
        return f"{self.auth_type} {self.api_key}"
