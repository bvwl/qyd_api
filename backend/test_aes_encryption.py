#!/usr/bin/env python3
"""
测试 AES 加密解密功能
"""
import sys
sys.path.insert(0, '.')

from app.core.tools import aes_encrypt, aes_decrypt


def test_aes_encryption():
    """测试 AES 加密解密"""
    
    # 测试数据
    user_id = "7233165c-cbae-4e67-9573-45df6ef322ec"
    password = "TestPassword123!@#"
    
    print("=" * 60)
    print("AES 加密解密测试")
    print("=" * 60)
    
    # 加密
    print(f"\n原始密码: {password}")
    print(f"用户ID: {user_id}")
    
    encrypted = aes_encrypt(password, user_id)
    print(f"\n加密后 (Base64): {encrypted}")
    print(f"加密后长度: {len(encrypted)} 字符")
    
    # 解密
    decrypted = aes_decrypt(encrypted, user_id)
    print(f"\n解密后: {decrypted}")
    
    # 验证
    if password == decrypted:
        print("\n✅ 加密解密测试通过！")
    else:
        print("\n❌ 加密解密测试失败！")
        return False
    
    # 测试不同用户ID
    print("\n" + "=" * 60)
    print("测试不同用户使用不同密钥")
    print("=" * 60)
    
    user_id_2 = "12345678-1234-1234-1234-123456789012"
    encrypted_2 = aes_encrypt(password, user_id_2)
    
    print(f"\n用户1加密: {encrypted}")
    print(f"用户2加密: {encrypted_2}")
    
    if encrypted != encrypted_2:
        print("\n✅ 不同用户使用不同密钥！")
    else:
        print("\n❌ 不同用户使用相同密钥（错误）！")
        return False
    
    # 测试用户1的密文不能用用户2的密钥解密
    try:
        wrong_decrypt = aes_decrypt(encrypted, user_id_2)
        print(f"\n❌ 错误：用户2能解密用户1的密码: {wrong_decrypt}")
        return False
    except Exception as e:
        print(f"\n✅ 正确：用户2无法解密用户1的密码")
    
    # 测试多种密码
    print("\n" + "=" * 60)
    print("测试多种密码格式")
    print("=" * 60)
    
    test_passwords = [
        "simple",
        "Complex@Pass123",
        "中文密码测试",
        "!@#$%^&*()_+-=[]{}|;:',.<>?/",
        "a" * 100,  # 长密码
    ]
    
    for pwd in test_passwords:
        enc = aes_encrypt(pwd, user_id)
        dec = aes_decrypt(enc, user_id)
        if pwd == dec:
            print(f"✅ 密码测试通过: {pwd[:20]}{'...' if len(pwd) > 20 else ''}")
        else:
            print(f"❌ 密码测试失败: {pwd}")
            return False
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_aes_encryption()
    sys.exit(0 if success else 1)
