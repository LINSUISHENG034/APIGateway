import traceback
import logging

from flask import Flask, jsonify, request
from src.models.provider import ProviderConfig
from src.services.provider_service import ProviderService
from src.core.port_manager import PortManager
from src.services.process_manager import ProcessManager
from src.utils.logger import get_logger
# 导入数据库初始化函数
from src.config.database import init_db


logger = get_logger("main")  # 日志将保存到 logs/main.log
logger.debug("Testing early logging 1")

# 初始化数据库表
logger.info("Initializing database tables")
init_db()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger = logger # Use the custom logger for the Flask app
provider_service = ProviderService()
port_manager = PortManager()
process_manager = ProcessManager()

@app.route('/', methods=['GET'])
def home():
    return "API Gateway is running. Use /api/providers to add a provider.", 200

@app.route('/api/providers', methods=['POST'])
def add_provider():
    app.logger.debug("Inside add_provider")
    # return jsonify({"message": "Reached add_provider"}), 200
    try:
        app.logger.debug(f"Request data: {request.data}")
        data = request.get_json(force=True, silent=True)  # Force parsing and silence errors
        app.logger.debug(f"Parsed JSON data: {data}")
        if data is None or not all(key in data for key in ['name', 'api_url', 'api_key']):
            return jsonify({"error": "Missing required fields or invalid JSON"}), 400

        port = port_manager.allocate_port()
        if port is None:
            return jsonify({"error": "No available ports"}), 503
        
        config = ProviderConfig(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # 管理端口