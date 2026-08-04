"""
@Time       :2026/8/3 23:43
@Author     :240227206@qq.com
@File       :app_service.py
"""
import uuid
from dataclasses import dataclass

from injector import inject

from internal.model import App
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AppService:
    """应用服务逻辑层：封装App相关数据库业务CRUD"""
    db: SQLAlchemy

    def create_app(self) -> App:
        # 实例化ORM模型对象（内存对象，还没入库）
        # 将实体类添加到session会话中
        # 提交session会话
        with self.db.auto_commit():
            app = App(name="测试机器人", account_id=uuid.uuid4(), icon="",
                      description="这是一个简单的聊天机器人")
            self.db.session.add(app)
        return app

    def get_app(self, id: uuid.UUID) -> App:
        app = self.db.session.query(App).get(id)
        return app

    def update_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "聊天机器人"
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
