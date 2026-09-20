"""
@Time       :2026/9/15 09:24
@Author     :240227206@qq.com
@File       :api_key.py
"""

from sqlalchemy import (
    Column,
    UUID,
    String,
    DateTime,
    Boolean,
    text,
    PrimaryKeyConstraint,
)

from internal.extension.database_extension import db


class ApiKey(db.Model):
    """API秘钥模型"""
    __tablename__ = "api_key"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_api_key_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))  # 记录id
    account_id = Column(UUID, nullable=False)  # 关联账号id
    api_key = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 加密后的api秘钥
    is_active = Column(Boolean, nullable=False, server_default=text('false'))  # 是否激活，为true时可以使用
    remark = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 备注信息
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)')
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def account(self) -> "Account":
        """只读属性，返回该秘钥归属的账号信息"""
        from internal.model.account import Account
        return db.session.query(Account).get(self.account_id)
