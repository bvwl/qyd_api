import string, secrets
from passlib.context import CryptContext
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64


# 密码工具类
class Hashing:
    """密码工具类 - 使用bcrypt加密"""

    def __init__(self, schemes: str = 'bcrypt'):
        self.crypt = CryptContext(schemes=[schemes], deprecated="auto")

    def hash(self, raw_pwd: str) -> str:
        """
        密码加密
        :param raw_pwd: 用户输入的原始密码
        :return: 密码的哈希值
        """
        # bcrypt限制密码长度为72字节，超过部分会被截断
        if len(raw_pwd.encode('utf-8')) > 72:
            raw_pwd = raw_pwd[:72]
        return self.crypt.hash(raw_pwd)

    def verify(self, raw_pwd: str, hashed_pwd: str) -> bool:
        """
        验证密码是否正确
        :param raw_pwd: 用户输入的原始密码
        :param hashed_pwd: 密码的哈希值
        :return: bool
        """
        # bcrypt限制密码长度为72字节
        if len(raw_pwd.encode('utf-8')) > 72:
            raw_pwd = raw_pwd[:72]
        return self.crypt.verify(raw_pwd, hashed_pwd)


def aes_encrypt(plaintext: str, user_id: str) -> str:
    """
    使用AES加密密码（用于SOCKS5代理账号密码）
    - 每个用户使用不同的密钥和IV
    - key: MD5(user_id + "9527")
    - iv: MD5("9527" + user_id) 取前16位
    
    :param plaintext: 原始密码
    :param user_id: 用户ID（UUID字符串）
    :return: Base64编码的加密密文
    """
    # 生成密钥：MD5(user_id + "9527")
    key_string = f"{user_id}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + user_id) 取前16位
    iv_string = f"9527{user_id}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # 创建AES加密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 填充明文到16字节的倍数
    padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
    
    # 加密
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # Base64编码返回
    return base64.b64encode(ciphertext).decode('utf-8')


def aes_decrypt(ciphertext: str, user_id: str) -> str:
    """
    使用AES解密密码（用于SOCKS5代理账号密码）
    - 每个用户使用不同的密钥和IV
    - key: MD5(user_id + "9527")
    - iv: MD5("9527" + user_id) 取前16位
    
    :param ciphertext: Base64编码的加密密文
    :param user_id: 用户ID（UUID字符串）
    :return: 原始密码
    """
    # 生成密钥：MD5(user_id + "9527")
    key_string = f"{user_id}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + user_id) 取前16位
    iv_string = f"9527{user_id}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # Base64解码
    encrypted_data = base64.b64decode(ciphertext)
    
    # 创建AES解密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 解密
    padded_plaintext = cipher.decrypt(encrypted_data)
    
    # 去除填充
    plaintext = unpad(padded_plaintext, AES.block_size)
    
    return plaintext.decode('utf-8')


def aes_encrypt_project(plaintext: str, account: str) -> str:
    """
    使用AES加密项目敏感数据（用于项目账号的 password、private_key 和 mnemonic）
    - 每个账号使用不同的密钥和IV
    - key: MD5(账号 + "9527")
    - iv: MD5("9527" + 账号) 取前16位
    
    :param plaintext: 原始数据
    :param account: 项目账号
    :return: Base64编码的加密密文
    """
    # 生成密钥：MD5(账号 + "9527")
    key_string = f"{account}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + 账号) 取前16位
    iv_string = f"9527{account}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # 创建AES加密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 填充明文到16字节的倍数
    padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
    
    # 加密
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # Base64编码返回
    return base64.b64encode(ciphertext).decode('utf-8')


def aes_decrypt_project(ciphertext: str, account: str) -> str:
    """
    使用AES解密项目敏感数据（用于项目账号的 password、private_key 和 mnemonic）
    - 每个账号使用不同的密钥和IV
    - key: MD5(账号 + "9527")
    - iv: MD5("9527" + 账号) 取前16位
    
    :param ciphertext: Base64编码的加密密文
    :param account: 项目账号
    :return: 原始数据
    """
    # 生成密钥：MD5(账号 + "9527")
    key_string = f"{account}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + 账号) 取前16位
    iv_string = f"9527{account}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # Base64解码
    encrypted_data = base64.b64decode(ciphertext)
    
    # 创建AES解密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 解密
    padded_plaintext = cipher.decrypt(encrypted_data)
    
    # 去除填充
    plaintext = unpad(padded_plaintext, AES.block_size)
    
    return plaintext.decode('utf-8')


def aes_encrypt_wallet(plaintext: str, project_name: str) -> str:
    """
    使用AES加密钱包敏感数据（用于项目钱包的 private_key 和 mnemonic）
    - 每个项目使用不同的密钥和IV
    - key: MD5(项目名称 + "9527")
    - iv: MD5("9527" + 项目名称) 取前16位
    
    :param plaintext: 原始数据（私钥或助记词）
    :param project_name: 项目名称
    :return: Base64编码的加密密文
    """
    # 生成密钥：MD5(项目名称 + "9527")
    key_string = f"{project_name}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + 项目名称) 取前16位
    iv_string = f"9527{project_name}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # 创建AES加密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 填充明文到16字节的倍数
    padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
    
    # 加密
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # Base64编码返回
    return base64.b64encode(ciphertext).decode('utf-8')


def aes_decrypt_wallet(ciphertext: str, project_name: str) -> str:
    """
    使用AES解密钱包敏感数据（用于项目钱包的 private_key 和 mnemonic）
    - 每个项目使用不同的密钥和IV
    - key: MD5(项目名称 + "9527")
    - iv: MD5("9527" + 项目名称) 取前16位
    
    :param ciphertext: Base64编码的加密密文
    :param project_name: 项目名称
    :return: 原始数据（私钥或助记词）
    """
    # 生成密钥：MD5(项目名称 + "9527")
    key_string = f"{project_name}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()  # 16字节
    
    # 生成IV：MD5("9527" + 项目名称) 取前16位
    iv_string = f"9527{project_name}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]  # 16字节
    
    # Base64解码
    encrypted_data = base64.b64decode(ciphertext)
    
    # 创建AES解密器（CBC模式）
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 解密
    padded_plaintext = cipher.decrypt(encrypted_data)
    
    # 去除填充
    plaintext = unpad(padded_plaintext, AES.block_size)
    
    return plaintext.decode('utf-8')


def genint(length: int = 4) -> str:
    """
    生成指定长度的纯数字字符串
    @param length: 字符长度
    return
    """
    characters = string.digits
    ret = "".join(secrets.choice(characters) for i in range(length))
    return ret


def genkey(length: int = 64) -> str:
    """
    生成指定长度的随机字符串
    :param length: 生成的字符串的长度
    :return: 字符串
    """
    characters = string.ascii_letters  # 26个小写字母和26个大写字母
    characters = characters + string.digits  # 10个数字
    characters = characters + '!@$%^&*./-'  # 特殊符号
    return "".join(secrets.choice(characters) for i in range(length))


def gen_api_token(username: str, timestamp: int) -> str:
    """
    生成API Token
    规则: MD5(用户名 + 13位时间戳 + "9527")
    :param username: 用户名
    :param timestamp: 13位时间戳（毫秒）
    :return: API Token (32位MD5字符串)
    """
    import hashlib
    raw_string = f"{username}{timestamp}9527"
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()


hashing = Hashing()

if __name__ == '__main__':
    hashing = Hashing()
    # 对原始密码进行哈希加密
    password_hash1 = hashing.hash("123456")
    print(password_hash1)
    password_hash2 = hashing.hash("123456")
    print(password_hash2)

    # 判断原始密码是否和密码哈希值是否匹配
    ret = hashing.verify("123455", password_hash1)
    print(ret)
    ret = hashing.verify("123456", password_hash2)
    print(ret)

    # 生成指定长度的随机字符串秘钥
    print(genkey())
