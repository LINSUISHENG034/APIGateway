# src/services/provider_service.py
from sqlalchemy.orm import Session
from src.models.provider import ProviderConfig
from src.utils.logger import get_logger
from src.config.database import SessionLocal

logger = get_logger("src.services.provider_service")

class ProviderService:
    def __init__(self):
        self.providers = {}  # 缓存，用于快速访问
        # 从数据库加载所有提供商
        self._load_providers_from_db()
        
    def _load_providers_from_db(self):
        """从数据库加载所有提供商到缓存"""
        db = SessionLocal()
        try:
            providers = db.query(ProviderConfig).all()
            for provider in providers:
                self.providers[provider.port] = provider
            logger.info(f"Loaded {len(providers)} providers from database")
        except Exception as e:
            logger.error(f"Error loading providers from database: {str(e)}")
        finally:
            db.close()
    
    def add_provider(self, config: ProviderConfig):
        """添加新的提供商配置"""
        db = SessionLocal()
        try:
            db.add(config)
            db.commit()
            db.refresh(config)
            # 更新缓存
            self.providers[config.port] = config
            logger.info(f"Added provider {config.name} on port {config.port}")
            return {"status": "success", "port": config.port}
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding provider: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    def get_provider(self, port: int):
        """获取指定端口的提供商"""
        return self.providers.get(port)
    
    def get_all(self):
        """获取所有提供商"""
        db = SessionLocal()
        try:
            return db.query(ProviderConfig).all()
        finally:
            db.close()
    
    def update_provider(self, port: int, **kwargs):
        """更新提供商配置"""
        db = SessionLocal()
        try:
            provider = db.query(ProviderConfig).filter(ProviderConfig.port == port).first()
            if not provider:
                logger.warning(f"Provider with port {port} not found")
                return {"status": "error", "message": "Provider not found"}
            # 允许更新的字段列表
            allowed_fields = ['name', 'api_url', 'api_key', 'auth_type', 'port', 'is_active']
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(provider, key):
                    setattr(provider, key, value)
                    setattr(provider, key, value)
            
            db.commit()
            db.refresh(provider)
            # 更新缓存
            self.providers[port] = provider
            logger.info(f"Updated provider on port {port}")
            return {"status": "success"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating provider: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    def delete_provider(self, port: int):
        """删除提供商配置"""
        db = SessionLocal()
        try:
            provider = db.query(ProviderConfig).filter(ProviderConfig.port == port).first()
            if not provider:
                logger.warning(f"Provider with port {port} not found")
                return {"status": "error", "message": "Provider not found"}
            
            db.delete(provider)
            db.commit()
            # 更新缓存
            if port in self.providers:
                del self.providers[port]
            logger.info(f"Deleted provider on port {port}")
            return {"status": "success"}
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting provider: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()