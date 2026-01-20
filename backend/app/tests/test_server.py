"""
服务器相关接口测试
测试顺序：Country -> Group -> ServerInfo -> ServerAccount
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


class TestServerCountry:
    """国家信息接口测试"""
    
    @pytest.fixture
    def country_data(self):
        return {
            "short_name": _rand_letters(2),
            "name": f"测试国家-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
    
    def test_create_country(self, country_data):
        """测试创建国家"""
        result = _req("POST", "/server/country", json=country_data)
        assert result["message"] == "成功"
        assert result["short_name"] == country_data["short_name"]
        assert result["name"] == country_data["name"]
        return result["id"]
    
    def test_get_country(self, country_data):
        """测试获取单个国家"""
        created = _req("POST", "/server/country", json=country_data)
        cid = created["id"]
        
        result = _req("GET", f"/server/country/{cid}")
        assert result["id"] == cid
        assert result["short_name"] == country_data["short_name"]
        
        # 清理
        _req("DELETE", f"/server/country/{cid}")
    
    def test_list_countries(self, country_data):
        """测试获取国家列表"""
        created = _req("POST", "/server/country", json=country_data)
        cid = created["id"]
        
        result = _req("GET", "/server/country", params={
            "short_name": country_data["short_name"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/server/country/{cid}")
    
    def test_update_country(self, country_data):
        """测试更新国家"""
        created = _req("POST", "/server/country", json=country_data)
        cid = created["id"]
        
        update_data = {"name": f"{country_data['name']}-更新", "status": 2}
        result = _req("PUT", f"/server/country/{cid}", json=update_data)
        assert result["name"] == update_data["name"]
        assert result["status"] == 2
        
        # 清理
        _req("DELETE", f"/server/country/{cid}")
    
    def test_upsert_country(self, country_data):
        """测试创建或更新国家"""
        result = _req("POST", "/server/country/upsert", json=country_data)
        assert result["short_name"] == country_data["short_name"]
        cid = result["id"]
        
        # 再次 upsert，应该更新
        country_data["name"] = f"{country_data['name']}-upsert"
        result2 = _req("POST", "/server/country/upsert", json=country_data)
        assert result2["id"] == cid
        assert result2["name"] == country_data["name"]
        
        # 清理
        _req("DELETE", f"/server/country/{cid}")


class TestServerGroup:
    """分组信息接口测试"""
    
    @pytest.fixture
    def setup_country(self):
        """创建测试用的国家"""
        country_data = {
            "short_name": _rand_letters(2),
            "name": f"测试国家-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
        country = _req("POST", "/server/country", json=country_data)
        yield country["id"]
        # 清理
        _req("DELETE", f"/server/country/{country['id']}")
    
    def test_create_group(self, setup_country):
        """测试创建分组"""
        group_data = {
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": setup_country,
            "status": 1
        }
        result = _req("POST", "/server/group", json=group_data)
        assert result["message"] == "成功"
        assert result["name"] == group_data["name"]
        
        # 清理
        _req("DELETE", f"/server/group/{result['id']}")
    
    def test_get_group(self, setup_country):
        """测试获取单个分组"""
        group_data = {
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": setup_country,
            "status": 1
        }
        created = _req("POST", "/server/group", json=group_data)
        gid = created["id"]
        
        result = _req("GET", f"/server/group/{gid}")
        assert result["id"] == gid
        assert result["name"] == group_data["name"]
        assert result["country_id"] == setup_country
        
        # 清理
        _req("DELETE", f"/server/group/{gid}")
    
    def test_list_groups(self, setup_country):
        """测试获取分组列表"""
        group_data = {
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": setup_country,
            "status": 1
        }
        created = _req("POST", "/server/group", json=group_data)
        gid = created["id"]
        
        result = _req("GET", "/server/group", params={
            "name": group_data["name"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/server/group/{gid}")
    
    def test_update_group(self, setup_country):
        """测试更新分组"""
        group_data = {
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": setup_country,
            "status": 1
        }
        created = _req("POST", "/server/group", json=group_data)
        gid = created["id"]
        
        update_data = {"name": f"{group_data['name']}-UP", "status": 2}
        result = _req("PUT", f"/server/group/{gid}", json=update_data)
        assert result["name"] == update_data["name"]
        assert result["status"] == 2
        
        # 清理
        _req("DELETE", f"/server/group/{gid}")


class TestServerInfo:
    """服务器信息接口测试"""
    
    @pytest.fixture
    def setup_group(self):
        """创建测试用的国家和分组"""
        country = _req("POST", "/server/country", json={
            "short_name": _rand_letters(2),
            "name": f"测试国家-{uuid.uuid4().hex[:6]}",
            "status": 1
        })
        group = _req("POST", "/server/group", json={
            "name": f"TEST-G-{uuid.uuid4().hex[:6].upper()}",
            "country_id": country["id"],
            "status": 1
        })
        yield group["id"]
        # 清理
        _req("DELETE", f"/server/group/{group['id']}")
        _req("DELETE", f"/server/country/{country['id']}")
    
    def test_create_server_info(self, setup_group):
        """测试创建服务器信息"""
        server_data = {
            "host": f"192.168.1.{random.randint(2, 250)}",
            "ssh_port": 22,
            "password": "secret",
            "status": 1,
            "domain": "example.com",
            "is_sale": 1,
            "port": 8080,
            "group_id": setup_group
        }
        result = _req("POST", "/server/info", json=server_data)
        assert result["message"] == "成功"
        assert result["host"] == server_data["host"]
        
        # 清理
        _req("DELETE", f"/server/info/{result['id']}")
    
    def test_get_server_info(self, setup_group):
        """测试获取单个服务器信息"""
        server_data = {
            "host": f"192.168.1.{random.randint(2, 250)}",
            "ssh_port": 22,
            "password": "secret",
            "status": 1,
            "group_id": setup_group
        }
        created = _req("POST", "/server/info", json=server_data)
        sid = created["id"]
        
        result = _req("GET", f"/server/info/{sid}")
        assert result["id"] == sid
        assert result["host"] == server_data["host"]
        
        # 清理
        _req("DELETE", f"/server/info/{sid}")
    
    def test_list_server_infos(self, setup_group):
        """测试获取服务器信息列表"""
        server_data = {
            "host": f"192.168.1.{random.randint(2, 250)}",
            "ssh_port": 22,
            "password": "secret",
            "status": 1,
            "group_id": setup_group
        }
        created = _req("POST", "/server/info", json=server_data)
        sid = created["id"]
        
        result = _req("GET", "/server/info", params={
            "host": server_data["host"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/server/info/{sid}")


class TestServerAccount:
    """代理账号接口测试"""
    
    def test_create_account(self):
        """测试创建代理账号"""
        account_data = {
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "password": "pwd123"
        }
        result = _req("POST", "/server/account", json=account_data)
        assert result["message"] == "成功"
        assert result["username"] == account_data["username"]
        
        # 清理
        _req("DELETE", f"/server/account/{result['id']}")
    
    def test_get_account(self):
        """测试获取单个代理账号"""
        account_data = {
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "password": "pwd123"
        }
        created = _req("POST", "/server/account", json=account_data)
        aid = created["id"]
        
        result = _req("GET", f"/server/account/{aid}")
        assert result["id"] == aid
        assert result["username"] == account_data["username"]
        
        # 清理
        _req("DELETE", f"/server/account/{aid}")
    
    def test_list_accounts(self):
        """测试获取代理账号列表"""
        account_data = {
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "password": "pwd123"
        }
        created = _req("POST", "/server/account", json=account_data)
        aid = created["id"]
        
        result = _req("GET", "/server/account", params={
            "username": account_data["username"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/server/account/{aid}")
    
    def test_update_account(self):
        """测试更新代理账号"""
        account_data = {
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "password": "pwd123"
        }
        created = _req("POST", "/server/account", json=account_data)
        aid = created["id"]
        
        update_data = {"password": "pwd456"}
        result = _req("PUT", f"/server/account/{aid}", json=update_data)
        assert result["id"] == aid
        
        # 清理
        _req("DELETE", f"/server/account/{aid}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
