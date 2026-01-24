"""
项目账号敏感数据加密/解密工具

用于处理项目账号 data 字段中的敏感信息（private_key 和 mnemonic）
"""

import copy
from typing import Any
from app.core.tools import aes_encrypt_project, aes_decrypt_project


def encrypt_sensitive_fields(data: dict | list | Any, project_name: str) -> dict | list | Any:
    """
    递归加密 JSON 数据中所有层级的 private_key 和 mnemonic 字段
    
    :param data: 原始数据（dict、list 或其他类型）
    :param project_name: 项目名称（用于生成加密密钥）
    :return: 加密后的数据
    """
    if data is None:
        return None
    
    # 深拷贝，避免修改原始数据
    data = copy.deepcopy(data)
    
    if isinstance(data, dict):
        for key, value in data.items():
            # 如果是敏感字段且值为字符串，进行加密
            if key in ['private_key', 'mnemonic'] and isinstance(value, str) and value:
                try:
                    data[key] = aes_encrypt_project(value, project_name)
                except Exception as e:
                    # 加密失败，记录错误但不中断流程
                    print(f"加密字段 {key} 失败: {e}")
            # 递归处理嵌套的 dict 或 list
            elif isinstance(value, (dict, list)):
                data[key] = encrypt_sensitive_fields(value, project_name)
    
    elif isinstance(data, list):
        data = [encrypt_sensitive_fields(item, project_name) for item in data]
    
    return data


def decrypt_sensitive_fields(data: dict | list | Any, project_name: str) -> dict | list | Any:
    """
    递归解密 JSON 数据中所有层级的 private_key 和 mnemonic 字段
    
    :param data: 加密的数据（dict、list 或其他类型）
    :param project_name: 项目名称（用于生成解密密钥）
    :return: 解密后的数据
    """
    if data is None:
        return None
    
    # 深拷贝，避免修改原始数据
    data = copy.deepcopy(data)
    
    if isinstance(data, dict):
        for key, value in data.items():
            # 如果是敏感字段且值为字符串，进行解密
            if key in ['private_key', 'mnemonic'] and isinstance(value, str) and value:
                try:
                    data[key] = aes_decrypt_project(value, project_name)
                except Exception as e:
                    # 解密失败，保持原值（可能已经是明文或加密失败）
                    print(f"解密字段 {key} 失败: {e}")
            # 递归处理嵌套的 dict 或 list
            elif isinstance(value, (dict, list)):
                data[key] = decrypt_sensitive_fields(value, project_name)
    
    elif isinstance(data, list):
        data = [decrypt_sensitive_fields(item, project_name) for item in data]
    
    return data


def check_user_can_decrypt(user_id: str, user_roles: list[str], project_user_ids: list[str]) -> bool:
    """
    检查用户是否有权限解密项目敏感数据
    
    :param user_id: 当前用户ID
    :param user_roles: 当前用户的角色列表
    :param project_user_ids: 项目所属用户ID列表
    :return: True 表示可以解密，False 表示不能解密
    """
    # 管理员可以解密所有项目
    if 'ADMIN' in user_roles:
        return True
    
    # 项目所属人可以解密
    if user_id in project_user_ids:
        return True
    
    return False


if __name__ == '__main__':
    # 测试加密和解密
    test_data = {
        "address": "0x1234567890",
        "private_key": "0xabcdef1234567890",
        "mnemonic": "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12",
        "nested": {
            "private_key": "nested_private_key",
            "other_field": "other_value"
        },
        "list_data": [
            {
                "private_key": "list_private_key_1",
                "mnemonic": "list mnemonic 1"
            },
            {
                "private_key": "list_private_key_2"
            }
        ]
    }
    
    project_name = "测试项目"
    
    print("原始数据:")
    print(test_data)
    print()
    
    # 加密
    encrypted_data = encrypt_sensitive_fields(test_data, project_name)
    print("加密后:")
    print(encrypted_data)
    print()
    
    # 解密
    decrypted_data = decrypt_sensitive_fields(encrypted_data, project_name)
    print("解密后:")
    print(decrypted_data)
    print()
    
    # 验证
    print("验证解密是否正确:")
    print(f"private_key: {test_data['private_key'] == decrypted_data['private_key']}")
    print(f"mnemonic: {test_data['mnemonic'] == decrypted_data['mnemonic']}")
    print(f"nested.private_key: {test_data['nested']['private_key'] == decrypted_data['nested']['private_key']}")
    print(f"list[0].private_key: {test_data['list_data'][0]['private_key'] == decrypted_data['list_data'][0]['private_key']}")
