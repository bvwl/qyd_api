"""
邮箱相关接口测试
依赖：ServerInfo
"""
import os
import uuid
import random
import string
import requests
import pytest


def _base_url() -> str:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "6080"))
    return f"http://{host}:{port}/v1"


def _rand_letters(n: int = 2) -> str:
    return "".join(random.choice(string.ascii_uppercase) for _ in range(n))


def _req(method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
    url = _base_url() + path
    resp = requests.request(method, url, json=json, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


class TestEmailInfo:
    """邮箱信息接口测试"""
    
    @pytest.fixture
    def setup_server_info(self):
        """创建测试用的服务器信息"""
        # 创建国家
        country = _req("POST", "/server/country", json={
            "short_name": _rand_letters(2),
            "name": f"测试国家-{uuid.uuid4().hex[:6]}",
            "status": 1
        })
        
        # 创建分组
        group = _req("POST", "/server/group", json={
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": country["id"],
            "status": 1
        })
        
        # 创建服务器信息
        server = _req("POST", "/server/info", json={
            "host": f"192.168.1.{random.randint(2, 250)}",
            "ssh_port": 22,
            "password": "secret",
            "status": 1,
            "group_id": group["id"]
        })
        
        yield server["id"]
        
        # 清理
        _req("DELETE", f"/server/info/{server['id']}")
        _req("DELETE", f"/server/group/{group['id']}")
        _req("DELETE", f"/server/country/{country['id']}")
    
    def test_create_email_info(self, setup_server_info):
        """测试创建邮箱信息"""
        email_data = {
            "email": f"user{uuid.uuid4().hex[:6]}@example.com",
            "password": "pwd123",
            "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
            "auxiliary_email_password": "auxpwd123",
            "client_id": "client-001",
            "access_token": None,
            "refresh_token": None,
            "status": 1,
            "server_id": setup_server_info
        }
        result = _req("POST", "/mail/info", json=email_data)
        assert result["message"] == "成功"
        assert result["email"] == email_data["email"]
        
        # 清理
        _req("DELETE", f"/mail/info/{result['id']}")
    
    def test_get_email_info(self, setup_server_info):
        """测试获取单个邮箱信息"""
        email_data = {
            "email": f"user{uuid.uuid4().hex[:6]}@example.com",
            "password": "pwd123",
            "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
            "auxiliary_email_password": "auxpwd123",
            "status": 1,
            "server_id": setup_server_info
        }
        created = _req("POST", "/mail/info", json=email_data)
        eid = created["id"]
        
        result = _req("GET", f"/mail/info/{eid}")
        assert result["id"] == eid
        assert result["email"] == email_data["email"]
        
        # 清理
        _req("DELETE", f"/mail/info/{eid}")
    
    def test_list_email_infos(self, setup_server_info):
        """测试获取邮箱信息列表"""
        email_data = {
            "email": f"user{uuid.uuid4().hex[:6]}@example.com",
            "password": "pwd123",
            "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
            "auxiliary_email_password": "auxpwd123",
            "status": 1,
            "server_id": setup_server_info
        }
        created = _req("POST", "/mail/info", json=email_data)
        eid = created["id"]
        
        result = _req("GET", "/mail/info", params={
            "email": email_data["email"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/mail/info/{eid}")
    
    def test_update_email_info(self, setup_server_info):
        """测试更新邮箱信息"""
        email_data = {
            "email": f"user{uuid.uuid4().hex[:6]}@example.com",
            "password": "pwd123",
            "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
            "auxiliary_email_password": "auxpwd123",
            "status": 1,
            "server_id": setup_server_info
        }
        created = _req("POST", "/mail/info", json=email_data)
        eid = created["id"]
        
        update_data = {"status": 2}
        result = _req("PUT", f"/mail/info/{eid}", json=update_data)
        assert result["status"] == 2
        
        # 清理
        _req("DELETE", f"/mail/info/{eid}")
    
    def test_upsert_email_info(self, setup_server_info):
        """测试创建或更新邮箱信息"""
        email_data = {
            "email": f"user{uuid.uuid4().hex[:6]}@example.com",
            "password": "pwd123",
            "auxiliary_email": f"aux{uuid.uuid4().hex[:6]}@example.com",
            "auxiliary_email_password": "auxpwd123",
            "status": 1,
            "server_id": setup_server_info
        }
        result = _req("POST", "/mail/info/upsert", json=email_data)
        assert result["email"] == email_data["email"]
        eid = result["id"]
        
        # 再次 upsert，应该更新
        email_data["status"] = 2
        result2 = _req("POST", "/mail/info/upsert", json=email_data)
        assert result2["id"] == eid
        assert result2["status"] == 2
        
        # 清理
        _req("DELETE", f"/mail/info/{eid}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
