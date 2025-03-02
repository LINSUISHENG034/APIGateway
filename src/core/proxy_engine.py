# src/core/proxy_engine.py
import requests
import json
import re
import logging
from flask import Flask, request, Response, stream_with_context, jsonify

from src.utils.logger import get_logger


logger = get_logger("src.core.proxy_engine")  # 日志将保存到 logs/proxy_engine.log

class ProxyEngine:
    def __init__(self, config):
        self.config = config
        self.app = Flask(f"proxy_{config.port}")
        self.app.logger.setLevel(logging.DEBUG)
        self._register_routes()
        logger.debug(f"Initialized ProxyEngine for port {config.port}")

    def _register_routes(self):
        logger.debug("Registering routes")
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def handle_request():
            logger.debug("Handling /v1/chat/completions request")
            return self._process_request(request)

        @self.app.route('/health', methods=['GET'])
        def health_check():
            logger.debug("Handling /health request")
            return jsonify({"status": "ok"}), 200
        logger.debug("Routes registered")

    def _clean_messages(self, messages):
        cleaned = []
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, list):
                cleaned_msg = msg.copy()
                cleaned_msg['content'] = content
                cleaned.append(cleaned_msg)
            else:
                cleaned_content = re.sub(r'<think>.*?</think>\s*\n*', '', content, flags=re.DOTALL)
                cleaned_msg = msg.copy()
                cleaned_msg['content'] = cleaned_content.strip()
                cleaned.append(cleaned_msg)
        return cleaned
    
    def _process_request(self, request):
        try:
            # 原始处理逻辑重构
            user_data = request.json
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            if 'messages' in user_data:
                user_data['messages'] = self._clean_messages(user_data['messages'])
            
            user_data['stream'] = True
            
            logger.debug(f"Forwarding request to {self.config.api_url}")
            response = requests.post(
                self.config.api_url,
                json=user_data,
                headers=headers,
                stream=True
            )
            
            def generate():
                # 原始流处理逻辑
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_text = line_text[6:]
                            if data_text == '[DONE]':
                                yield f"data: [DONE]\n\n"
                                break
                            
                            try:
                                data = json.loads(data_text)
                                yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                yield f"data: {data_text}\n\n"
                    
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream'
            )
        except Exception as e:
            logger.error(f"Error in _process_request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
    
    def run(self):
        try:
            logger.info(f"Starting proxy server on port {self.config.port}")
            self.app.run(host='0.0.0.0', port=self.config.port, threaded=True)
        except Exception as e:
            logger.error(f"Error running proxy server: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())