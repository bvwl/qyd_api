"""
检查数据库中的密码是否已加密
"""
import asyncio
import sys
sys.path.insert(0, '/Users/qingliang/code/python/company/api/qyd_api2/backend')

from app.models.project import ProjectAccount
from app.core.database import init_db
from app.utils.project_crypto import decrypt_password


async def check_password():
    # 初始化数据库
    await init_db()
    
    # 查询账号
    account_email = "hsm48786@kisoq.com"
    account = await ProjectAccount.get_or_none(account=account_email)
    
    if not account:
        print(f"❌ 未找到账号: {account_email}")
        return
    
    print(f"✅ 找到账号: {account_email}")
    print(f"账号ID: {account.id}")
    print(f"项目ID: {account.project_id}")
    print(f"数据库中的password字段: {account.password}")
    
    # 尝试解密
    if account.password:
        try:
            decrypted = decrypt_password(account.password, account.account)
            print(f"\n解密后的密码: {decrypted}")
            
            # 检查是否是明文
            if account.password == "Zpaily88":
                print("\n❌ 密码未加密！存储的是明文密码")
            else:
                print("\n✅ 密码已加密")
        except Exception as e:
            print(f"\n解密失败: {e}")
            print("可能是明文密码或加密方式不匹配")
    else:
        print("\n⚠️  password字段为空")


if __name__ == '__main__':
    asyncio.run(check_password())
