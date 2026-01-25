"""
测试 balance 自动计算功能
"""
import asyncio
import httpx
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://127.0.0.1:6080"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjkyMjAyNDYsImlhdCI6MTc2OTEzMzg0NiwianRpIjoiMGNiNGEzNjQtYTQwZC00ZmU2LTllZGMtM2IzYjA3MWNhZmJjIiwiaWQiOiI3MjMzMTY1Yy1jYmFlLTRlNjctOTU3My00NWRmNmVmMzIyZWMiLCJlbWFpbCI6IjIyMDExMDExMjJAcXEuY29tIiwicm9sZXMiOlsiTUFOVUFMIiwiSVQiXX0.CVADuZ070pO0t-7sqdr0wWRh9b1Dmx5jxtDGz3QZ6Wc"
PROJECT_ID = "2052f094-800c-41b1-a750-996280b38281"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


async def test_balance_calculation():
    """测试 balance 自动计算功能"""
    async with httpx.AsyncClient() as client:
        test_account = f"balance_test_{datetime.now().strftime('%H%M%S')}"
        
        print("=" * 80)
        print("测试 Balance 自动计算功能")
        print("=" * 80)
        
        # 测试1: 首次创建（传入 balance）
        print("\n【测试1】首次创建，传入 balance=100")
        print("-" * 80)
        
        data1 = {
            "account": test_account,
            "balance": 100,
            "project_id": PROJECT_ID,
            "status": 1,
            "account_type": 1
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/project/account/upsert",
            json=data1,
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 等待队列处理
        print("\n等待队列处理（5秒）...")
        await asyncio.sleep(5)
        
        # 查询结果
        response = await client.get(
            f"{BASE_URL}/v1/project/account",
            params={"account": test_account, "project_id": PROJECT_ID},
            headers=headers
        )
        result = response.json()
        if result['items']:
            item = result['items'][0]
            print(f"\n查询结果:")
            print(f"  账号: {item['account']}")
            print(f"  余额: {item['balance']}")
            print(f"  变动: {item['variable']}")
            print(f"  历史: {item['balance_history']}")
            print(f"\n✅ 预期: balance=100, variable=100 (首次创建，从0增加到100), balance_history 有1条记录")
            print(f"✅ 实际: balance={item['balance']}, variable={item['variable']}, "
                  f"balance_history 有 {len(item['balance_history'] or {})} 条记录")
        
        # 测试2: 第二天更新（传入 balance=150）
        print("\n" + "=" * 80)
        print("【测试2】第二天更新，传入 balance=150")
        print("-" * 80)
        
        data2 = {
            "account": test_account,
            "balance": 150,
            "project_id": PROJECT_ID
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/project/account/upsert",
            json=data2,
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 等待队列处理
        print("\n等待队列处理（5秒）...")
        await asyncio.sleep(5)
        
        # 查询结果
        response = await client.get(
            f"{BASE_URL}/v1/project/account",
            params={"account": test_account, "project_id": PROJECT_ID},
            headers=headers
        )
        result = response.json()
        if result['items']:
            item = result['items'][0]
            print(f"\n查询结果:")
            print(f"  账号: {item['account']}")
            print(f"  余额: {item['balance']}")
            print(f"  变动: {item['variable']}")
            print(f"  历史: {item['balance_history']}")
            print(f"\n✅ 预期: balance=150, variable=50 (150-100), balance_history 有1条记录（同一天覆盖）")
            print(f"✅ 实际: balance={item['balance']}, variable={item['variable']}, "
                  f"balance_history 有 {len(item['balance_history'] or {})} 条记录")
        
        # 测试3: 不传 balance，只更新其他字段
        print("\n" + "=" * 80)
        print("【测试3】不传 balance，只更新 status")
        print("-" * 80)
        
        data3 = {
            "account": test_account,
            "status": 2,  # 改为异常状态
            "project_id": PROJECT_ID
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/project/account/upsert",
            json=data3,
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 等待队列处理
        print("\n等待队列处理（5秒）...")
        await asyncio.sleep(5)
        
        # 查询结果
        response = await client.get(
            f"{BASE_URL}/v1/project/account",
            params={"account": test_account, "project_id": PROJECT_ID},
            headers=headers
        )
        result = response.json()
        if result['items']:
            item = result['items'][0]
            print(f"\n查询结果:")
            print(f"  账号: {item['account']}")
            print(f"  状态: {item['status']}")
            print(f"  余额: {item['balance']}")
            print(f"  变动: {item['variable']}")
            print(f"  历史: {item['balance_history']}")
            print(f"\n✅ 预期: status=2, balance/variable/balance_history 保持不变")
            print(f"✅ 实际: status={item['status']}, balance={item['balance']}, "
                  f"variable={item['variable']}")
        
        # 测试4: 传入 variable 和 balance_history（应该被忽略）
        print("\n" + "=" * 80)
        print("【测试4】传入 balance=200，同时传入 variable=999 和 balance_history（应该被忽略）")
        print("-" * 80)
        
        data4 = {
            "account": test_account,
            "balance": 200,
            "variable": 999,  # 应该被忽略
            "balance_history": {"2020-01-01": 999},  # 应该被忽略
            "project_id": PROJECT_ID
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/project/account/upsert",
            json=data4,
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 等待队列处理
        print("\n等待队列处理（5秒）...")
        await asyncio.sleep(5)
        
        # 查询结果
        response = await client.get(
            f"{BASE_URL}/v1/project/account",
            params={"account": test_account, "project_id": PROJECT_ID},
            headers=headers
        )
        result = response.json()
        if result['items']:
            item = result['items'][0]
            print(f"\n查询结果:")
            print(f"  账号: {item['account']}")
            print(f"  余额: {item['balance']}")
            print(f"  变动: {item['variable']}")
            print(f"  历史: {item['balance_history']}")
            print(f"\n✅ 预期: balance=200, variable=50 (200-150，自动计算), "
                  f"balance_history 不包含 2020-01-01")
            print(f"✅ 实际: balance={item['balance']}, variable={item['variable']}")
            if item['balance_history'] and "2020-01-01" in item['balance_history']:
                print(f"❌ 错误: balance_history 包含了不应该存在的 2020-01-01")
            else:
                print(f"✅ 正确: balance_history 不包含 2020-01-01")
        
        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_balance_calculation())
