#!/usr/bin/env python3
"""
测试仪表盘API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:6080/v1/user"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_dashboard():
    """测试仪表盘功能"""
    
    print_section("测试仪表盘API")
    
    # 测试不同角色的用户
    test_users = [
        {"email": "zhiyu", "password": "2201101122@qq.com", "role": "ADMIN"},
    ]
    
    for user_info in test_users:
        print(f"\n{'='*60}")
        print(f"  测试用户: {user_info['email']} ({user_info['role']})")
        print(f"{'='*60}\n")
        
        # 1. 登录
        print("1. 登录...")
        login_data = {
            "email": user_info['email'],
            "password": user_info['password']
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.text}")
            continue
        
        token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ 登录成功")
        
        # 2. 获取仪表盘统计
        print("\n2. 获取仪表盘统计...")
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if response.status_code != 200:
            print(f"❌ 获取统计失败: {response.text}")
            continue
        
        stats = response.json()
        print(f"✅ 统计数据:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        # 验证数据
        print(f"\n数据验证:")
        print(f"  角色: {stats['role']}")
        print(f"  用户邮箱: {stats['user_email']}")
        print(f"  用户昵称: {stats['user_nickname']}")
        print(f"  项目数量: {stats['project_count']}")
        print(f"  账户数量: {stats['account_count']}")
        
        if stats.get('user_count') is not None:
            print(f"  用户数量: {stats['user_count']} (仅管理员可见)")
        
        # 3. 获取项目列表
        print("\n3. 获取项目列表...")
        response = requests.get(f"{BASE_URL}/dashboard/projects", headers=headers)
        if response.status_code != 200:
            print(f"❌ 获取项目列表失败: {response.text}")
            continue
        
        projects = response.json()
        print(f"✅ 项目列表 (共 {len(projects)} 个):")
        
        if projects:
            print(f"\n{'项目名称':<30} {'账户数量':<10} {'状态':<10}")
            print("-" * 60)
            for project in projects[:10]:  # 只显示前10个
                print(f"{project['name']:<30} {project['account_count']:<10} {project['status']:<10}")
            
            if len(projects) > 10:
                print(f"... 还有 {len(projects) - 10} 个项目")
        else:
            print("  暂无项目")
    
    print_section("测试完成")
    print("✅ 仪表盘API测试通过！")
    
    return True

if __name__ == "__main__":
    try:
        import sys
        success = test_dashboard()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
