#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试项目账号敏感数据加密功能
"""

from app.utils.project_crypto import encrypt_sensitive_fields, decrypt_sensitive_fields, check_user_can_decrypt


def test_encryption():
    """测试加密和解密功能"""
    print("=" * 60)
    print("测试项目账号敏感数据加密功能")
    print("=" * 60)
    
    # 测试数据
    test_data = {
        "address": "0x1234567890abcdef",
        "private_key": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "mnemonic": "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12",
        "balance": 100.5,
        "nested": {
            "private_key": "nested_private_key_value",
            "other_field": "other_value",
            "deep_nested": {
                "mnemonic": "deep nested mnemonic value"
            }
        },
        "list_data": [
            {
                "private_key": "list_private_key_1",
                "mnemonic": "list mnemonic 1",
                "index": 0
            },
            {
                "private_key": "list_private_key_2",
                "index": 1
            },
            {
                "mnemonic": "list mnemonic 3",
                "index": 2
            }
        ],
        "normal_field": "this should not be encrypted"
    }
    
    project_name = "测试项目"
    
    print("\n1. 原始数据:")
    print("-" * 60)
    import json
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    # 加密
    print("\n2. 加密后的数据:")
    print("-" * 60)
    encrypted_data = encrypt_sensitive_fields(test_data, project_name)
    print(json.dumps(encrypted_data, indent=2, ensure_ascii=False))
    
    # 验证敏感字段已加密
    print("\n3. 验证敏感字段已加密:")
    print("-" * 60)
    print(f"✓ private_key 已加密: {encrypted_data['private_key'] != test_data['private_key']}")
    print(f"✓ mnemonic 已加密: {encrypted_data['mnemonic'] != test_data['mnemonic']}")
    print(f"✓ nested.private_key 已加密: {encrypted_data['nested']['private_key'] != test_data['nested']['private_key']}")
    print(f"✓ nested.deep_nested.mnemonic 已加密: {encrypted_data['nested']['deep_nested']['mnemonic'] != test_data['nested']['deep_nested']['mnemonic']}")
    print(f"✓ list[0].private_key 已加密: {encrypted_data['list_data'][0]['private_key'] != test_data['list_data'][0]['private_key']}")
    print(f"✓ list[0].mnemonic 已加密: {encrypted_data['list_data'][0]['mnemonic'] != test_data['list_data'][0]['mnemonic']}")
    print(f"✓ normal_field 未加密: {encrypted_data['normal_field'] == test_data['normal_field']}")
    
    # 解密
    print("\n4. 解密后的数据:")
    print("-" * 60)
    decrypted_data = decrypt_sensitive_fields(encrypted_data, project_name)
    print(json.dumps(decrypted_data, indent=2, ensure_ascii=False))
    
    # 验证解密是否正确
    print("\n5. 验证解密是否正确:")
    print("-" * 60)
    print(f"✓ private_key: {test_data['private_key'] == decrypted_data['private_key']}")
    print(f"✓ mnemonic: {test_data['mnemonic'] == decrypted_data['mnemonic']}")
    print(f"✓ nested.private_key: {test_data['nested']['private_key'] == decrypted_data['nested']['private_key']}")
    print(f"✓ nested.deep_nested.mnemonic: {test_data['nested']['deep_nested']['mnemonic'] == decrypted_data['nested']['deep_nested']['mnemonic']}")
    print(f"✓ list[0].private_key: {test_data['list_data'][0]['private_key'] == decrypted_data['list_data'][0]['private_key']}")
    print(f"✓ list[0].mnemonic: {test_data['list_data'][0]['mnemonic'] == decrypted_data['list_data'][0]['mnemonic']}")
    print(f"✓ list[1].private_key: {test_data['list_data'][1]['private_key'] == decrypted_data['list_data'][1]['private_key']}")
    print(f"✓ list[2].mnemonic: {test_data['list_data'][2]['mnemonic'] == decrypted_data['list_data'][2]['mnemonic']}")
    print(f"✓ normal_field: {test_data['normal_field'] == decrypted_data['normal_field']}")


def test_permission():
    """测试权限检查功能"""
    print("\n" + "=" * 60)
    print("测试权限检查功能")
    print("=" * 60)
    
    # 测试场景
    scenarios = [
        {
            "name": "管理员用户",
            "user_id": "user-123",
            "user_roles": ["ADMIN"],
            "project_user_ids": ["user-456"],
            "expected": True
        },
        {
            "name": "项目所属人",
            "user_id": "user-123",
            "user_roles": ["MANUAL"],
            "project_user_ids": ["user-123", "user-456"],
            "expected": True
        },
        {
            "name": "非项目所属人",
            "user_id": "user-123",
            "user_roles": ["MANUAL"],
            "project_user_ids": ["user-456", "user-789"],
            "expected": False
        },
        {
            "name": "GM用户（非项目所属人）",
            "user_id": "user-123",
            "user_roles": ["GM"],
            "project_user_ids": ["user-456"],
            "expected": False
        },
    ]
    
    for scenario in scenarios:
        result = check_user_can_decrypt(
            scenario["user_id"],
            scenario["user_roles"],
            scenario["project_user_ids"]
        )
        status = "✓" if result == scenario["expected"] else "✗"
        print(f"{status} {scenario['name']}: {result} (期望: {scenario['expected']})")


def test_different_projects():
    """测试不同项目使用不同密钥"""
    print("\n" + "=" * 60)
    print("测试不同项目使用不同密钥")
    print("=" * 60)
    
    data = {
        "private_key": "test_private_key_12345",
        "mnemonic": "test mnemonic words"
    }
    
    project1 = "项目A"
    project2 = "项目B"
    
    # 使用项目A的密钥加密
    encrypted1 = encrypt_sensitive_fields(data, project1)
    print(f"\n项目A加密后的 private_key: {encrypted1['private_key'][:50]}...")
    
    # 使用项目B的密钥加密
    encrypted2 = encrypt_sensitive_fields(data, project2)
    print(f"项目B加密后的 private_key: {encrypted2['private_key'][:50]}...")
    
    # 验证不同项目的加密结果不同
    print(f"\n✓ 不同项目加密结果不同: {encrypted1['private_key'] != encrypted2['private_key']}")
    
    # 验证只能用对应项目的密钥解密
    decrypted1 = decrypt_sensitive_fields(encrypted1, project1)
    print(f"✓ 项目A密钥解密项目A数据: {decrypted1['private_key'] == data['private_key']}")
    
    decrypted2 = decrypt_sensitive_fields(encrypted2, project2)
    print(f"✓ 项目B密钥解密项目B数据: {decrypted2['private_key'] == data['private_key']}")
    
    # 尝试用错误的密钥解密（会失败）
    try:
        wrong_decrypt = decrypt_sensitive_fields(encrypted1, project2)
        print(f"✗ 项目B密钥解密项目A数据: 不应该成功")
    except Exception as e:
        print(f"✓ 项目B密钥无法解密项目A数据: {type(e).__name__}")


if __name__ == '__main__':
    test_encryption()
    test_permission()
    test_different_projects()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
