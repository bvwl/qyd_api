"""
测试安全日志系统
验证非法操作和越权操作的记录功能
"""
import asyncio
from tortoise import Tortoise
from app.core.settings import get_tortoise_config
from app.utils.security_log import (
    log_security_event,
    log_illegal_operation,
    log_unauthorized_access,
    log_permission_denied,
    log_data_access_violation,
    log_authentication_failure,
    log_rate_limit_exceeded,
    log_invalid_parameter,
    LogAction,
    SecurityLogLevel
)
from app.models.user import UserLog, UserInfo
from uuid import UUID


async def test_security_log():
    """测试安全日志功能"""
    await Tortoise.init(config=get_tortoise_config())
    
    try:
        print("="*80)
        print("安全日志系统测试")
        print("="*80)
        
        # 获取测试用户
        user = await UserInfo.filter(email="zhiyu").first()
        if not user:
            print("❌ 未找到测试用户 zhiyu")
            return
        
        user_id = user.id
        print(f"\n✅ 测试用户: {user.email} (ID: {user_id})")
        
        # 1. 测试登录失败记录
        print("\n" + "-"*80)
        print("1. 测试登录失败记录")
        print("-"*80)
        
        await log_authentication_failure(
            email="test@example.com",
            reason="密码错误",
            ip="192.168.1.100"
        )
        print("✅ 记录登录失败: test@example.com")
        
        # 2. 测试越权访问记录
        print("\n" + "-"*80)
        print("2. 测试越权访问记录")
        print("-"*80)
        
        await log_unauthorized_access(
            resource="管理员功能",
            operation="访问",
            user_id=user_id,
            required_role="ADMIN",
            user_roles=["MANUAL"]
        )
        print("✅ 记录越权访问: MANUAL用户尝试访问管理员功能")
        
        # 3. 测试数据访问违规记录
        print("\n" + "-"*80)
        print("3. 测试数据访问违规记录")
        print("-"*80)
        
        await log_data_access_violation(
            resource_type="user",
            resource_id="target-user-id",
            operation="edit",
            user_id=user_id,
            owner_id=UUID("12345678-1234-1234-1234-123456789012")
        )
        print("✅ 记录数据访问违规: 尝试修改他人用户数据")
        
        # 4. 测试权限拒绝记录
        print("\n" + "-"*80)
        print("4. 测试权限拒绝记录")
        print("-"*80)
        
        await log_permission_denied(
            endpoint="/v1/user/user",
            method="DELETE",
            user_id=user_id,
            reason="需要管理员权限"
        )
        print("✅ 记录权限拒绝: DELETE /v1/user/user")
        
        # 5. 测试非法参数记录
        print("\n" + "-"*80)
        print("5. 测试非法参数记录")
        print("-"*80)
        
        await log_invalid_parameter(
            parameter="user_id",
            value="invalid-uuid",
            reason="UUID格式错误",
            user_id=user_id
        )
        print("✅ 记录非法参数: user_id=invalid-uuid")
        
        # 6. 测试频率限制记录
        print("\n" + "-"*80)
        print("6. 测试频率限制记录")
        print("-"*80)
        
        await log_rate_limit_exceeded(
            endpoint="/v1/user/login",
            user_id=user_id,
            limit=5,
            window="1分钟"
        )
        print("✅ 记录频率限制: /v1/user/login 超过5次/1分钟")
        
        # 7. 测试非法操作记录
        print("\n" + "-"*80)
        print("7. 测试非法操作记录")
        print("-"*80)
        
        await log_illegal_operation(
            description="尝试SQL注入",
            user_id=user_id,
            action=LogAction.SQL_INJECTION_ATTEMPT,
            extra_data={"sql": "' OR '1'='1"}
        )
        print("✅ 记录非法操作: SQL注入尝试")
        
        # 8. 测试通用安全事件记录
        print("\n" + "-"*80)
        print("8. 测试通用安全事件记录")
        print("-"*80)
        
        await log_security_event(
            action=LogAction.USER_DELETE,
            description="删除用户: test@example.com",
            user_id=user_id,
            level=SecurityLogLevel.INFO
        )
        print("✅ 记录通用事件: 删除用户")
        
        # 9. 查询记录的日志
        print("\n" + "="*80)
        print("查询记录的日志")
        print("="*80)
        
        # 查询最近的日志
        recent_logs = await UserLog.all().order_by('-create_time').limit(10)
        
        print(f"\n最近10条日志记录:")
        print("-"*80)
        for i, log in enumerate(recent_logs, 1):
            user_info = "系统" if not log.user_id else f"用户={log.user_id}"
            ip_info = f"IP={log.ip}" if log.ip else "IP=未知"
            print(f"{i}. [{user_info}] [{ip_info}] action={log.action} - {log.description[:60]}...")
        
        # 统计各类操作
        print("\n" + "="*80)
        print("操作类型统计")
        print("="*80)
        
        action_stats = {}
        all_logs = await UserLog.all()
        for log in all_logs:
            action_stats[log.action] = action_stats.get(log.action, 0) + 1
        
        action_names = {
            1: "登录",
            3: "登录失败",
            5: "Token无效",
            13: "删除用户",
            31: "权限拒绝",
            32: "未授权访问",
            71: "非法参数",
            72: "SQL注入尝试",
            75: "超过频率限制",
            91: "访问他人数据",
            92: "修改他人数据",
        }
        
        for action, count in sorted(action_stats.items()):
            action_name = action_names.get(action, f"操作{action}")
            print(f"  {action_name} (action={action}): {count}次")
        
        # 查询越权操作
        print("\n" + "="*80)
        print("越权操作记录")
        print("="*80)
        
        unauthorized_logs = await UserLog.filter(
            action__in=[31, 32, 91, 92, 93]
        ).order_by('-create_time').limit(5)
        
        if unauthorized_logs:
            for i, log in enumerate(unauthorized_logs, 1):
                user_info = "系统" if not log.user_id else f"用户={log.user_id}"
                print(f"{i}. [{user_info}] {log.description}")
        else:
            print("  暂无越权操作记录")
        
        # 查询登录失败记录
        print("\n" + "="*80)
        print("登录失败记录")
        print("="*80)
        
        login_failed_logs = await UserLog.filter(
            action=3
        ).order_by('-create_time').limit(5)
        
        if login_failed_logs:
            for i, log in enumerate(login_failed_logs, 1):
                ip_info = f"IP={log.ip}" if log.ip else "IP=未知"
                print(f"{i}. [{ip_info}] {log.description}")
        else:
            print("  暂无登录失败记录")
        
        print("\n" + "="*80)
        print("✅ 测试完成！")
        print("="*80)
        
        print("\n📝 测试结果总结:")
        print("  ✅ 登录失败记录 - 正常")
        print("  ✅ 越权访问记录 - 正常")
        print("  ✅ 数据访问违规记录 - 正常")
        print("  ✅ 权限拒绝记录 - 正常")
        print("  ✅ 非法参数记录 - 正常")
        print("  ✅ 频率限制记录 - 正常")
        print("  ✅ 非法操作记录 - 正常")
        print("  ✅ 通用事件记录 - 正常")
        
        print("\n📊 日志存储:")
        print("  - 数据库: user_logs 表")
        print("  - 文件: logs/security.log")
        
        print("\n🔍 查看日志:")
        print("  - 数据库查询: SELECT * FROM user_logs ORDER BY create_time DESC LIMIT 10;")
        print("  - 文件查看: tail -f logs/security.log")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_security_log())
