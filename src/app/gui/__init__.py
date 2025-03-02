# src/app/gui/__init__.py
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from src.config.database import SessionLocal, engine, Base
from src.models.provider import ProviderConfig
from src.utils.logger import get_logger

logger = get_logger("src.app.gui")

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于session加密，生产环境应使用环境变量

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建Admin实例
admin = Admin(app, name='API Gateway 管理', template_mode='bootstrap3')

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

# 添加视图
admin.add_view(ProviderModelView(ProviderConfig, SessionLocal()))

# 导入路由
from src.app.gui import routes