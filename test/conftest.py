"""
@Time       :2026/8/3 10:54
@Author     :240227206@qq.com
@File       :conftest.py
"""
import sys
from pathlib import Path

import pytest

# 把项目根目录加入环境变量，让Python识别到顶层包 app
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.http.app import app


@pytest.fixture
def client():
    """获取flask应用的测试应用，并返回"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
