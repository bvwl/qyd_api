import os
import uuid
import requests


def _base_url() -> str:
    """
    获取基础接口地址
    """
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "6080"))
    return f"http://{host}:{port}/v1"


def _req(method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
    """
    统一请求封装，返回 JSON 字典
    """
    url = _base_url() + path
    resp = requests.request(method, url, json=json, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def test_user_register_and_login_flow() -> None:
    """
    用户注册 + 登录 + 列表查询完整流程
    """
    email = f"test_user_{uuid.uuid4().hex[:6]}@example.com"
    password = "Test1234!"
    nickname = "测试用户"

    # 注册
    reg_res = _req(
        "POST",
        "/user/auth/register",
        json={
            "email": email,
            "password": password,
            "nickname": nickname,
        },
    )
    assert reg_res["message"] == "成功"
    user = reg_res["user"]
    assert user["email"] == email

    # 登录
    login_res = _req(
        "POST",
        "/user/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_res["message"] == "成功"
    assert login_res["user"]["email"] == email

    # 用户列表（验证 /v1/user/user）
    list_res = _req(
        "GET",
        "/user/user",
        params={
            "order_by": "-create_time",
            "res_count": False,
            "page": 1,
            "limit": 10,
        },
    )
    assert list_res["message"] == "成功"
    assert isinstance(list_res["items"], list)
