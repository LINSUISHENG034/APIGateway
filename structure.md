ai-proxy/
├── docker/                       # Docker 相关配置
│   ├── Dockerfile                # 镜像构建文件
│   └── supervisord.conf          # 进程管理配置
├── src/                          # 核心代码
│   ├── __init__.py
│   ├── app/                      # 主应用模块
│   │   ├── gui/                  # GUI 管理界面
│   │   │   ├── routes.py         # 页面路由
│   │   │   └── templates/        # HTML 模板
│   │   │       └── providers.html
│   ├── core/                     # 核心逻辑
│   │   ├── proxy_engine.py       # 代理转发引擎
│   │   └── port_manager.py       # 端口分配与检测
│   ├── models/                   # 数据模型
│   │   └── provider.py           # ProviderConfig 类定义
│   ├── services/                 # 服务层
│   │   ├── provider_service.py   # 服务商 CRUD 逻辑
│   │   └── process_manager.py    # 子进程生命周期管理
│   └── utils/                    # 工具类
│       ├── logger.py             # 日志配置
│       └── security.py           # 敏感数据加密
├── config/                       # 配置文件
│   ├── settings.py               # 应用配置（端口范围等）
│   └── database.py               # 数据库连接配置
├── static/                       # 静态资源
│   ├── css/
│   └── js/
├── tests/                        # 测试用例
│   ├── test_proxy_engine.py
│   └── test_port_manager.py
├── data/                         # 挂载卷目录（数据库文件）
├── docs/                         # 文档
│   └── API_REFERENCE.md
├── requirements.txt              # Python 依赖
├── docker-compose.yml            # 多容器编排（可选）
└── main.py                       # 应用入口