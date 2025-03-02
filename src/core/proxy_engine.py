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
            
            # 优先使用请求中的授权头，如果没有则使用配置中的授权头
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                auth_header = self.config.authorization_header  # 现在这是一个属性方法
                logger.debug("Using authorization header from config")
            else:
                logger.debug("Using authorization header from request")
                
            headers = {
                "Authorization": auth_header,
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
                is_first_reasoning = True  
                last_was_reasoning = False 
                
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_text = line_text[6:]
                            
                            if data_text == '[DONE]':
                                if last_was_reasoning:
                                    modified_data = {
                                        'choices': [{
                                            'delta': {
                                                'content': "</think>"
                                            }
                                        }]
                                    }
                                    yield f"data: {json.dumps(modified_data)}\n\n"
                                yield 'data: [DONE]\n\n'
                                break
                            
                            try:
                                data = json.loads(data_text)
                                
                                if 'choices' in data and data['choices']:
                                    choice = data['choices'][0]
                                    
                                    if 'delta' in choice:
                                        delta = choice['delta']
                                        
                                        reasoning = delta.get('reasoning_content', '')
                                        if reasoning:
                                            if is_first_reasoning:
                                                modified_data = {
                                                    'choices': [{
                                                        'delta': {
                                                            'content': "<think>"
                                                        }
                                                    }]
                                                }
                                                yield f"data: {json.dumps(modified_data)}\n\n"
                                                is_first_reasoning = False
                                            
                                            modified_data = {
                                                'choices': [{
                                                    'delta': {
                                                        'content': reasoning
                                                    }
                                                }]
                                            }
                                            yield f"data: {json.dumps(modified_data)}\n\n"
                                            last_was_reasoning = True
                                        
                                        content = delta.get('content', '')
                                        if content:
                                            if last_was_reasoning:
                                                modified_data = {
                                                    'choices': [{
                                                        'delta': {
                                                            'content': "</think>\n\n"
                                                        }
                                                    }]
                                                }
                                                yield f"data: {json.dumps(modified_data)}\n\n"
                                                last_was_reasoning = False
                                            yield f"data: {json.dumps(data)}\n\n"
                                        
                                        if not (reasoning or content):
                                            yield f"data: {json.dumps(data)}\n\n"
                                    else:
                                        yield f"data: {json.dumps(data)}\n\n"
                                else:
                                    yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                yield f"data: {data_text}\n\n"
                
                # End of generate function
            
            # Return the streaming response
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