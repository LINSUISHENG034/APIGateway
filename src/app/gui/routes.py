# src/gui/routes.py
from flask import render_template, request, redirect, url_for, jsonify
from src.app.gui import app
from src.models.provider import ProviderConfig
from src.services.provider_service import ProviderService
from src.services.process_manager import ProcessManager
from src.core.port_manager import PortManager
from src.utils.logger import get_logger

logger = get_logger("src.app.gui.routes")

# 初始化服务
port_manager = PortManager()
provider_service = ProviderService()
process_manager = ProcessManager()

@app.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@app.route('/dashboard/data')
def dashboard_data():
    """获取仪表盘数据"""
    providers = provider_service.get_all()
    total_providers = len(providers)
    active_providers = sum(1 for p in providers if process_manager.get_running_status(p.port) == "Running")
    available_ports = sum(1 for port in port_manager.port_range if port_manager.is_port_available(port))
    
    provider_list = [{
        'name': p.name,
        'port': p.port,
        'is_active': process_manager.get_running_status(p.port) == "Running"
    } for p in providers]
    
    return jsonify({
        'total_providers': total_providers,
        'active_providers': active_providers,
        'available_ports': available_ports,
        'stopped_providers': total_providers - active_providers,
        'providers': provider_list
    })

# 修改模板引用
@app.route('/')
def index():
    """主页，显示所有提供商"""
    providers = provider_service.get_all()
    return render_template('providers.html', providers=providers)

@app.route('/providers')
def provider_list():
    """提供商列表页面"""
    providers = provider_service.get_all()
    return render_template('providers.html', providers=providers)

@app.route('/providers/add', methods=['GET', 'POST'])
def add_provider():
    """添加提供商页面和处理"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            api_url = request.form.get('api_url')
            authorization_header = request.headers.get('Authorization')
            
            # 分配端口
            port = port_manager.allocate_port()
            if not port:
                return render_template('add_provider.html', error="无法分配端口，请稍后再试")
            
            # 解析授权头
            if authorization_header and ' ' in authorization_header:
                auth_type, api_key = authorization_header.split(' ', 1)
            else:
                return render_template('add_provider.html', error="Invalid Authorization header")
            
            # 创建配置
            config = ProviderConfig(
                name=name,
                api_url=api_url,
                api_key=api_key,
                auth_type=auth_type,
                port=port
            )
            result = provider_service.add_provider(config)
            
            if result["status"] == "success":
                # 启动提供商服务
                process_manager.start_provider(config)
                return redirect(url_for('provider_list'))
            else:
                # 释放端口
                port_manager.release_port(port)
                return render_template('add_provider.html', error=result["message"])
                
        except Exception as e:
            logger.error(f"Error adding provider: {str(e)}")
            return render_template('add_provider.html', error=str(e))
    
    return render_template('add_provider.html')

@app.route('/providers/<int:port>/start', methods=['POST'])
def start_provider(port):
    """启动提供商服务"""
    provider = provider_service.get_provider(port)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404
    
    result = process_manager.start_provider(provider)
    if result:
        provider_service.update_provider(port, is_active=True)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Failed to start provider"}), 500

@app.route('/providers/<int:port>/stop', methods=['POST'])
def stop_provider(port):
    """停止提供商服务"""
    provider = provider_service.get_provider(port)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404
    
    result = process_manager.stop_provider(port)
    if result:
        provider_service.update_provider(port, is_active=False)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Failed to stop provider"}), 500

@app.route('/providers/<int:port>/delete', methods=['POST'])
def delete_provider(port):
    """删除提供商"""
    # 先停止服务
    process_manager.stop_provider(port)
    # 释放端口
    port_manager.release_port(port)
    # 删除配置
    result = provider_service.delete_provider(port)
    return jsonify(result)

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok"})

# 在现有路由文件中添加以下路由

@app.route('/providers/<int:port>/status', methods=['GET'])
def get_provider_status(port):
    """获取提供商服务状态"""
    provider = provider_service.get_provider(port)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404
    
    status = process_manager.get_running_status(port)
    return jsonify({"status": "success", "running_status": status})