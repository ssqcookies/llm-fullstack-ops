"""
@Time       :2026/8/3 10:33
@Author     :240227206@qq.com
@File       :test_app_handler.py
"""
import pytest

from pkg.response import ResponseCode


class TestAppHandler:
    """app控制器的测试类"""

    @pytest.mark.parametrize("query", [None, "你好，你是谁？"])
    def test_completion(self, query, client):
        resp = client.post("/api/chat", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == ResponseCode.VALIDATE_ERROR
        else:
            assert resp.json.get("code") == ResponseCode.SUCCESS
        print("响应内容", resp.json)
