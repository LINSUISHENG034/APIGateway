# src/app/api/__init__.py
# 这个文件使src/app/api成为一个Python包
from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入路由
from src.app.api import routes