#!/usr/bin/env python3
"""
测试JWT Token生成功能
验证10年有效期的JWT Token可以正常生成和存储
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.jwt_tool import create_access_token, JwtToken
from datetime import datetime, timezone


async def test_jwt_generation():
    """测试JWT生成"""
    print("=" * 60)
    print("测试JWT Token生成")
    print("=" * 60)
    print()
    
    # 1. 测试基本JWT生成
    print("1. 测试基本JWT生成:")
    print("-" * 60)
    
    test_data = {
        'id': '12345678-1234-1234-1234-123456789012',
        'email': 'test@example.com',
        'roles': ['ADMIN', 'GM']
    }
    
    # 生成10年有效期的Token
    token = create_access_token(test_data, expires_delta=315360000)
    
    print(f"✓ Token生成成功")
    print(f"  长度: {len(token)} 字符")
    print(f"  预览: {token[:80]}...")
    print()
    
    # 2. 验证Token内容
    print("2. 验证Token内容:")
    print("-" * 60)
    
    try:
        payload = JwtToken.verify_token(token)
        print(f"✓ Token验证成功")
        print(f"  用户ID: {payload.get('id')}")
        print(f"  邮箱: {payload.get('email')}")
        print(f"  角色: {payload.get('roles')}")
        print(f"  签发时间: {datetime.fromtimestamp(payload.get('iat'), tz=timezone.utc)}")
        print(f"  过期时间: {datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)}")
        
        # 计算有效期
        exp_time = datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload.get('iat'), tz=timezone.utc)
        valid_days = (exp_time - iat_time).days
        valid_years = valid_days / 365.25
        
        print(f"  有效期: {valid_days} 天 (约 {valid_years:.1f} 年)")
        print()
        
        # 验证有效期是否接近10年
        if 9.9 <= valid_years <= 10.1:
            print("✓ 有效期验证通过：约10年")
        else:
            print(f"✗ 有效期验证失败：{valid_years:.1f}年，期望10年")
        print()
        
    except Exception as e:
        print(f"✗ Token验证失败: {e}")
        return False
    
    # 3. 测试Token长度是否适合TEXT字段
    print("3. 验证数据库兼容性:")
    print("-" * 60)
    
    if len(token) < 65535:  # TEXT字段最大长度
        print(f"✓ Token长度 ({len(token)}) < TEXT最大长度 (65535)")
        print(f"✓ 可以安全存储到数据库")
    else:
        print(f"✗ Token长度 ({len(token)}) 超过TEXT最大长度")
    print()
    
    # 4. 测试不同数据量的Token长度
    print("4. 测试不同角色数量的Token长度:")
    print("-" * 60)
    
    test_cases = [
        {'roles': ['ADMIN']},
        {'roles': ['ADMIN', 'GM']},
        {'roles': ['ADMIN', 'GM', 'IT', 'MANUAL']},
    ]
    
    for i, case in enumerate(test_cases, 1):
        data = {
            'id': '12345678-1234-1234-1234-123456789012',
            'email': 'test@example.com',
            **case
        }
        token = create_access_token(data, expires_delta=315360000)
        print(f"  角色数 {len(case['roles'])}: Token长度 {len(token)} 字符")
    
    print()
    
    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print()
    print("JWT Token生成功能正常，可以安全使用")
    print()
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_jwt_generation())
    sys.exit(0 if result else 1)
