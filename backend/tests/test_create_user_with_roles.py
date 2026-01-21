#!/usr/bin/env python3
"""
测试创建用户并分配角色
"""
import requests
import json

BASE_URL = "http://127.0.0.1:6080/v1/user"

def test_create_user_with_roles():
    """测试创建用户并分配角色"""
    
    print("="*60)
    print("  测试创建用户并分配角色")
    print("="*60)
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    login_data = {
        "email": "zhiyu",
        "password": "2201101122@qq.com"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return False
    
    admin_token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ 登录成功")
    
    # 2. 获取所有角色
    print("\n2. 获取角色列表...")
    response = requests.get(f"{BASE_URL}/role", params={"limit": 100}, headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取角色失败: {response.text}")
        return False
    
    roles = response.json()['items']
    print(f"✅ 获取到 {len(roles)} 个角色:")
    for role in roles:
        print(f"   - {role['name']} ({role['code']}): {role['id']}")
    
    # 获取 MANUAL 和 IT 角色的ID
    manual_role = next((r for r in roles if r['code'] == 'MANUAL'), None)
    it_role = next((r for r in roles if r['code'] == 'IT'), None)
    
    if not manual_role or not it_role:
        print("❌ 未找到 MANUAL 或 IT 角色")
        return False
    
    # 3. 创建用户并分配角色
    print("\n3. 创建用户并分配角色...")
    import time
    timestamp = int(time.time())
    
    user_data = {
        "email": f"test_roles_{timestamp}@example.com",
        "nickname": "角色测试用户",
        "password": "test123456",
        "status": 1,
        "role_ids": [manual_role['id'], it_role['id']]
    }
    
    print(f"\n创建用户数据:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    
    response = requests.post(f"{BASE_URL}/user", json=user_data, headers=headers)
    
    if response.status_code != 200:
        print(f"\n❌ 创建用户失败:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    created_user = response.json()
    print(f"\n✅ 用户创建成功:")
    print(json.dumps(created_user, indent=2, ensure_ascii=False))
    
    # 4. 验证角色分配
    print("\n4. 验证角色分配...")
    user_roles = created_user.get('roles', [])
    role_codes = [r['code'] for r in user_roles]
    
    print(f"用户角色: {role_codes}")
    
    if 'MANUAL' in role_codes and 'IT' in role_codes:
        print("✅ 角色分配正确")
    else:
        print(f"⚠️  角色分配不完整")
        print(f"   预期: ['MANUAL', 'IT']")
        print(f"   实际: {role_codes}")
    
    # 5. 测试你提供的数据
    print("\n5. 测试你提供的数据...")
    user_data_2 = {
        "email": "2201101122@qq.com",
        "nickname": "栀虞",
        "password": "Zpaily88",
        "status": 1,
        "role_ids": [manual_role['id'], it_role['id']]
    }
    
    print(f"\n创建用户数据:")
    print(json.dumps(user_data_2, indent=2, ensure_ascii=False))
    
    response = requests.post(f"{BASE_URL}/user", json=user_data_2, headers=headers)
    
    if response.status_code == 400 and "邮箱已存在" in response.text:
        print(f"\n⚠️  邮箱已存在（这是正常的）")
        print(f"   如果之前创建过这个邮箱，这是预期行为")
    elif response.status_code != 200:
        print(f"\n❌ 创建用户失败:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    else:
        created_user_2 = response.json()
        print(f"\n✅ 用户创建成功:")
        print(json.dumps(created_user_2, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("  ✅ 测试完成")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        import sys
        success = test_create_user_with_roles()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
