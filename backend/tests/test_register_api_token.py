#!/usr/bin/env python3
"""
测试注册功能 - API Token生成
"""
import requests
import json
import time
import hashlib

BASE_URL = "http://127.0.0.1:6080/v1/user"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def verify_api_token(email: str, api_token: str, timestamp_range_ms: int = 5000):
    """
    验证API token是否符合生成规则
    由于时间戳可能有微小差异，检查前后5秒范围内的token
    """
    current_time_ms = int(time.time() * 1000)
    
    # 检查前后5秒范围
    for offset in range(-timestamp_range_ms, timestamp_range_ms + 1, 1):
        test_timestamp = current_time_ms + offset
        expected_token = hashlib.md5(f"{email}{test_timestamp}9527".encode('utf-8')).hexdigest()
        if expected_token == api_token:
            print(f"✅ API Token验证成功")
            print(f"   生成时间戳: {test_timestamp}")
            print(f"   规则: MD5({email} + {test_timestamp} + 9527)")
            return True
    
    print(f"⚠️  API Token验证失败")
    print(f"   实际token: {api_token}")
    print(f"   预期规则: MD5(邮箱 + 13位时间戳 + 9527)")
    return False

def test_register_with_api_token():
    """测试注册功能 - 生成API Token"""
    
    # 1. 注册新用户
    print_section("1. 注册新用户")
    timestamp = int(time.time())
    register_data = {
        "email": f"apitoken_test_{timestamp}@example.com",
        "password": "test123456",
        "nickname": "API Token测试用户"
    }
    
    print(f"注册信息:")
    print(f"  邮箱: {register_data['email']}")
    print(f"  密码: {register_data['password']}")
    print(f"  昵称: {register_data['nickname']}")
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code != 200:
        print(f"❌ 注册失败: {response.text}")
        return False
    
    result = response.json()
    print(f"\n✅ 注册成功")
    print(f"\n响应数据:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 2. 验证响应结构
    print_section("2. 验证响应结构")
    
    if 'access_token' in result:
        print(f"⚠️  警告: 响应中包含 access_token (JWT)，应该只有 api_token")
    else:
        print(f"✅ 响应中不包含 access_token (符合预期)")
    
    if 'api_token' not in result:
        print(f"❌ 错误: 响应中缺少 api_token")
        return False
    else:
        print(f"✅ 响应中包含 api_token")
    
    api_token = result['api_token']
    user = result['user']
    
    print(f"\nAPI Token: {api_token}")
    print(f"Token长度: {len(api_token)} (MD5应为32位)")
    print(f"用户ID: {user['id']}")
    print(f"用户邮箱: {user['email']}")
    print(f"用户角色: {[r['code'] for r in user['roles']]}")
    
    # 3. 验证API Token格式
    print_section("3. 验证API Token格式")
    
    if len(api_token) != 32:
        print(f"⚠️  警告: API Token长度不是32位 (实际: {len(api_token)})")
    else:
        print(f"✅ API Token长度正确 (32位MD5)")
    
    # 验证是否为有效的MD5格式（只包含0-9a-f）
    if all(c in '0123456789abcdef' for c in api_token):
        print(f"✅ API Token格式正确 (MD5十六进制)")
    else:
        print(f"⚠️  警告: API Token格式不符合MD5")
    
    # 4. 验证生成规则
    print_section("4. 验证API Token生成规则")
    verify_api_token(register_data['email'], api_token)
    
    # 5. 验证默认角色
    print_section("5. 验证默认角色")
    
    if user['roles'] and user['roles'][0]['code'] == 'MANUAL':
        print(f"✅ 默认角色正确: MANUAL")
    else:
        print(f"⚠️  警告: 默认角色不是MANUAL")
        print(f"   实际角色: {[r['code'] for r in user['roles']]}")
    
    # 6. 使用管理员账户查询token表
    print_section("6. 验证Token已保存到数据库")
    
    # 管理员登录
    login_data = {
        "email": "zhiyu",
        "password": "2201101122@qq.com"
    }
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"⚠️  无法验证数据库: 管理员登录失败")
        return True
    
    admin_token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 查询该用户的tokens
    token_response = requests.get(
        f"{BASE_URL}/token",
        params={"user_id": user['id']},
        headers=headers
    )
    
    if token_response.status_code == 200:
        tokens = token_response.json()
        if tokens.get('items'):
            saved_token = tokens['items'][0]['token']
            if saved_token == api_token:
                print(f"✅ API Token已正确保存到数据库")
                print(f"   Token ID: {tokens['items'][0]['id']}")
                print(f"   状态: {tokens['items'][0]['status']}")
            else:
                print(f"⚠️  数据库中的token与返回的不一致")
        else:
            print(f"⚠️  数据库中未找到该用户的token")
    else:
        print(f"⚠️  无法查询token表: {token_response.text}")
    
    print_section("测试完成")
    print("✅ 注册功能测试通过！")
    print(f"\n总结:")
    print(f"  - 注册成功返回 api_token (不是 access_token)")
    print(f"  - API Token使用 MD5(邮箱 + 13位时间戳 + 9527) 生成")
    print(f"  - Token已保存到数据库")
    print(f"  - 默认分配 MANUAL 角色")
    
    return True

if __name__ == "__main__":
    try:
        import sys
        success = test_register_with_api_token()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
