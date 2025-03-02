# src/services/provider_service.py
from src.models.provider import ProviderConfig

class ProviderService:
    def __init__(self):
        self.providers = {}    # 临时用内存存储，后续替换为数据库
    
    def add_provider(self, config: ProviderConfig):
        # 修正：使用字典存储，以端口为键
        self.providers[config.port] = config
        return {"status": "success", "port": config.port}
    
    def get_provider(self, port: int):
        return self.providers.get(port)
        
    def get_all(self):
        return list(self.providers.values())