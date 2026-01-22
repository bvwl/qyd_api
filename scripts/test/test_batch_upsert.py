#!/usr/bin/env python3
"""
测试项目账号批量upsert接口
"""
import requests
import json
import time
from uuid import uuid4

# 配置
BASE_URL = "http://127.0.0.1:6080"
LOGIN_URL = f"{BASE_URL}/v1/user/auth/login"
BATCH_UPSERT_URL = f"{BASE_URL}/v1/project/account/batch-upsert"
LIST_URL = f"{BASE_URL}/v1/project/account"

# 登录信息
LOGIN_DATA = {
    "email": "zhiyu",
    "password": "2201101122@qq.com"
}

def login():
    """登录获取token"""
    print("正在登录...")
    response = requests.post(LOGIN_URL, json=LOGIN_DATA)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        if token:
            print(f"✅ 登录成功，token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: 未获取到token")
            print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return None
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def test_batch_upsert(token, count=10):
    """测试批量upsert"""
    print(f"\n正在测试批量upsert {count} 条数据...")
    
    # 生成测试数据
    test_data = []
    project_id = str(uuid4())  # 使用同一个项目ID
    
    for i in range(count):
        test_data.append({
            "account": f"test_account_{i}_{int(time.time())}",
            "project_id": project_id,
            "password": f"password_{i}",
            "status": 1,
            "account_type": 1,
            "balance": 0,  # 添加balance字段
            "variable": 0  # 添加variable字段
        })
    
    # 发送请求
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    response = requests.post(BATCH_UPSERT_URL, json=test_data, headers=headers)
    end_time = time.time()
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 批量upsert成功")
        print(f"   响应时间: {end_time - start_time:.2f}秒")
        print(f"   响应消息: {data.get('message')}")
        print(f"   成功数量: {data.get('count')}")
        return True
    else:
        print(f"❌ 批量upsert失败: {response.text}")
        return False

def check_queue_processing(token, wait_seconds=5):
    """等待队列处理并检查结果"""
    print(f"\n等待 {wait_seconds} 秒让队列处理数据...")
    time.sleep(wait_seconds)
    
    print("检查数据是否已处理...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(LIST_URL, headers=headers, params={"limit": 20})
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("data", {}).get("items", [])
        print(f"✅ 查询成功，当前有 {len(items)} 条数据")
        
        # 显示最新的几条数据
        if items:
            print("\n最新的数据:")
            for i, item in enumerate(items[:5], 1):
                print(f"   {i}. 账号: {item.get('account')}, 项目ID: {item.get('project_id')}")
        return True
    else:
        print(f"❌ 查询失败: {response.text}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("项目账号批量upsert测试")
    print("=" * 60)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 测试小批量（10条）
    print("\n" + "=" * 60)
    print("测试1: 小批量（10条数据）")
    print("=" * 60)
    if test_batch_upsert(token, count=10):
        check_queue_processing(token, wait_seconds=3)
    
    # 3. 测试中批量（100条）
    print("\n" + "=" * 60)
    print("测试2: 中批量（100条数据）")
    print("=" * 60)
    if test_batch_upsert(token, count=100):
        check_queue_processing(token, wait_seconds=5)
    
    # 4. 测试大批量（500条）
    print("\n" + "=" * 60)
    print("测试3: 大批量（500条数据）")
    print("=" * 60)
    if test_batch_upsert(token, count=500):
        check_queue_processing(token, wait_seconds=10)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("1. 查看后端日志: tail -f backend/logs/app.log | grep Worker")
    print("2. 查看Redis队列: redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ")
    print("   - 查看队列大小: ZCARD qyd:project_account_keys_zset")
    print("   - 查看队列内容: ZRANGE qyd:project_account_keys_zset 0 10")

if __name__ == "__main__":
    main()
