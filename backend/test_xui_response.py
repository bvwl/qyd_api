"""
测试 XuiOperationResponse 响应格式
"""
from app.schemas.xui.user import XuiOperationResponse

# 测试创建响应
try:
    response = XuiOperationResponse(
        success=True,
        message="同步入站配置任务已提交，正在后台执行",
        data={"server_id": "test-id", "task": "sync_inbounds"}
    )
    print("✅ 响应创建成功:")
    print(f"  success: {response.success}")
    print(f"  message: {response.message}")
    print(f"  data: {response.data}")
    print()
    print("✅ 转换为字典:")
    print(response.model_dump())
    print()
    print("✅ 转换为 JSON:")
    print(response.model_dump_json())
except Exception as e:
    print(f"❌ 错误: {e}")
