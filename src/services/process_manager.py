# src/services/process_manager.py
import subprocess
import threading
import time
import os
import sys
from src.models.provider import ProviderConfig
from src.core.proxy_engine import ProxyEngine

from src.utils.logger import get_logger


logger = get_logger("src.services.process_manager")  # 日志将保存到 logs/process_manager.log

class ProcessManager:
    def __init__(self):
        self.processes = {}
        
    def start_provider(self, config: ProviderConfig):
        """启动一个新的代理服务进程"""
        try:
            # 使用线程启动代理引擎
            def run_proxy():
                try:
                    proxy = ProxyEngine(config)
                    proxy.run()
                except Exception as e:
                    print(f"Error in proxy thread: {str(e)}")
                
            thread = threading.Thread(target=run_proxy)
            thread.daemon = True
            thread.start()
            
            # 存储线程引用
            self.processes[config.port] = thread
            
            # 等待服务启动
            max_retries = 5
            for i in range(max_retries):
                time.sleep(1)  # 等待更长时间
                
                # 检查端口是否已经在监听
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', config.port))
                    if result == 0:
                        config.is_active = True
                        return True
            
            # 如果达到最大重试次数仍未成功，则返回失败
            print(f"Failed to start provider on port {config.port} after {max_retries} retries")
            return False
                
        except Exception as e:
            print(f"Error starting provider: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def stop_provider(self, port):
        """停止指定端口的代理服务"""
        if port in self.processes:
            # 标记为不活跃
            self.processes.pop(port, None)
            return True
        return False