# src/app/gui/__init__.py
from flask import Blueprint
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from src.config.database import SessionLocal, engine, Base
from src.models.provider import ProviderConfig
from src.utils.logger import get_logger

logger = get_logger("src.app.gui")

# 创建蓝图
app = Blueprint('gui', __name__, template_folder='templates')

# 创建Admin实例
admin = Admin(name='API Gateway 管理', template_mode='bootstrap3')

# 添加模型视图
class ProviderModelView(ModelView):
    column_list = ('id', 'name', 'api_url', 'port', 'is_active')
    column_searchable_list = ['name']
    column_filters = ['is_active']
    form_excluded_columns = ['is_active']  # 排除自动设置的字段
    
    def get_query(self):
        return self.session.query(self.model)
    
    def get_count_query(self):
        return self.session.query(self.model)

# 初始化函数，用于在主应用中注册
def init_admin(app):
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 设置密钥
    app.secret_key = 'your_secret_key'  # 用于session加密，生产环境应使用环境变量
    
    # 初始化Admin
    admin.init_app(app)
    
    # 添加视图
    admin.add_view(ProviderModelView(ProviderConfig, SessionLocal()))
    
    return app

# 导入路由
from src.app.gui import routes