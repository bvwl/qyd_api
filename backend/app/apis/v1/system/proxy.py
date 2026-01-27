from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel, Field

from app.utils.req import Req
from app.apis.deps import get_current_user


app = APIRouter()


class ProxyCheckOut(BaseModel):
    """代理检测输出模型"""
    message: str = Field(..., description="提示信息")
    status: str = Field(..., description="代理状态：success/failed")
    proxy_url: str | None = Field(None, description="代理地址")
    ip: str | None = Field(None, description="检测到的IP地址")
    source: str | None = Field(None, description="检测来源")
    details: dict | None = Field(None, description="详细信息")


@app.get("/check", response_model=ProxyCheckOut, description="检测代理是否可用", summary="代理检测")
async def check_proxy(
    proxy_url: str | None = Query(None, description="代理地址（http://ip:port 或 socks5://ip:port）"),
    current_user: dict = Depends(get_current_user)
):
    """
    检测代理是否可用
    
    功能说明：
    - 依次测试多个网站，任意一个返回 200 即为成功
    - 支持 HTTP 和 SOCKS5 代理
    
    参数说明：
    - proxy_url: 代理地址（可选）
      - HTTP 代理：http://user:pass@ip:port
      - SOCKS5 代理：socks5://user:pass@ip:port
    
    返回说明：
    - status: success（可用）/ failed（不可用）
    - ip: 检测到的 IP 地址
    - source: 检测来源网站
    """
    
    import httpx
    
    # 测试网站列表（按优先级排序）
    test_sites = [
        {"url": "https://api.ipify.org/?format=json", "name": "ipify"},
        {"url": "https://api.myip.com/", "name": "myip"},
        {"url": "https://ifconfig.me/ip", "name": "ifconfig"},
        {"url": "https://icanhazip.com/", "name": "icanhazip"},
    ]
    
    # 构建代理配置
    proxies = None
    if proxy_url:
        proxies = {
            "http://": proxy_url,
            "https://": proxy_url,
        }
    
    # 依次测试每个网站
    for site in test_sites:
        try:
            async with httpx.AsyncClient(proxies=proxies, timeout=10.0, verify=False) as client:
                response = await client.get(site["url"])
                
                if response.status_code == 200:
                    # 解析 IP 地址
                    ip = None
                    try:
                        # 尝试解析 JSON
                        data = response.json()
                        ip = data.get("ip") or data.get("IP") or data.get("query")
                    except:
                        # 纯文本格式
                        ip = response.text.strip()
                    
                    return ProxyCheckOut(
                        message="代理检测成功" if proxy_url else "网络连接正常",
                        status="success",
                        proxy_url=proxy_url,
                        ip=ip,
                        source=site["name"],
                        details={"status_code": response.status_code}
                    )
        except Exception as e:
            # 当前网站失败，继续测试下一个
            continue
    
    # 所有网站都失败
    return ProxyCheckOut(
        message="代理检测失败，所有测试网站均无法访问" if proxy_url else "网络连接失败",
        status="failed",
        proxy_url=proxy_url,
        ip=None,
        source=None,
        details={"error": "所有测试网站均返回非 200 状态码或请求超时"}
    )
