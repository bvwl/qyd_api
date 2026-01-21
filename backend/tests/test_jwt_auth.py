#!/usr/bin/env python3
"""测试JWT认证是否正常工作"""
import requests
import json

BASE_URL = "http://localhost:6080"

def test_jwt_auth():
    print("=" * 60)
    print("测试 JWT 认证")
    print("=" * 60)
    
    # 1. 登录获取JWT token
    print("\n1. 登录获取JWT token...")
    login_data = {
        "email": "zhiyu",
        "password": "2201101122@qq.com"
    }
    
    response = requests.post(f"{BASE_URL}/v1/user/auth/login", json=login_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return
    
    result = response.json()
    access_token = result.get("access_token")
    print(f"✓ 登录成功")
    print(f"JWT Token: {access_token[:50]}...")
    
    # 2. 使用JWT token访问受保护的API
    print("\n2. 使用JWT token访问用户列表...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/v1/user/user",
        headers=headers,
        params={"page": 1, "limit": 1, "res_count": "true"}
    )
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ JWT认证成功！")
        result = response.json()
        print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"✗ JWT认证失败: {response.text}")
    
    # 3. 测试其他API
    print("\n3. 测试项目信息API...")
    response = requests.get(
        f"{BASE_URL}/v1/project/info",
        headers=headers,
        params={"page": 1, "limit": 1, "res_count": "true"}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 项目信息API认证成功！")
    else:
        print(f"✗ 项目信息API认证失败: {response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_jwt_auth()
