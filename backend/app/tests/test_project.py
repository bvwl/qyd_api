"""
项目相关接口测试
测试顺序：ProjectInfo -> ProjectAccount -> ProjectBalance -> ProjectWallet
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


class TestProjectInfo:
    """项目信息接口测试"""
    
    def test_create_project(self):
        """测试创建项目"""
        project_data = {
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1,
            "content": "test content"
        }
        result = _req("POST", "/project/info", json=project_data)
        assert result["message"] == "成功"
        assert result["name"] == project_data["name"]
        
        # 清理
        _req("DELETE", f"/project/info/{result['id']}")
    
    def test_get_project(self):
        """测试获取单个项目"""
        project_data = {
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
        created = _req("POST", "/project/info", json=project_data)
        pid = created["id"]
        
        result = _req("GET", f"/project/info/{pid}")
        assert result["id"] == pid
        assert result["name"] == project_data["name"]
        
        # 清理
        _req("DELETE", f"/project/info/{pid}")
    
    def test_list_projects(self):
        """测试获取项目列表"""
        project_data = {
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
        created = _req("POST", "/project/info", json=project_data)
        pid = created["id"]
        
        result = _req("GET", "/project/info", params={
            "name": project_data["name"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/project/info/{pid}")
    
    def test_update_project(self):
        """测试更新项目"""
        project_data = {
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
        created = _req("POST", "/project/info", json=project_data)
        pid = created["id"]
        
        update_data = {"name": f"{project_data['name']}-更新", "status": 2}
        result = _req("PUT", f"/project/info/{pid}", json=update_data)
        assert result["name"] == update_data["name"]
        assert result["status"] == 2
        
        # 清理
        _req("DELETE", f"/project/info/{pid}")
    
    def test_upsert_project(self):
        """测试创建或更新项目"""
        project_data = {
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        }
        result = _req("POST", "/project/info/upsert", json=project_data)
        assert result["name"] == project_data["name"]
        pid = result["id"]
        
        # 再次 upsert，应该更新
        project_data["status"] = 2
        result2 = _req("POST", "/project/info/upsert", json=project_data)
        assert result2["id"] == pid
        assert result2["status"] == 2
        
        # 清理
        _req("DELETE", f"/project/info/{pid}")


class TestProjectAccount:
    """项目账号接口测试"""
    
    @pytest.fixture
    def setup_project_and_server(self):
        """创建测试用的项目和服务器信息"""
        # 创建项目
        project = _req("POST", "/project/info", json={
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        })
        
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
        
        yield {"project_id": project["id"], "server_info_id": server["id"]}
        
        # 清理
        _req("DELETE", f"/server/info/{server['id']}")
        _req("DELETE", f"/server/group/{group['id']}")
        _req("DELETE", f"/server/country/{country['id']}")
        _req("DELETE", f"/project/info/{project['id']}")
    
    def test_create_project_account(self, setup_project_and_server):
        """测试创建项目账号"""
        account_data = {
            "account": f"test_account_{uuid.uuid4().hex[:6]}",
            "password": "pwd123",
            "status": 1,
            "account_type": 1,
            "project_id": setup_project_and_server["project_id"],
            "server_info_id": setup_project_and_server["server_info_id"]
        }
        result = _req("POST", "/project/account", json=account_data)
        assert result["message"] == "成功"
        assert result["account"] == account_data["account"]
        
        # 清理
        _req("DELETE", f"/project/account/{result['id']}")
    
    def test_get_project_account(self, setup_project_and_server):
        """测试获取单个项目账号"""
        account_data = {
            "account": f"test_account_{uuid.uuid4().hex[:6]}",
            "password": "pwd123",
            "status": 1,
            "account_type": 1,
            "project_id": setup_project_and_server["project_id"],
            "server_info_id": setup_project_and_server["server_info_id"]
        }
        created = _req("POST", "/project/account", json=account_data)
        aid = created["id"]
        
        result = _req("GET", f"/project/account/{aid}")
        assert result["id"] == aid
        assert result["account"] == account_data["account"]
        
        # 清理
        _req("DELETE", f"/project/account/{aid}")
    
    def test_list_project_accounts(self, setup_project_and_server):
        """测试获取项目账号列表"""
        account_data = {
            "account": f"test_account_{uuid.uuid4().hex[:6]}",
            "password": "pwd123",
            "status": 1,
            "account_type": 1,
            "project_id": setup_project_and_server["project_id"]
        }
        created = _req("POST", "/project/account", json=account_data)
        aid = created["id"]
        
        result = _req("GET", "/project/account", params={
            "account": account_data["account"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/project/account/{aid}")
    
    def test_update_project_account(self, setup_project_and_server):
        """测试更新项目账号"""
        account_data = {
            "account": f"test_account_{uuid.uuid4().hex[:6]}",
            "password": "pwd123",
            "status": 1,
            "account_type": 1,
            "project_id": setup_project_and_server["project_id"]
        }
        created = _req("POST", "/project/account", json=account_data)
        aid = created["id"]
        
        update_data = {"status": 2, "password": "newpwd456"}
        result = _req("PUT", f"/project/account/{aid}", json=update_data)
        assert result["status"] == 2
        
        # 清理
        _req("DELETE", f"/project/account/{aid}")


class TestProjectBalance:
    """项目余额接口测试"""
    
    @pytest.fixture
    def setup_project_account(self):
        """创建测试用的项目账号"""
        # 创建项目
        project = _req("POST", "/project/info", json={
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        })
        
        # 创建项目账号
        account = _req("POST", "/project/account", json={
            "account": f"test_account_{uuid.uuid4().hex[:6]}",
            "password": "pwd123",
            "status": 1,
            "account_type": 1,
            "project_id": project["id"]
        })
        
        yield account["id"]
        
        # 清理
        _req("DELETE", f"/project/account/{account['id']}")
        _req("DELETE", f"/project/info/{project['id']}")
    
    def test_create_project_balance(self, setup_project_account):
        """测试创建项目余额"""
        balance_data = {
            "account_id": setup_project_account,
            "balance": 100.50,
            "variable": 10.25
        }
        result = _req("POST", "/project/balance", json=balance_data)
        assert result["message"] == "成功"
        assert float(result["balance"]) == balance_data["balance"]
        
        # 清理
        _req("DELETE", f"/project/balance/{result['id']}")
    
    def test_get_project_balance(self, setup_project_account):
        """测试获取单个项目余额"""
        balance_data = {
            "account_id": setup_project_account,
            "balance": 100.50,
            "variable": 10.25
        }
        created = _req("POST", "/project/balance", json=balance_data)
        bid = created["id"]
        
        result = _req("GET", f"/project/balance/{bid}")
        assert result["id"] == bid
        assert float(result["balance"]) == balance_data["balance"]
        
        # 清理
        _req("DELETE", f"/project/balance/{bid}")
    
    def test_list_project_balances(self, setup_project_account):
        """测试获取项目余额列表"""
        balance_data = {
            "account_id": setup_project_account,
            "balance": 100.50,
            "variable": 10.25
        }
        created = _req("POST", "/project/balance", json=balance_data)
        bid = created["id"]
        
        result = _req("GET", "/project/balance", params={
            "account_id": setup_project_account,
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/project/balance/{bid}")
    
    def test_update_project_balance(self, setup_project_account):
        """测试更新项目余额"""
        balance_data = {
            "account_id": setup_project_account,
            "balance": 100.50,
            "variable": 10.25
        }
        created = _req("POST", "/project/balance", json=balance_data)
        bid = created["id"]
        
        update_data = {"balance": 200.75, "variable": 20.50}
        result = _req("PUT", f"/project/balance/{bid}", json=update_data)
        assert float(result["balance"]) == update_data["balance"]
        
        # 清理
        _req("DELETE", f"/project/balance/{bid}")


class TestProjectWallet:
    """项目钱包接口测试"""
    
    @pytest.fixture
    def setup_project(self):
        """创建测试用的项目"""
        project = _req("POST", "/project/info", json={
            "name": f"测试项目-{uuid.uuid4().hex[:6]}",
            "status": 1
        })
        yield project["id"]
        # 清理
        _req("DELETE", f"/project/info/{project['id']}")
    
    def test_create_project_wallet(self, setup_project):
        """测试创建项目钱包"""
        wallet_data = {
            "private_key": f"private_key_{uuid.uuid4().hex}",
            "public_key": f"public_key_{uuid.uuid4().hex}",
            "mnemonic": f"mnemonic_{uuid.uuid4().hex}",
            "project_id": setup_project
        }
        result = _req("POST", "/project/wallet", json=wallet_data)
        assert result["message"] == "成功"
        assert result["public_key"] == wallet_data["public_key"]
        
        # 清理
        _req("DELETE", f"/project/wallet/{result['id']}")
    
    def test_get_project_wallet(self, setup_project):
        """测试获取单个项目钱包"""
        wallet_data = {
            "private_key": f"private_key_{uuid.uuid4().hex}",
            "public_key": f"public_key_{uuid.uuid4().hex}",
            "mnemonic": f"mnemonic_{uuid.uuid4().hex}",
            "project_id": setup_project
        }
        created = _req("POST", "/project/wallet", json=wallet_data)
        wid = created["id"]
        
        result = _req("GET", f"/project/wallet/{wid}")
        assert result["id"] == wid
        assert result["public_key"] == wallet_data["public_key"]
        
        # 清理
        _req("DELETE", f"/project/wallet/{wid}")
    
    def test_list_project_wallets(self, setup_project):
        """测试获取项目钱包列表"""
        wallet_data = {
            "private_key": f"private_key_{uuid.uuid4().hex}",
            "public_key": f"public_key_{uuid.uuid4().hex}",
            "mnemonic": f"mnemonic_{uuid.uuid4().hex}",
            "project_id": setup_project
        }
        created = _req("POST", "/project/wallet", json=wallet_data)
        wid = created["id"]
        
        result = _req("GET", "/project/wallet", params={
            "project_id": setup_project,
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
        
        # 清理
        _req("DELETE", f"/project/wallet/{wid}")
    
    def test_update_project_wallet(self, setup_project):
        """测试更新项目钱包"""
        wallet_data = {
            "private_key": f"private_key_{uuid.uuid4().hex}",
            "public_key": f"public_key_{uuid.uuid4().hex}",
            "mnemonic": f"mnemonic_{uuid.uuid4().hex}",
            "project_id": setup_project
        }
        created = _req("POST", "/project/wallet", json=wallet_data)
        wid = created["id"]
        
        update_data = {"mnemonic": f"new_mnemonic_{uuid.uuid4().hex}"}
        result = _req("PUT", f"/project/wallet/{wid}", json=update_data)
        assert result["mnemonic"] == update_data["mnemonic"]
        
        # 清理
        _req("DELETE", f"/project/wallet/{wid}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
