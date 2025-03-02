# 在现有代码中添加以下内容
from src.app.api.routes import api_bp
from src.config.database import init_db

# 在app初始化后添加
app.register_blueprint(api_bp)

# 应用启动时初始化数据库
init_db()