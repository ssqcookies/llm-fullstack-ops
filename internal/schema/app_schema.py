"""
@Time       :2026/8/2 16:17
@Author     :240227206@qq.com
@File       :app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length


class KimiForm(FlaskForm):
    """基础聊天接口验证"""
    # 必填、长度100
    query = StringField("query", validators=[DataRequired("用户的提问是必填"), Length(min=1, max=100)])
