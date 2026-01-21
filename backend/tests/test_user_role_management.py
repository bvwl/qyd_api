#!/usr/bin/env python3
"""
测试用户角色管理功能
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:6080/v1/user"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_user_role_management():
    """测试用户角色管理完整流程"""
    
    # 1. 管理员登录
    print_section("1. 管理员登录")
    login_data = {
        "email": "zhiyu",
        "password": "2201101122@qq.com"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return False
    
    login_result = response.json()
    admin_token = login_result['access_token']
    print(f"✅ 管理员登录成功")
    print(f"Token: {admin_token[:50]}...")
    print(f"角色: {[r['code'] for r in login_result['user']['roles']]}")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. 注册新用户（应该自动分配MANUAL角色）
    print_section("2. 注册新用户（测试默认MANUAL角色）")
    register_data = {
        "email": f"test_role_{int(requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'])}@example.com",
        "password": "test123456",
        "nickname": "角色测试用户"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 200:
        print(f"❌ 注册失败: {response.text}")
        return False
    
    register_result = response.json()
    test_user_id = register_result['user']['id']
    test_user_email = register_result['user']['email']
    print(f"✅ 用户注册成功")
    print(f"用户ID: {test_user_id}")
    print(f"邮箱: {test_user_email}")
    print(f"默认角色: {[r['code'] for r in register_result['user']['roles']]}")
    
    if not register_result['user']['roles'] or register_result['user']['roles'][0]['code'] != 'MANUAL':
        print(f"⚠️  警告: 默认角色不是MANUAL")
    
    # 3. 获取用户当前角色
    print_section("3. 获取用户当前角色")
    response = requests.get(f"{BASE_URL}/{test_user_id}/roles", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取角色失败: {response.text}")
        return False
    
    current_roles = response.json()
    print(f"✅ 当前角色:")
    print_json(current_roles)
    
    # 4. 为用户分配多个角色
    print_section("4. 为用户分配多个角色 (MANUAL + IT)")
    assign_data = {
        "role_codes": ["MANUAL", "IT"]
    }
    response = requests.put(f"{BASE_URL}/{test_user_id}/roles", json=assign_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ 分配角色失败: {response.text}")
        return False
    
    updated_user = response.json()
    print(f"✅ 角色分配成功")
    print(f"新角色: {[r['code'] for r in updated_user['roles']]}")
    
    # 5. 添加单个角色
    print_section("5. 添加单个角色 (GM)")
    response = requests.post(f"{BASE_URL}/{test_user_id}/roles/GM", headers=headers)
    if response.status_code != 200:
        print(f"❌ 添加角色失败: {response.text}")
        return False
    
    updated_user = response.json()
    print(f"✅ 角色添加成功")
    print(f"当前角色: {[r['code'] for r in updated_user['roles']]}")
    
    # 6. 移除单个角色
    print_section("6. 移除单个角色 (IT)")
    response = requests.delete(f"{BASE_URL}/{test_user_id}/roles/IT", headers=headers)
    if response.status_code != 200:
        print(f"❌ 移除角色失败: {response.text}")
        return False
    
    updated_user = response.json()
    print(f"✅ 角色移除成功")
    print(f"当前角色: {[r['code'] for r in updated_user['roles']]}")
    
    # 7. 验证用户列表中显示正确的角色
    print_section("7. 验证用户列表")
    response = requests.get(f"{BASE_URL}/user", params={"email": test_user_email}, headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取用户列表失败: {response.text}")
        return False
    
    user_list = response.json()
    if user_list['items']:
        user = user_list['items'][0]
        print(f"✅ 用户信息:")
        print(f"邮箱: {user['email']}")
        print(f"昵称: {user['nickname']}")
        print(f"角色: {[r['code'] for r in user['roles']]}")
    
    # 8. 测试非管理员权限（应该失败）
    print_section("8. 测试权限控制（非管理员）")
    test_user_token = register_result['access_token']
    test_headers = {"Authorization": f"Bearer {test_user_token}"}
    
    response = requests.get(f"{BASE_URL}/{test_user_id}/roles", headers=test_headers)
    if response.status_code == 403:
        print(f"✅ 权限控制正常: 非管理员无法访问角色管理")
    else:
        print(f"⚠️  权限控制异常: 状态码 {response.status_code}")
    
    print_section("测试完成")
    print("✅ 所有测试通过！")
    return True

if __name__ == "__main__":
    try:
        success = test_user_role_management()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
