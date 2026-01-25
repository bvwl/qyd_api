"""
批量创建钱包API使用示例

展示如何使用批量创建钱包API
"""
import requests
import json


# 配置
BASE_URL = "http://localhost:6080"
ADMIN_EMAIL = "zhiyu"
ADMIN_PASSWORD = "2201101122@qq.com"


def login(email: str, password: str) -> str:
    """登录获取Token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/user/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        raise Exception(f"登录失败: {response.text}")


def batch_create_wallets(token: str, project_name: str, chain: str, count: int, remark: str = None):
    """批量创建钱包"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "project_name": project_name,
        "chain": chain,
        "count": count
    }
    
    if remark:
        data["remark"] = remark
    
    response = requests.post(
        f"{BASE_URL}/api/v1/project/wallet/batch",
        headers=headers,
        json=data
    )
    
    print(f"\n批量创建 {chain.upper()} 钱包")
    print("="*60)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"创建成功: {result['count']} 个钱包")
        print(f"\n前3个钱包:")
        for i, wallet in enumerate(result['items'][:3], 1):
            print(f"\n钱包 {i}:")
            print(f"  ID: {wallet['id']}")
            print(f"  链: {wallet['chain']}")
            print(f"  公钥: {wallet['public_key']}")
            print(f"  私钥(加密): {wallet['private_key'][:50]}...")
        return result['items']
    else:
        print(f"创建失败: {response.text}")
        return []


def get_wallet_detail(token: str, wallet_id: str):
    """获取钱包详情"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/project/wallet/{wallet_id}",
        headers=headers
    )
    
    print(f"\n获取钱包详情")
    print("="*60)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        wallet = response.json()
        print(f"\n钱包ID: {wallet['id']}")
        print(f"链: {wallet['chain']}")
        print(f"公钥: {wallet['public_key']}")
        print(f"私钥: {wallet['private_key'][:50]}...")
        if wallet.get('mnemonic'):
            print(f"助记词: {wallet['mnemonic'][:50]}...")
        return wallet
    else:
        print(f"获取失败: {response.text}")
        return None


def get_wallet_list(token: str, chain: str = None, limit: int = 10):
    """获取钱包列表"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit}
    
    if chain:
        params["chain"] = chain
    
    response = requests.get(
        f"{BASE_URL}/api/v1/project/wallet",
        headers=headers,
        params=params
    )
    
    print(f"\n获取钱包列表")
    print("="*60)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"总数: {result['num']} 个钱包")
        print(f"\n前3个钱包:")
        for i, wallet in enumerate(result['items'][:3], 1):
            print(f"\n钱包 {i}:")
            print(f"  ID: {wallet['id']}")
            print(f"  链: {wallet['chain']}")
            print(f"  公钥: {wallet['public_key']}")
        return result['items']
    else:
        print(f"获取失败: {response.text}")
        return []


def main():
    """主函数"""
    print("="*60)
    print("批量创建钱包API使用示例")
    print("="*60)
    
    # 1. 登录
    print("\n1. 管理员登录...")
    try:
        token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        print(f"登录成功！Token: {token[:50]}...")
    except Exception as e:
        print(f"登录失败: {e}")
        print("\n请确保后端服务已启动: python backend/start.py")
        return
    
    # 2. 批量创建ETH钱包
    print("\n2. 批量创建ETH钱包...")
    eth_wallets = batch_create_wallets(
        token=token,
        project_name="示例项目A",
        chain="eth",
        count=3,
        remark="API示例创建的ETH钱包"
    )
    
    # 3. 批量创建Solana钱包
    print("\n3. 批量创建Solana钱包...")
    sol_wallets = batch_create_wallets(
        token=token,
        project_name="示例项目B",
        chain="solana",
        count=2,
        remark="API示例创建的Solana钱包"
    )
    
    # 4. 获取钱包详情
    if eth_wallets:
        print("\n4. 获取ETH钱包详情...")
        get_wallet_detail(token, eth_wallets[0]['id'])
    
    # 5. 获取钱包列表
    print("\n5. 获取钱包列表...")
    get_wallet_list(token, chain="eth", limit=5)
    
    print("\n" + "="*60)
    print("示例完成！")
    print("="*60)


if __name__ == "__main__":
    main()
