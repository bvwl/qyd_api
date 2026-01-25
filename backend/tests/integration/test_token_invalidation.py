"""
测试API Token失效机制
验证：
1. 生成新Token后，旧Token应该失效（status=2）
2. 旧Token无法通过验证
3. 新Token可以正常使用
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from app.core.settings import get_tortoise_config
from app.models.user import UserInfo, UserToken, Status
from app.crud.user.token import token_crud


async def test_token_invalidation():
    """测试Token失效机制"""
    await Tortoise.init(config=get_tortoise_config())
    
    try:
        # 1. 获取测试用户（使用admin用户）
        user = await UserInfo.filter(email="zhiyu").prefetch_related('roles').first()
        if not user:
            print("❌ 未找到测试用户 zhiyu")
            return
        
        print(f"✅ 找到测试用户: {user.email} (ID: {user.id})")
        
        # 2. 查看当前有效的Token数量
        active_tokens_before = await UserToken.filter(user_id=user.id, status=Status.OK).count()
        print(f"\n📊 当前有效Token数量: {active_tokens_before}")
        
        # 3. 生成第一个Token
        print("\n🔑 生成第一个Token...")
        token1 = await token_crud.generate_token(user.id)
        print(f"✅ Token 1 生成成功: {token1.token[:50]}...")
        
        # 4. 验证第一个Token有效
        active_tokens = await UserToken.filter(user_id=user.id, status=Status.OK).count()
        print(f"📊 有效Token数量: {active_tokens}")
        
        # 5. 生成第二个Token
        print("\n🔑 生成第二个Token...")
        token2 = await token_crud.generate_token(user.id)
        print(f"✅ Token 2 生成成功: {token2.token[:50]}...")
        
        # 6. 验证只有一个Token有效
        active_tokens_after = await UserToken.filter(user_id=user.id, status=Status.OK).count()
        print(f"📊 有效Token数量: {active_tokens_after}")
        
        # 7. 验证旧Token已失效
        token1_record = await UserToken.filter(id=token1.id).first()
        print(f"\n🔍 Token 1 状态: {token1_record.status} (1=有效, 2=失效)")
        
        # 8. 验证新Token有效
        token2_record = await UserToken.filter(id=token2.id).first()
        print(f"🔍 Token 2 状态: {token2_record.status} (1=有效, 2=失效)")
        
        # 9. 尝试使用旧Token验证
        print("\n🧪 测试旧Token验证...")
        old_token_obj = await UserToken.filter(token=token1.token, status=1).first()
        if old_token_obj:
            print("❌ 错误：旧Token仍然有效！")
        else:
            print("✅ 正确：旧Token已失效，无法通过验证")
        
        # 10. 尝试使用新Token验证
        print("\n🧪 测试新Token验证...")
        new_token_obj = await UserToken.filter(token=token2.token, status=1).first()
        if new_token_obj:
            print("✅ 正确：新Token有效，可以通过验证")
        else:
            print("❌ 错误：新Token无效！")
        
        # 11. 显示所有Token状态
        print("\n📋 所有Token状态:")
        all_tokens = await UserToken.filter(user_id=user.id).order_by('-create_time')
        for i, token in enumerate(all_tokens[:5], 1):  # 只显示最近5个
            status_text = "有效" if token.status == Status.OK else "失效"
            print(f"  {i}. {token.token[:50]}... - {status_text} (创建于: {token.create_time})")
        
        print("\n" + "="*80)
        print("✅ 测试完成！")
        print("="*80)
        
        # 总结
        print("\n📝 测试结果总结:")
        if active_tokens_after == 1 and token1_record.status == Status.NOT and token2_record.status == Status.OK:
            print("✅ Token失效机制工作正常！")
            print("   - 生成新Token后，旧Token自动失效")
            print("   - 只有最新的Token保持有效状态")
        else:
            print("❌ Token失效机制存在问题！")
            print(f"   - 有效Token数量: {active_tokens_after} (期望: 1)")
            print(f"   - Token 1 状态: {token1_record.status} (期望: 2)")
            print(f"   - Token 2 状态: {token2_record.status} (期望: 1)")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_token_invalidation())
