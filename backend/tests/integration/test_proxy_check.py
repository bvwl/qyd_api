"""
测试代理检测 API
"""
import asyncio
import requests


def test_proxy_check_no_proxy():
    """测试不使用代理的情况"""
    print("=" * 60)
    print("测试 1: 检测本机网络（不使用代理）")
    print("=" * 60)
    
    url = "http://127.0.0.1:6080/v1/system/proxy/check"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"
    }
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"消息: {result['message']}")
        print(f"状态: {result['status']}")
        print(f"IP: {result['ip']}")
        print(f"来源: {result['source']}")
        print(f"详情: {result['details']}")
        print()
        
        if result['status'] == 'success':
            print("✅ 测试通过：本机网络正常")
        else:
            print("❌ 测试失败：本机网络异常")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()


def test_proxy_check_with_http_proxy():
    """测试使用 HTTP 代理的情况"""
    print("=" * 60)
    print("测试 2: 检测 HTTP 代理")
    print("=" * 60)
    
    url = "http://127.0.0.1:6080/v1/system/proxy/check"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"
    }
    
    # 示例代理地址（需要替换为实际可用的代理）
    proxy_url = "http://127.0.0.1:7890"
    
    try:
        response = requests.get(url, headers=headers, params={"proxy_url": proxy_url})
        result = response.json()
        
        print(f"代理地址: {proxy_url}")
        print(f"状态码: {response.status_code}")
        print(f"消息: {result['message']}")
        print(f"状态: {result['status']}")
        print(f"IP: {result['ip']}")
        print(f"来源: {result['source']}")
        print(f"详情: {result['details']}")
        print()
        
        if result['status'] == 'success':
            print("✅ 测试通过：代理可用")
        else:
            print("⚠️  代理不可用（可能是代理地址错误或代理服务未启动）")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()


def test_proxy_check_with_socks5_proxy():
    """测试使用 SOCKS5 代理的情况"""
    print("=" * 60)
    print("测试 3: 检测 SOCKS5 代理")
    print("=" * 60)
    
    url = "http://127.0.0.1:6080/v1/system/proxy/check"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"
    }
    
    # 示例代理地址（需要替换为实际可用的代理）
    proxy_url = "socks5h://127.0.0.1:1080"
    
    try:
        response = requests.get(url, headers=headers, params={"proxy_url": proxy_url})
        result = response.json()
        
        print(f"代理地址: {proxy_url}")
        print(f"状态码: {response.status_code}")
        print(f"消息: {result['message']}")
        print(f"状态: {result['status']}")
        print(f"IP: {result['ip']}")
        print(f"来源: {result['source']}")
        print(f"详情: {result['details']}")
        print()
        
        if result['status'] == 'success':
            print("✅ 测试通过：代理可用")
        else:
            print("⚠️  代理不可用（可能是代理地址错误或代理服务未启动）")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()


def test_proxy_check_with_invalid_proxy():
    """测试使用无效代理的情况"""
    print("=" * 60)
    print("测试 4: 检测无效代理")
    print("=" * 60)
    
    url = "http://127.0.0.1:6080/v1/system/proxy/check"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0MTk0MzMsImlhdCI6MTc2OTMzMzAzMywianRpIjoiMGI1ODc2NzYtMDFmYy00NmI3LTljYWUtYjBlMzI3NTdiNTA4IiwiaWQiOiI3OTE0Y2JhYy04ZmY5LTRiMTAtOTg1NC04MGZjMTY2N2EzMzkiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.pTJtPSFEiCUm6Sa1lTUJS6d6WNcq6R5gmat8XxjNvpQ"
    }
    
    # 无效的代理地址
    proxy_url = "http://192.168.1.1:9999"
    
    try:
        response = requests.get(url, headers=headers, params={"proxy_url": proxy_url})
        result = response.json()
        
        print(f"代理地址: {proxy_url}")
        print(f"状态码: {response.status_code}")
        print(f"消息: {result['message']}")
        print(f"状态: {result['status']}")
        print(f"IP: {result['ip']}")
        print(f"来源: {result['source']}")
        print(f"详情: {result['details']}")
        print()
        
        if result['status'] == 'failed':
            print("✅ 测试通过：正确识别无效代理")
        else:
            print("❌ 测试失败：未能识别无效代理")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("代理检测 API 测试")
    print("=" * 60 + "\n")
    
    # 测试 1: 不使用代理
    test_proxy_check_no_proxy()
    
    # 测试 2: 使用 HTTP 代理
    test_proxy_check_with_http_proxy()
    
    # 测试 3: 使用 SOCKS5 代理
    test_proxy_check_with_socks5_proxy()
    
    # 测试 4: 使用无效代理
    test_proxy_check_with_invalid_proxy()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
