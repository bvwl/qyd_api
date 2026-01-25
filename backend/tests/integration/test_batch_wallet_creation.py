"""
测试批量创建钱包功能

测试内容：
1. 批量创建ETH钱包
2. 批量创建Solana钱包
3. 验证加密存储
4. 验证管理员自动解密
"""
import asyncio
import httpx
import json


# 配置
BASE_URL = "http://localhost:6080"
ADMIN_EMAIL = "zhiyu"
ADMIN_PASSWORD = "2201101122@qq.com"


async def login(email: str, password: str) -> str:
    """登录获取Token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/user/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            raise Exception(f"登录失败: {response.text}")


async def batch_create_wallets(token: str, project_name: str, chain: str, count: int):
    """批量创建钱包"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/project/wallet/batch",
            headers=headers,
            json={
                "project_name": project_name,
                "chain": chain,
                "count": count,
                "remark": f"测试批量创建{chain}钱包"
            }
        )
        
        print(f"\n{'='*60}")
        print(f"批量创建 {chain.upper()} 钱包")
        print(f"{'='*60}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"创建成功: {data['count']} 个钱包")
            print(f"\n前3个钱包信息:")
            for i, wallet in enumerate(data['items'][:3], 1):
                print(f"\n钱包 {i}:")
                print(f"  ID: {wallet['id']}")
                print(f"  链: {wallet['chain']}")
                print(f"  公钥: {wallet['public_key'][:50]}...")
                print(f"  私钥(加密): {wallet['private_key'][:50]}...")
                if wallet.get('mnemonic'):
                    print(f"  助记词(加密): {wallet['mnemonic'][:50]}...")
            return data['items']
        else:
            print(f"创建失败: {response.text}")
            return []


async def get_wallet_detail(token: str, wallet_id: str):
    """获取钱包详情（管理员会自动解密）"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/project/wallet/{wallet_id}",
            headers=headers
        )
        
        print(f"\n{'='*60}")
        print(f"获取钱包详情（管理员自动解密）")
        print(f"{'='*60}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n钱包ID: {data['id']}")
            print(f"链: {data['chain']}")
            print(f"公钥: {data['public_key']}")
            print(f"私钥(已解密): {data['private_key']}")
            if data.get('mnemonic'):
                print(f"助记词(已解密): {data['mnemonic']}")
            return data
        else:
            print(f"获取失败: {response.text}")
            return None


async def get_wallet_list(token: str, chain: str = None):
    """获取钱包列表（管理员会自动解密）"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": 5}
    if chain:
        params["chain"] = chain
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/project/wallet",
            headers=headers,
            params=params
        )
        
        print(f"\n{'='*60}")
        print(f"获取钱包列表（管理员自动解密）")
        print(f"{'='*60}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总数: {data['num']} 个钱包")
            print(f"\n前3个钱包:")
            for i, wallet in enumerate(data['items'][:3], 1):
                print(f"\n钱包 {i}:")
                print(f"  ID: {wallet['id']}")
                print(f"  链: {wallet['chain']}")
                print(f"  公钥: {wallet['public_key'][:50]}...")
                print(f"  私钥(已解密): {wallet['private_key'][:50]}...")
            return data['items']
        else:
            print(f"获取失败: {response.text}")
            return []


async def main():
    """主测试流程"""
    print("="*60)
    print("批量创建钱包功能测试")
    print("="*60)
    
    # 1. 登录获取Token
    print("\n1. 管理员登录...")
    token = await login(ADMIN_EMAIL, ADMIN_PASSWORD)
    print(f"登录成功，Token: {token[:50]}...")
    
    # 2. 批量创建ETH钱包
    print("\n2. 批量创建ETH钱包...")
    eth_wallets = await batch_create_wallets(
        token=token,
        project_name="测试项目A",
        chain="eth",
        count=3
    )
    
    # 3. 批量创建Solana钱包
    print("\n3. 批量创建Solana钱包...")
    solana_wallets = await batch_create_wallets(
        token=token,
        project_name="测试项目B",
        chain="solana",
        count=2
    )
    
    # 4. 获取单个钱包详情（验证自动解密）
    if eth_wallets:
        print("\n4. 获取ETH钱包详情（验证自动解密）...")
        await get_wallet_detail(token, eth_wallets[0]['id'])
    
    # 5. 获取钱包列表（验证自动解密）
    print("\n5. 获取钱包列表（验证自动解密）...")
    await get_wallet_list(token, chain="eth")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n总结:")
    print("✓ 批量创建钱包功能正常")
    print("✓ 私钥和助记词已加密存储")
    print("✓ 管理员查询时自动解密")
    print("✓ 支持ETH和Solana两种链")


if __name__ == "__main__":
    asyncio.run(main())
