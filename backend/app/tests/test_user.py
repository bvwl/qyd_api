"""
用户相关接口测试
"""
import os
import uuid
import requests
import pytest


def _base_url() -> str:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "6080"))
    return f"http://{host}:{port}/v1"


def _req(method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
    url = _base_url() + path
    resp = requests.request(method, url, json=json, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


class TestUserAuth:
    """用户认证接口测试"""
    
    def test_register(self):
        """测试用户注册"""
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        result = _req("POST", "/user/auth/register", json=user_data)
        assert result["message"] == "成功"
        assert result["user"]["email"] == user_data["email"]
        assert "access_token" in result
        
        return result["user"]["id"]
    
    def test_login(self):
        """测试用户登录"""
        # 先注册
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        _req("POST", "/user/auth/register", json=user_data)
        
        # 登录
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        result = _req("POST", "/user/auth/login", json=login_data)
        assert result["message"] == "成功"
        assert result["user"]["email"] == user_data["email"]
        assert "access_token" in result
    
    def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        # 第一次注册
        _req("POST", "/user/auth/register", json=user_data)
        
        # 第二次注册相同邮箱，应该失败
        try:
            _req("POST", "/user/auth/register", json=user_data)
            assert False, "应该抛出异常"
        except requests.HTTPError as e:
            assert e.response.status_code == 400
    
    def test_login_wrong_password(self):
        """测试错误密码登录"""
        # 先注册
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        _req("POST", "/user/auth/register", json=user_data)
        
        # 使用错误密码登录
        login_data = {
            "email": user_data["email"],
            "password": "WrongPassword!"
        }
        try:
            _req("POST", "/user/auth/login", json=login_data)
            assert False, "应该抛出异常"
        except requests.HTTPError as e:
            assert e.response.status_code == 400


class TestUserManagement:
    """用户管理接口测试"""
    
    @pytest.fixture
    def setup_user(self):
        """创建测试用户"""
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        result = _req("POST", "/user/auth/register", json=user_data)
        return result["user"]["id"]
    
    def test_get_user(self, setup_user):
        """测试获取单个用户"""
        result = _req("GET", f"/user/user/{setup_user}")
        assert result["id"] == setup_user
    
    def test_list_users(self):
        """测试获取用户列表"""
        # 先创建一个用户
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        created = _req("POST", "/user/auth/register", json=user_data)
        
        # 获取用户列表
        result = _req("GET", "/user/user", params={
            "email": user_data["email"],
            "res_count": True
        })
        assert result["message"] == "成功"
        assert result["count"] >= 1
    
    def test_update_user(self, setup_user):
        """测试更新用户"""
        update_data = {
            "nickname": "更新后的昵称",
            "status": 1
        }
        result = _req("PUT", f"/user/user/{setup_user}", json=update_data)
        assert result["nickname"] == update_data["nickname"]
    
    def test_delete_user(self):
        """测试删除用户"""
        # 先创建一个用户
        user_data = {
            "email": f"test_user_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Test1234!",
            "nickname": "测试用户"
        }
        created = _req("POST", "/user/auth/register", json=user_data)
        uid = created["user"]["id"]
        
        # 删除用户
        result = _req("DELETE", f"/user/user/{uid}")
        assert result["message"] == "成功"
        
        # 验证用户已删除
        try:
            _req("GET", f"/user/user/{uid}")
            assert False, "应该抛出异常"
        except requests.HTTPError as e:
            assert e.response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
