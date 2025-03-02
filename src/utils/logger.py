import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_level=logging.DEBUG, log_to_file=True, log_dir="logs"):
    """设置并返回一个配置好的日志记录器"""
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经配置过处理器，则直接返回
    if logger.handlers:
        return logger
        
    # 设置日志级别
    logger.setLevel(log_level)
    
    # 创建控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # 添加控制台处理器到日志记录器
    logger.addHandler(ch)
    
    # 如果需要记录到文件
    if log_to_file:
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 从名称中提取模块路径
        module_parts = name.split('.')
        module_name = module_parts[-1]
        module_path = os.path.join(*module_parts[:-1]) if len(module_parts) > 1 else ""

        # 创建模块对应的子目录
        module_log_dir = os.path.join(log_dir, module_path)
        if not os.path.exists(module_log_dir):
            os.makedirs(module_log_dir)

        # 创建文件处理器
        log_file = os.path.join(module_log_dir, f"{module_name}.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # 添加文件处理器到日志记录器
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name):
    """获取已配置的日志记录器，如果不存在则创建一个新的"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger