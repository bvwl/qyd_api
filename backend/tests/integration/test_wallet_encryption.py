"""
测试钱包加密解密功能

不需要启动服务器，直接测试加密解密逻辑
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.tools import aes_encrypt_wallet, aes_decrypt_wallet
from app.clients.wallet import WalletClient
import asyncio


def test_encryption():
    """测试加密解密功能"""
    print("="*60)
    print("测试钱包加密解密功能")
    print("="*60)
    
    # 测试数据
    project_name = "测试项目A"
    test_private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    test_mnemonic = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12"
    
    print(f"\n项目名称: {project_name}")
    print(f"原始私钥: {test_private_key}")
    print(f"原始助记词: {test_mnemonic}")
    
    # 加密
    print("\n" + "-"*60)
    print("1. 加密测试")
    print("-"*60)
    encrypted_private_key = aes_encrypt_wallet(test_private_key, project_name)
    encrypted_mnemonic = aes_encrypt_wallet(test_mnemonic, project_name)
    
    print(f"加密后私钥: {encrypted_private_key}")
    print(f"加密后助记词: {encrypted_mnemonic}")
    
    # 解密
    print("\n" + "-"*60)
    print("2. 解密测试")
    print("-"*60)
    decrypted_private_key = aes_decrypt_wallet(encrypted_private_key, project_name)
    decrypted_mnemonic = aes_decrypt_wallet(encrypted_mnemonic, project_name)
    
    print(f"解密后私钥: {decrypted_private_key}")
    print(f"解密后助记词: {decrypted_mnemonic}")
    
    # 验证
    print("\n" + "-"*60)
    print("3. 验证结果")
    print("-"*60)
    
    if decrypted_private_key == test_private_key:
        print("✓ 私钥加密解密成功")
    else:
        print("✗ 私钥加密解密失败")
        return False
    
    if decrypted_mnemonic == test_mnemonic:
        print("✓ 助记词加密解密成功")
    else:
        print("✗ 助记词加密解密失败")
        return False
    
    # 测试不同项目名称无法解密
    print("\n" + "-"*60)
    print("4. 测试密钥隔离")
    print("-"*60)
    
    try:
        wrong_project = "错误的项目名称"
        aes_decrypt_wallet(encrypted_private_key, wrong_project)
        print("✗ 密钥隔离失败（不应该能解密）")
        return False
    except Exception as e:
        print(f"✓ 密钥隔离成功（使用错误项目名称无法解密）")
    
    return True


async def test_wallet_creation():
    """测试钱包创建功能"""
    print("\n" + "="*60)
    print("测试钱包创建功能")
    print("="*60)
    
    wallet_client = WalletClient()
    
    # 测试ETH钱包创建
    print("\n" + "-"*60)
    print("1. 创建ETH钱包")
    print("-"*60)
    
    eth_private_key, eth_public_key, eth_mnemonic = await wallet_client.eth_create()
    print(f"私钥: {eth_private_key[:50]}...")
    print(f"公钥: {eth_public_key}")
    print(f"助记词: {eth_mnemonic}")
    
    # 测试加密
    project_name = "ETH测试项目"
    encrypted_eth_private = aes_encrypt_wallet(eth_private_key, project_name)
    encrypted_eth_mnemonic = aes_encrypt_wallet(eth_mnemonic, project_name)
    
    print(f"\n加密后私钥: {encrypted_eth_private[:50]}...")
    print(f"加密后助记词: {encrypted_eth_mnemonic[:50]}...")
    
    # 测试解密
    decrypted_eth_private = aes_decrypt_wallet(encrypted_eth_private, project_name)
    decrypted_eth_mnemonic = aes_decrypt_wallet(encrypted_eth_mnemonic, project_name)
    
    if decrypted_eth_private == eth_private_key and decrypted_eth_mnemonic == eth_mnemonic:
        print("\n✓ ETH钱包加密解密成功")
    else:
        print("\n✗ ETH钱包加密解密失败")
        return False
    
    # 测试Solana钱包创建
    print("\n" + "-"*60)
    print("2. 创建Solana钱包")
    print("-"*60)
    
    sol_private_key, sol_public_key, sol_mnemonic = await wallet_client.solana_create()
    print(f"私钥: {sol_private_key}")
    print(f"公钥: {sol_public_key}")
    print(f"助记词: {sol_mnemonic}")
    
    # 测试加密
    project_name = "Solana测试项目"
    encrypted_sol_private = aes_encrypt_wallet(sol_private_key, project_name)
    
    print(f"\n加密后私钥: {encrypted_sol_private[:50]}...")
    
    # 测试解密
    decrypted_sol_private = aes_decrypt_wallet(encrypted_sol_private, project_name)
    
    if decrypted_sol_private == sol_private_key:
        print("\n✓ Solana钱包加密解密成功")
    else:
        print("\n✗ Solana钱包加密解密失败")
        return False
    
    return True


async def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("钱包功能完整测试")
    print("="*60)
    
    # 测试加密解密
    if not test_encryption():
        print("\n✗ 加密解密测试失败")
        return
    
    # 测试钱包创建
    if not await test_wallet_creation():
        print("\n✗ 钱包创建测试失败")
        return
    
    # 测试批量创建模拟
    print("\n" + "="*60)
    print("模拟批量创建钱包")
    print("="*60)
    
    wallet_client = WalletClient()
    project_name = "批量测试项目"
    count = 5
    
    print(f"\n项目名称: {project_name}")
    print(f"创建数量: {count}")
    print(f"链类型: ETH")
    
    wallets = []
    for i in range(count):
        private_key, public_key, mnemonic = await wallet_client.eth_create()
        
        # 加密
        encrypted_private = aes_encrypt_wallet(private_key, project_name)
        encrypted_mnemonic = aes_encrypt_wallet(mnemonic, project_name)
        
        wallets.append({
            'index': i + 1,
            'public_key': public_key,
            'encrypted_private': encrypted_private,
            'encrypted_mnemonic': encrypted_mnemonic,
            'original_private': private_key,
            'original_mnemonic': mnemonic
        })
        
        print(f"\n钱包 {i+1}:")
        print(f"  公钥: {public_key}")
        print(f"  私钥(加密): {encrypted_private[:50]}...")
    
    # 验证解密
    print("\n" + "-"*60)
    print("验证批量解密")
    print("-"*60)
    
    all_success = True
    for wallet in wallets:
        decrypted_private = aes_decrypt_wallet(wallet['encrypted_private'], project_name)
        decrypted_mnemonic = aes_decrypt_wallet(wallet['encrypted_mnemonic'], project_name)
        
        if decrypted_private == wallet['original_private'] and decrypted_mnemonic == wallet['original_mnemonic']:
            print(f"✓ 钱包 {wallet['index']} 解密成功")
        else:
            print(f"✗ 钱包 {wallet['index']} 解密失败")
            all_success = False
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    if all_success:
        print("\n✓ 所有测试通过！")
        print("\n功能验证:")
        print("  ✓ AES加密解密正常")
        print("  ✓ ETH钱包创建正常")
        print("  ✓ Solana钱包创建正常")
        print("  ✓ 批量创建模拟正常")
        print("  ✓ 密钥隔离正常")
        print("\n可以安全使用批量创建钱包功能！")
    else:
        print("\n✗ 部分测试失败")


if __name__ == "__main__":
    asyncio.run(main())
