# src/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 确保数据目录存在
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 数据库文件路径
db_path = os.path.join(data_dir, 'providers.db')

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 添加此函数来初始化数据库表
def init_db():
    # 导入所有模型，确保它们被注册到Base.metadata
    from src.models.provider import ProviderConfig

    # 始终检查并更新数据库表结构
    # 获取期望的列
    expected_columns = [column.name for column in ProviderConfig.__table__.columns]

    # 检查表是否存在以及列是否匹配
    with engine.connect() as connection:
        result = connection.execute("PRAGMA table_info(providers)")
        existing_columns = [row[1] for row in result]  # 获取列名

        # 如果表不存在或列不匹配，则更新表结构
        if not existing_columns or set(expected_columns) != set(existing_columns):
            print("Updating 'providers' table schema.")
            ProviderConfig.__table__.drop(engine, checkfirst=True)  # 删除现有表（如果存在）
            Base.metadata.create_all(bind=engine)  # 重新创建所有表
        else:
            print("Schema is up-to-date.")

    # 确保有示例数据（可选）
    # with SessionLocal() as session:
    #     if session.query(ProviderConfig).count() == 0:
    #         print("Adding sample provider data.")
    #         sample_provider = ProviderConfig(
    #             name="Sample Provider",
    #             api_url="http://example.com/api",
    #             api_key="sample_api_key",
    #             auth_type="Bearer",
    #             port=8080,
    #             is_active=True
    #         )
    #         session.add(sample_provider)
    #         session.commit()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()