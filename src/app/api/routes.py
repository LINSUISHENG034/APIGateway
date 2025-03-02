# src/app/api/routes.py
from flask import Blueprint, request, jsonify
from src.models.provider import ProviderConfig
from src.services.provider_service import ProviderService
from src.services.port_manager import PortManager
from src.utils.logger import get_logger

logger = get_logger("src.app.api.routes")
api_bp = Blueprint('api', __name__, url_prefix='/api')

provider_service = ProviderService()
port_manager = PortManager()

@api_bp.route('/providers', methods=['GET'])
def get_providers():
    """获取所有提供商配置"""
    providers = provider_service.get_all()
    result = []
    for provider in providers:
        result.append({
            'id': provider.id,
            'name': provider.name,
            'api_url': provider.api_url,
            'port': provider.port,
            'is_active': provider.is_active
        })
    return jsonify(result)

@api_bp.route('/providers', methods=['POST'])
def add_provider():
    """添加新的提供商配置"""
    try:
        data = request.json
        name = data.get('name')
        api_url = data.get('api_url')
        api_key = data.get('api_key')
        
        # 验证必要字段
        if not all([name, api_url, api_key]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        # 分配端口
        port = port_manager.allocate_port()
        if not port:
            return jsonify({"status": "error", "message": "No available ports"}), 503
        
        # 创建配置
        config = ProviderConfig(name=name, api_url=api_url, api_key=api_key, port=port)
        result = provider_service.add_provider(config)
        
        if result["status"] == "success":
            return jsonify({
                "status": "success", 
                "provider": {
                    "id": config.id,
                    "name": config.name,
                    "api_url": config.api_url,
                    "port": config.port
                }
            }), 201
        else:
            # 释放端口
            port_manager.release_port(port)
            return jsonify({"status": "error", "message": result["message"]}), 400
            
    except Exception as e:
        logger.error(f"Error adding provider via API: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/providers/<int:port>', methods=['DELETE'])
def delete_provider(port):
    """删除提供商配置"""
    result = provider_service.delete_provider(port)
    if result["status"] == "success":
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": result["message"]}), 404

@api_bp.route('/providers/status', methods=['GET'])
def get_provider_status():
    """获取提供商状态"""
    port = request.args.get('port', type=int)
    if not port:
        return jsonify({"status": "error", "message": "Port parameter required"}), 400
        
    from src.services.process_manager import ProcessManager
    process_manager = ProcessManager()
    
    provider = provider_service.get_provider(port)
    if not provider:
        return jsonify({"status": "error", "message": "Provider not found"}), 404
    
    status = process_manager.get_running_status(port)
    return jsonify({"status": status})