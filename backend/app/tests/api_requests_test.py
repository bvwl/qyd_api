import os
import uuid
import random
import string
import requests


def _base_url() -> str:
    """
    获取基础接口地址
    """
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "6080"))
    return f"http://{host}:{port}/v1"


def _rand_letters(n: int = 2) -> str:
    """
    生成随机大写字母串
    """
    return "".join(random.choice(string.ascii_uppercase) for _ in range(n))


def _req(method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
    """
    统一请求封装，返回 JSON 字典
    """
    url = _base_url() + path
    resp = requests.request(method, url, json=json, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def test_country_flow() -> dict:
    """
    国家接口完整流程：创建→获取→列表→更新→返回 ID
    """
    short = _rand_letters(2)
    name = f"测试国家-{uuid.uuid4().hex[:6]}"
    created = _req(
        "POST",
        "/server/country",
        json={"short_name": short, "name": name, "status": 1},
    )
    cid = created["id"]

    _ = _req("GET", f"/server/country/{cid}")
    _ = _req("GET", "/server/country", params={"short_name": short, "res_count": True})
    _ = _req("GET", "/server/country", params={"status": 1, "res_count": True})
    _ = _req(
        "PUT",
        f"/server/country/{cid}",
        json={"name": f"{name}-更新", "status": 2},
    )
    return {"id": cid, "short_name": short}


def test_group_flow(country_id: str, country_short: str) -> dict:
    """
    分组接口完整流程：创建（关联国家）→获取→列表→更新→返回 ID
    """
    gname = f"TEST-G-{uuid.uuid4().hex[:6].upper()}"
    created = _req(
        "POST",
        "/server/group",
        json={"name": gname, "country_id": country_id, "status": 1},
    )
    gid = created["id"]

    _ = _req("GET", f"/server/group/{gid}")
    _ = _req("GET", "/server/group", params={"name": gname, "res_count": True})
    _ = _req("GET", "/server/group", params={"name": gname, "status": 1, "res_count": True})
    _ = _req(
        "PUT",
        f"/server/group/{gid}",
        json={"name": f"{gname}-UP", "status": 2},
    )
    return {"id": gid, "name": gname}


def test_server_info_flow(group_id: str) -> dict:
    """
    服务器信息接口完整流程：创建（关联分组）→获取→列表→更新→返回 ID
    """
    host = f"192.168.1.{random.randint(2, 250)}"
    payload = {
        "host": host,
        "ssh_port": 22,
        "password": "secret",
        "status": 1,
        "domain": "example.com",
        "is_sale": 1,
        "port": 8080,
        "group_id": group_id,
    }
    created = _req("POST", "/server/info", json=payload)
    sid = created["id"]

    _ = _req("GET", f"/server/info/{sid}")
    _ = _req("GET", "/server/info", params={"host": host, "res_count": True})
    _ = _req("PUT", f"/server/info/{sid}", json={"domain": "updated.example.com"})
    return {"id": sid, "host": host}


def test_email_info_flow(server_info_id: str) -> dict:
    """
    邮箱信息接口完整流程：创建（关联服务器信息）→获取→列表→更新→返回 ID
    """
    email = f"user{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "pwd123",
        "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
        "auxiliary_email_password": "auxpwd123",
        "client_id": "client-001",
        "access_token": None,
        "refresh_token": None,
        "status": 1,
        "server_info_id": server_info_id,
    }
    created = _req("POST", "/mail/info", json=payload)
    eid = created["id"]

    _ = _req("GET", f"/mail/info/{eid}")
    _ = _req("GET", "/mail/info", params={"email": email, "res_count": True})
    _ = _req("PUT", f"/mail/info/{eid}", json={"status": 2})
    return {"id": eid, "email": email}


def test_account_flow() -> dict:
    """
    代理账号接口完整流程：创建→获取→列表→更新→返回 ID
    """
    username = f"user_{uuid.uuid4().hex[:6]}"
    payload = {"username": username, "password": "pwd123"}
    created = _req("POST", "/server/account", json=payload)
    aid = created["id"]

    _ = _req("GET", f"/server/account/{aid}")
    _ = _req("GET", "/server/account", params={"username": username, "res_count": True})
    _ = _req("PUT", f"/server/account/{aid}", json={"password": "pwd456"})
    return {"id": aid, "username": username}


def test_email_auth_flow() -> dict:
    """
    已废弃：邮箱授权接口已移除
    """
    return {}


def cleanup_resources(ids: dict) -> None:
    """
    清理资源，按外键依赖逆序删除
    """
    # 再删邮箱信息（依赖 server_info）
    if ids.get("email_info"):
        _ = _req("DELETE", f"/mail/info/{ids['email_info']['id']}")
    # 再删服务器信息（依赖 group）
    if ids.get("server_info"):
        _ = _req("DELETE", f"/server/info/{ids['server_info']['id']}")
    # 再删分组（依赖 country）
    if ids.get("group"):
        _ = _req("DELETE", f"/server/group/{ids['group']['id']}")
    # 再删代理账号（无外键）
    if ids.get("account"):
        _ = _req("DELETE", f"/server/account/{ids['account']['id']}")
    # 最后删国家
    if ids.get("country"):
        _ = _req("DELETE", f"/server/country/{ids['country']['id']}")


def run_all_tests() -> None:
    """
    运行全部接口测试并打印摘要
    """
    ids: dict = {}
    try:
        country = test_country_flow()
        ids["country"] = country

        group = test_group_flow(country_id=country["id"], country_short=country["short_name"])
        ids["group"] = group

        server_info = test_server_info_flow(group_id=group["id"])
        ids["server_info"] = server_info

        email_info = test_email_info_flow(server_info_id=server_info["id"])
        ids["email_info"] = email_info

        account = test_account_flow()
        ids["account"] = account

        print("全部接口测试完成：")
        print(f"- 国家: {ids['country']['id']}")
        print(f"- 分组: {ids['group']['id']} (国家={ids['country']['short_name']})")
        print(f"- 服务器信息: {ids['server_info']['id']}")
        print(f"- 邮箱信息: {ids['email_info']['id']}")
        print(f"- 代理账号: {ids['account']['id']}")
    finally:
        cleanup_resources(ids)


if __name__ == "__main__":
    """
    脚本入口：运行所有接口测试
    """
    run_all_tests()
