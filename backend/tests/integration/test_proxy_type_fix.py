#!/usr/bin/env python3
"""
测试代理类型自动识别功能

验证：
1. HTTP端口（22000-28999）生成 http:// URL
2. SOCKS5端口（32000-38999）生成 socks5:// URL
3. proxy_type 字段正确返回
"""

import requests
import json

# API配置
BASE_URL = "http://127.0.0.1:6080"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_proxy_type():
    """测试代理类型识别"""
    print("=" * 60)
    print("测试代理类型自动识别功能")
    print("=" * 60)
    
    # 获取服务器列表
    response = requests.get(
        f"{BASE_URL}/v1/server/info",
        headers=headers,
        params={"page": 1, "limit": 20, "res_count": True}
    )
    
    if response.status_code != 200:
        print(f"❌ API请求失败: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    items = data.get("items", [])
    
    if not items:
        print("❌ 没有找到服务器数据")
        return
    
    print(f"\n找到 {len(items)} 个服务器\n")
    
    # 测试结果统计
    http_count = 0
    socks5_count = 0
    errors = []
    
    for item in items:
        port = item.get("port")
        proxy_url = item.get("proxy_url", "")
        proxy_type = item.get("proxy_type", "")
        
        if not port:
            continue
        
        # 判断预期的代理类型
        if 21999 < port < 29999:
            expected_type = "http"
            expected_protocol = "http://"
        elif 31999 < port < 39999:
            expected_type = "socks5"
            expected_protocol = "socks5://"
        else:
            expected_type = "socks5"
            expected_protocol = "socks5://"
        
        # 验证 proxy_type
        if proxy_type != expected_type:
            errors.append(f"端口 {port}: proxy_type 错误 (期望: {expected_type}, 实际: {proxy_type})")
            continue
        
        # 验证 proxy_url 协议
        if not proxy_url.startswith(expected_protocol):
            errors.append(f"端口 {port}: proxy_url 协议错误 (期望: {expected_protocol}, 实际: {proxy_url[:10]}...)")
            continue
        
        # 统计
        if proxy_type == "http":
            http_count += 1
            print(f"✅ HTTP  端口 {port:5d}: {proxy_url[:50]}...")
        else:
            socks5_count += 1
            print(f"✅ SOCKS5 端口 {port:5d}: {proxy_url[:50]}...")
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"HTTP 代理数量:   {http_count}")
    print(f"SOCKS5 代理数量: {socks5_count}")
    print(f"错误数量:        {len(errors)}")
    
    if errors:
        print("\n错误详情:")
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("\n🎉 所有测试通过！")
    
    print("=" * 60)

if __name__ == "__main__":
    test_proxy_type()
