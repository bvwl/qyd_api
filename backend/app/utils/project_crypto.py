"""
项目账号敏感数据加密/解密工具

用于处理项目账号的敏感信息：
- password 字段（与 data 同级）
- data 字段中所有层级的 private_key 和 mnemonic

加密方式：
- key: MD5(账号 + "9527")
- iv: MD5("9527" + 账号)
"""

import copy
import base64
import binascii
from typing import Any
from app.core.tools import aes_encrypt_project, aes_decrypt_project


def encrypt_sensitive_fields(data: dict | list | Any, account: str) -> dict | list | Any:
    """
    递归加密 JSON 数据中所有层级的 private_key 和 mnemonic 字段
    
    :param data: 原始数据（dict、list 或其他类型）
    :param account: 项目账号（用于生成加密密钥）
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
                    data[key] = aes_encrypt_project(value, account)
                except Exception as e:
                    # 加密失败，记录错误但不中断流程
                    print(f"加密字段 {key} 失败: {e}")
            # 递归处理嵌套的 dict 或 list
            elif isinstance(value, (dict, list)):
                data[key] = encrypt_sensitive_fields(value, account)
    
    elif isinstance(data, list):
        data = [encrypt_sensitive_fields(item, account) for item in data]
    
    return data


def decrypt_sensitive_fields(data: dict | list | Any, account: str) -> dict | list | Any:
    """
    递归解密 JSON 数据中所有层级的 private_key 和 mnemonic 字段
    
    :param data: 加密的数据（dict、list 或其他类型）
    :param account: 项目账号（用于生成解密密钥）
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
                    data[key] = aes_decrypt_project(value, account)
                except Exception as e:
                    # 解密失败，保持原值（可能已经是明文或加密失败）
                    print(f"解密字段 {key} 失败: {e}")
            # 递归处理嵌套的 dict 或 list
            elif isinstance(value, (dict, list)):
                data[key] = decrypt_sensitive_fields(value, account)
    
    elif isinstance(data, list):
        data = [decrypt_sensitive_fields(item, account) for item in data]
    
    return data


def encrypt_password(password: str, account: str) -> str:
    """
    加密项目账号的 password 字段
    
    :param password: 原始密码
    :param account: 项目账号（用于生成加密密钥）
    :return: 加密后的密码
    """
    if not password:
        return password
    
    try:
        return aes_encrypt_project(password, account)
    except Exception as e:
        print(f"加密 password 失败: {e}")
        return password


def decrypt_password(encrypted_password: str, account: str) -> str:
    """
    解密项目账号的 password 字段
    
    :param encrypted_password: 加密的密码
    :param account: 项目账号（用于生成解密密钥）
    :return: 解密后的密码
    """
    if not encrypted_password:
        return encrypted_password

    try:
        encrypted_bytes = base64.b64decode(encrypted_password, validate=True)
    except (binascii.Error, ValueError):
        # 历史数据可能是明文或旧格式，直接原样返回，避免日志刷屏。
        return encrypted_password

    if len(encrypted_bytes) == 0 or len(encrypted_bytes) % 16 != 0:
        # AES-CBC 密文长度必须是 16 字节倍数；不满足则视为明文/旧格式。
        return encrypted_password
    
    try:
        return aes_decrypt_project(encrypted_password, account)
    except Exception:
        return encrypted_password


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
    
    account = "test_account@example.com"
    password = "test_password_123"
    
    print("原始数据:")
    print(test_data)
    print(f"原始密码: {password}")
    print()
    
    # 加密 data 字段
    encrypted_data = encrypt_sensitive_fields(test_data, account)
    print("加密后的 data:")
    print(encrypted_data)
    print()
    
    # 加密 password 字段
    encrypted_password = encrypt_password(password, account)
    print(f"加密后的 password: {encrypted_password}")
    print()
    
    # 解密 data 字段
    decrypted_data = decrypt_sensitive_fields(encrypted_data, account)
    print("解密后的 data:")
    print(decrypted_data)
    print()
    
    # 解密 password 字段
    decrypted_password = decrypt_password(encrypted_password, account)
    print(f"解密后的 password: {decrypted_password}")
    print()
    
    # 验证
    print("验证解密是否正确:")
    print(f"private_key: {test_data['private_key'] == decrypted_data['private_key']}")
    print(f"mnemonic: {test_data['mnemonic'] == decrypted_data['mnemonic']}")
    print(f"nested.private_key: {test_data['nested']['private_key'] == decrypted_data['nested']['private_key']}")
    print(f"list[0].private_key: {test_data['list_data'][0]['private_key'] == decrypted_data['list_data'][0]['private_key']}")
    print(f"password: {password == decrypted_password}")
