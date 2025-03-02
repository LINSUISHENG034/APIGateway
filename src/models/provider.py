# src/models/provider.py
from src.utils.logger import get_logger

logger = get_logger("src.models.provider")

class ProviderConfig:
    def __init__(self, name, api_url, api_key, port):
        logger.debug(f"Initializing ProviderConfig with name={name}, api_url={api_url}, api_key={api_key}, port={port}")
        self.name = name       # 服务商名称
        self.api_url = api_url # 目标API地址
        self.api_key = api_key # 认证密钥
        self.port = port       # 监听端口
        self.is_active = False # 运行状态
        logger.debug("ProviderConfig initialized successfully")


# src/services/provider_service.py  <- Remove this duplicated code
# class ProviderService:
#     def __init__(self):
#         self.providers = {}    # 临时用内存存储，后续替换为数据库
#
#     def add_provider(self, config: ProviderConfig):
#         # 伪逻辑：添加配置并返回分配结果
#         self.providers.append(config)
#         return {"status": "success", "port": config.port}
#
#     def get_provider(self, port: int):
#         return self.providers.get(port)