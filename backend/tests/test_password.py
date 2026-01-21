#!/usr/bin/env python3
"""
密码加密功能测试
测试bcrypt密码加密和验证
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.core.tools import hashing

def test_password_hashing():
    """测试密码加密"""
    print("=" * 50)
    print("测试1: 密码加密")
    print("=" * 50)
    
    password = "test123456"
    
    try:
        # 加密密码
        hash1 = hashing.hash(password)
        print(f"✓ 密码加密成功")
        print(f"  原始密码: {password}")
        print(f"  加密结果: {hash1[:50]}...")
        print(f"  哈希长度: {len(hash1)}")
        
        # 再次加密同一密码（应该得到不同的哈希）
        hash2 = hashing.hash(password)
        print(f"\n✓ 再次加密同一密码")
        print(f"  加密结果: {hash2[:50]}...")
        print(f"  两次哈希不同: {hash1 != hash2}")
        print()
        
        return hash1, hash2
    except Exception as e:
        print(f"✗ 密码加密失败: {e}\n")
        return None, None


def test_password_verification(password, hash1, hash2):
    """测试密码验证"""
    print("=" * 50)
    print("测试2: 密码验证")
    print("=" * 50)
    
    try:
        # 验证正确的密码
        result1 = hashing.verify(password, hash1)
        print(f"✓ 验证正确密码（哈希1）: {result1}")
        
        result2 = hashing.verify(password, hash2)
        print(f"✓ 验证正确密码（哈希2）: {result2}")
        
        # 验证错误的密码
        result3 = hashing.verify("wrongpassword", hash1)
        print(f"✓ 验证错误密码: {result3}")
        
        # 验证空密码
        result4 = hashing.verify("", hash1)
        print(f"✓ 验证空密码: {result4}")
        
        print()
        return result1 and result2 and not result3 and not result4
    except Exception as e:
        print(f"✗ 密码验证失败: {e}\n")
        return False


def test_different_passwords():
    """测试不同密码"""
    print("=" * 50)
    print("测试3: 不同密码加密")
    print("=" * 50)
    
    passwords = ["123456", "password", "Test@123", "中文密码123"]
    
    try:
        for pwd in passwords:
            hash_value = hashing.hash(pwd)
            verify_result = hashing.verify(pwd, hash_value)
            print(f"✓ 密码: {pwd:15} | 验证: {verify_result}")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def test_edge_cases():
    """测试边界情况"""
    print("=" * 50)
    print("测试4: 边界情况")
    print("=" * 50)
    
    test_cases = [
        ("a", "单字符密码"),
        ("a" * 100, "100字符密码"),
        ("!@#$%^&*()", "特殊字符密码"),
        ("   spaces   ", "包含空格的密码"),
    ]
    
    try:
        for pwd, desc in test_cases:
            hash_value = hashing.hash(pwd)
            verify_result = hashing.verify(pwd, hash_value)
            status = "✓" if verify_result else "✗"
            print(f"{status} {desc:20} | 验证: {verify_result}")
        
        print()
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def test_security():
    """测试安全性"""
    print("=" * 50)
    print("测试5: 安全性测试")
    print("=" * 50)
    
    password = "securepassword"
    
    try:
        # 生成多个哈希，确保每次都不同（salt随机）
        hashes = [hashing.hash(password) for _ in range(5)]
        unique_hashes = len(set(hashes))
        
        print(f"✓ 生成5个哈希，唯一数量: {unique_hashes}")
        print(f"✓ 每次加密结果不同（使用随机salt）: {unique_hashes == 5}")
        
        # 验证所有哈希都能正确验证
        all_valid = all(hashing.verify(password, h) for h in hashes)
        print(f"✓ 所有哈希都能正确验证: {all_valid}")
        
        # 确保错误密码无法通过任何哈希验证
        none_valid = not any(hashing.verify("wrongpassword", h) for h in hashes)
        print(f"✓ 错误密码无法通过验证: {none_valid}")
        
        print()
        return unique_hashes == 5 and all_valid and none_valid
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("密码加密功能测试")
    print("=" * 50 + "\n")
    
    results = []
    
    # 测试1: 密码加密
    hash1, hash2 = test_password_hashing()
    results.append(("密码加密", hash1 is not None and hash2 is not None))
    
    if hash1 and hash2:
        # 测试2: 密码验证
        results.append(("密码验证", test_password_verification("test123456", hash1, hash2)))
        
        # 测试3: 不同密码
        results.append(("不同密码加密", test_different_passwords()))
        
        # 测试4: 边界情况
        results.append(("边界情况", test_edge_cases()))
        
        # 测试5: 安全性
        results.append(("安全性测试", test_security()))
    
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
        print("\n🎉 所有测试通过！密码加密功能正常。")
        print("\n💡 提示:")
        print("  - bcrypt自动使用随机salt，每次加密结果都不同")
        print("  - 即使密码相同，哈希值也不同，这是正常的")
        print("  - bcrypt.verify()会自动处理salt验证")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
