import traceback
import logging
from flask import Flask, jsonify, request, redirect, url_for

from src.models.provider import ProviderConfig
from src.services.provider_service import ProviderService
from src.core.port_manager import PortManager
from src.services.process_manager import ProcessManager
from src.utils.logger import get_logger
# 导入数据库初始化函数
from src.config.database import init_db
# 导入 GUI 子应用
from src.app.gui import app as gui_blueprint, init_admin
from src.app import app  # Import the Flask app instance

# 导入 API 蓝图
from src.app.api.routes import api_bp

# 初始化服务
port_manager = PortManager()
process_manager = ProcessManager()

def activate_saved_providers():
    """激活所有已保存的提供商"""
    try:
        # 创建新的ProviderService实例用于激活
        provider_service = ProviderService()
        providers = provider_service.get_all()
        
        for provider in providers:
            if provider.is_active:
                # 检查端口是否可用
                if not port_manager.is_port_available(provider.port):
                    app.logger.warning(f"Port {provider.port} is already in use for provider {provider.name}")
                    continue
                
                # 尝试启动提供商
                success = process_manager.start_provider(provider)
                if success:
                    app.logger.info(f"Successfully activated provider {provider.name} on port {provider.port}")
                else:
                    app.logger.error(f"Failed to activate provider {provider.name} on port {provider.port}")
                    port_manager.release_port(provider.port)

    except Exception as e:
        app.logger.error(f"Error activating saved providers: {str(e)}")
        app.logger.error(traceback.format_exc())

# 在应用启动前激活所有已保存的提供商
with app.app_context():
    init_db()  # 确保数据库初始化
    activate_saved_providers()

from flask import g

# 使用Flask的g对象管理ProviderService实例
@app.before_request
def initialize_services():
    if 'provider_service' not in g:
        g.provider_service = ProviderService()

# 提供一个函数来获取ProviderService实例
def get_provider_service():
    return g.provider_service

# 注册API蓝图
app.register_blueprint(api_bp, url_prefix='/api', name='api_v1')

# 在应用初始化后添加
# 注册GUI蓝图
app.register_blueprint(gui_blueprint, url_prefix='/gui')

# 初始化Admin
init_admin(app)

# 添加首页重定向
@app.route('/gui')
def gui_redirect():
    return redirect(url_for('gui.dashboard'))
@app.route('/admin')
def admin_redirect():
    return redirect('/admin/')
@app.route('/', methods=['GET'])
def home():
    return """
    <h1>API Gateway</h1>
    <p>API Gateway 正在运行。</p>
    <ul>
        <li><a href="/api/providers">API 接口</a></li>
        <li><a href="/gui">管理界面</a></li>
        <li><a href="/admin">Admin 界面</a></li>
    </ul>
    """, 200
@app.route('/api/providers', methods=['POST'])
def add_provider():
    app.logger.debug("Inside add_provider")
    # return jsonify({"message": "Reached add_provider"}), 200
    try:
        app.logger.debug(f"Request data: {request.data}")
        data = request.get_json(force=True, silent=True)  # Force parsing and silence errors
        app.logger.debug(f"Parsed JSON data: {data}")
        if data is None or not all(key in data for key in ['name', 'api_url']):
            return jsonify({"error": "Missing required fields or invalid JSON"}), 400

        # 从请求头或请求体中获取 API Key
        api_key = data.get('api_key')
        if not api_key:
            auth_header = request.headers.get('Authorization')
            if auth_header and ' ' in auth_header:
                auth_type, api_key = auth_header.split(' ', 1)
            else:
                return jsonify({"error": "Missing API Key"}), 400
        
        # 可选的授权类型
        auth_type = data.get('auth_type', 'Bearer')

        port = port_manager.allocate_port()
        if port is None:
            return jsonify({"error": "No available ports"}), 503
        
        config = ProviderConfig(
            name=data['name'],
            api_url=data['api_url'],
            api_key=api_key,
            auth_type=auth_type,
            port=port
        )
        
        # 添加详细日志
        app.logger.debug(f"Adding provider: {config.name} on port {config.port}")
        provider_service.add_provider(config)
        
        app.logger.debug(f"Starting provider process on port {config.port}")
        success = process_manager.start_provider(config)
        
        if not success:
            app.logger.error(f"Failed to start provider on port {config.port}")
            port_manager.release_port(port)
            return jsonify({"error": "Failed to start provider process"}), 500
            
        app.logger.info(f"Successfully started provider {config.name} on port {config.port}")
        return jsonify({
            "port": port,
            "status": "running"
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error in add_provider: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# 添加新的路由来获取所有提供商
@app.route('/api/providers', methods=['GET'])
def get_providers():
    try:
        providers = provider_service.get_all()
        result = []
        for provider in providers:
            result.append({
                "id": provider.id,
                "name": provider.name,
                "api_url": provider.api_url,
                "port": provider.port,
                "is_active": provider.is_active
            })
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error getting providers: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # 管理端口