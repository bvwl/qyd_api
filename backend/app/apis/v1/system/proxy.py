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
    proxy_url: str | None = Query(None, description="代理地址（http://ip:port 或 socks5h://ip:port）"),
    current_user: dict = Depends(get_current_user)
):
    """
    检测代理是否可用
    
    功能说明：
    - 依次访问 3 个 IP 检测网站
    - 如果任一网站返回 200，则认为代理可用
    - 如果 3 个网站都访问失败，则认为代理不可用
    - 不提供代理地址时，检测本机网络
    
    检测网站列表：
    1. https://api.ipify.org/ - 返回纯文本 IP
    2. https://api.myip.com/ - 返回 JSON 格式
    3. https://iprust.io/ip.json - 返回 JSON 格式
    
    参数说明：
    - proxy_url: 代理地址（可选）
      - HTTP 代理：http://ip:port 或 http://user:pass@ip:port
      - SOCKS5 代理：socks5h://ip:port 或 socks5h://user:pass@ip:port
    
    返回说明：
    - status: success（可用）/ failed（不可用）
    - ip: 检测到的 IP 地址
    - source: 检测来源网站
    - details: 详细信息（包含响应内容）
    """
    
    # 检测网站列表
    check_urls = [
        {
            "url": "https://api.ipify.org/",
            "name": "ipify",
            "type": "text"
        },
        {
            "url": "https://api.myip.com/",
            "name": "myip",
            "type": "json"
        },
        {
            "url": "https://iprust.io/ip.json",
            "name": "iprust",
            "type": "json"
        }
    ]
    
    # 依次检测
    for check_site in check_urls:
        try:
            # 使用 _req2 方法进行异步请求
            result = await Req._req2(
                method="GET",
                url=check_site["url"],
                proxy_url=proxy_url,
                ran_env="chrome124"
            )
            
            # 检查状态码
            if result["code"] == 200:
                content = result["content"]
                
                # 解析 IP 地址
                ip = None
                details = {}
                
                if check_site["type"] == "text":
                    # 纯文本格式，直接就是 IP
                    ip = content.strip() if isinstance(content, str) else None
                    details = {"raw": content}
                elif check_site["type"] == "json":
                    # JSON 格式，提取 IP
                    if isinstance(content, dict):
                        ip = content.get("ip") or content.get("IP") or content.get("query")
                        details = content
                    else:
                        details = {"raw": content}
                
                # 返回成功结果
                return ProxyCheckOut(
                    message="代理检测成功" if proxy_url else "网络连接正常",
                    status="success",
                    proxy_url=proxy_url,
                    ip=ip,
                    source=check_site["name"],
                    details=details
                )
                
        except Exception as e:
            # 当前网站检测失败，继续下一个
            continue
    
    # 所有网站都检测失败
    return ProxyCheckOut(
        message="代理检测失败，所有检测网站均无法访问" if proxy_url else "网络连接失败，所有检测网站均无法访问",
        status="failed",
        proxy_url=proxy_url,
        ip=None,
        source=None,
        details={"error": "所有检测网站均返回非 200 状态码或请求超时"}
    )
