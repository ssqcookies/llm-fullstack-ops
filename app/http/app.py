"""
@Time       :2026/7/31 15:47
@Author     :240227206@qq.com
@File       :app.py
"""
from dotenv import load_dotenv
from flask_migrate import Migrate
from injector import Injector

from app.http import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http
from pkg.sqlalchemy import SQLAlchemy

# 第一步优先加载环境变量
load_dotenv(override=True)
# 1. 创建注入器容器（全局单例容器）
config = Config()

injector = Injector([ExtensionModule])

# 2. 从容器自动拿到Router实例，传给Http服务
app = Http(
    __name__,
    conf=config,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router)
)
# 3. 启动web服务
if __name__ == "__main__":
    app.run(debug=True)
