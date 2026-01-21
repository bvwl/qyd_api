#!/usr/bin/env python3
"""
JWT功能测试脚本
测试JWT token的生成和验证
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.jwt_tool import JwtToken
from app.core import settings

def test_jwt_config():
    """测试JWT配置"""
    print("=" * 50)
    print("测试1: JWT配置")
    print("=" * 50)
    
    try:
        print(f"✓ JWT Secret Key: {settings.JWT['secret_key'][:10]}...")
        print(f"✓ JWT Algorithm: {settings.JWT['algorithm']}")
        print(f"✓ JWT Expire Time: {settings.JWT['expire_time']}秒")
        print("✓ JWT配置正常\n")
        return True
    except Exception as e:
        print(f"✗ JWT配置错误: {e}\n")
        return False


def test_create_token():
    """测试创建token"""
    print("=" * 50)
    print("测试2: 创建JWT Token")
    print("=" * 50)
    
    try:
        # 测试数据
        user_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "roles": ["USER", "ADMIN"]
        }
        
        # 创建token
        token = JwtToken.create_token(user_data)
        print(f"✓ Token创建成功")
        print(f"  Token长度: {len(token)}")
        print(f"  Token前50字符: {token[:50]}...")
        print()
        return token
    except Exception as e:
        print(f"✗ Token创建失败: {e}\n")
        return None


def test_verify_token(token):
    """测试验证token"""
    print("=" * 50)
    print("测试3: 验证JWT Token")
    print("=" * 50)
    
    try:
        # 验证token
        payload = JwtToken.verify_token(token)
        print(f"✓ Token验证成功")
        print(f"  用户ID: {payload.get('id')}")
        print(f"  邮箱: {payload.get('email')}")
        print(f"  角色: {payload.get('roles')}")
        print(f"  签发时间: {payload.get('iat')}")
        print(f"  过期时间: {payload.get('exp')}")
        print()
        return True
    except JwtToken.ExpiredSignatureError:
        print(f"✗ Token已过期\n")
        return False
    except JwtToken.JWTError as e:
        print(f"✗ Token验证失败: {e}\n")
        return False
    except Exception as e:
        print(f"✗ 未知错误: {e}\n")
        return False


def test_invalid_token():
    """测试无效token"""
    print("=" * 50)
    print("测试4: 无效Token处理")
    print("=" * 50)
    
    invalid_tokens = [
        "invalid.token.here",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
        ""
    ]
    
    for i, token in enumerate(invalid_tokens, 1):
        try:
            JwtToken.verify_token(token)
            print(f"✗ 测试{i}失败: 应该抛出异常")
            return False
        except (JwtToken.JWTError, Exception):
            print(f"✓ 测试{i}通过: 正确拒绝无效token")
    
    print()
    return True


def test_custom_expire_time():
    """测试自定义过期时间"""
    print("=" * 50)
    print("测试5: 自定义过期时间")
    print("=" * 50)
    
    try:
        user_data = {
            "id": "test-user",
            "email": "test@example.com"
        }
        
        # 创建1小时过期的token
        token = JwtToken.create_token(user_data, expire_time=3600)
        payload = JwtToken.verify_token(token)
        
        # 检查过期时间
        exp_time = payload.get('exp')
        iat_time = payload.get('iat')
        duration = exp_time - iat_time
        
        print(f"✓ 自定义过期时间设置成功")
        print(f"  设置时长: 3600秒 (1小时)")
        print(f"  实际时长: {duration}秒")
        print()
        return abs(duration - 3600) < 2  # 允许2秒误差
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("JWT功能测试")
    print("=" * 50 + "\n")
    
    results = []
    
    # 测试1: 配置
    results.append(("JWT配置", test_jwt_config()))
    
    # 测试2: 创建token
    token = test_create_token()
    results.append(("创建Token", token is not None))
    
    if token:
        # 测试3: 验证token
        results.append(("验证Token", test_verify_token(token)))
        
        # 测试4: 无效token
        results.append(("无效Token处理", test_invalid_token()))
        
        # 测试5: 自定义过期时间
        results.append(("自定义过期时间", test_custom_expire_time()))
    
    # 打印总结
    print("=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！JWT功能正常。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
