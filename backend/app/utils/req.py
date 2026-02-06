import base64
import random

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
import requests
from curl_cffi.requests import AsyncSession, request, exceptions
import urllib3

# 屏蔽 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENV_LIST = ["edge99", "edge101", "chrome99", "chrome100", "chrome101", "chrome104", "chrome107", "chrome110",
            "chrome116", "chrome119", "chrome120", "chrome123", "chrome124", "safari15_3", "safari15_5", "safari17_0"]


# 网络请求模块
class Req:

    def __init__(self):
        self.session = None
        self.async_session = None
        pass

    # 同步网络请求
    @staticmethod
    def req(method: str, url: str, headers: dict = None, cookies: dict = None,
            proxy_url: str = None, **kwargs) -> dict:
        """
        同步网络请求
        :param proxy_url: http/socks5h代理
        :param method: 请求方法 GET POST PUT DELETE
        :param url: 请求地址
        :param headers:  请求头
        :param cookies:  cookies
        :param kwargs:  其他参数 如 data=data json=data verify=False 等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        proxies = None if proxy_url is None else {'http': f'{proxy_url}', 'https': f'{proxy_url}'}
        try:
            response = requests.request(method, url, headers=headers, cookies=cookies, proxies=proxies, timeout=30,
                                        verify=False, **kwargs)
            content_type = response.headers.get('Content-Type', '').lower()
            # 根据 Content-Type 判断并处理数据
            if "application/json" in content_type:
                # 处理 JSON 格式
                content = response.json()
            elif "text/" in content_type:
                # 处理文本格式
                content = response.text
            elif 'image/' in content_type:
                # 处理图片格式
                content = base64.b64encode(response.content).decode('utf-8')
            elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                # 处理二进制数据
                content = response.content  # 返回字节流
            else:
                # 默认处理方式
                content = response.text
            status_code = response.status_code
            cookies = response.cookies.get_dict()
            headers = dict(response.headers)
        except requests.exceptions.Timeout:
            status_code = 408  # 请求超时
            content = "Request Timeout"
        except Exception as e:
            status_code = 500  # 网络错误
            content = str(e)
        return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}

    # 同步网络请求2
    @staticmethod
    def req2(method: str, url: str, headers: dict = None, cookies: dict = None, ran_env: str | None = 'chrome124',
             proxy_url: str = None, **kwargs) -> dict:
        """
        同步网络请求2
        :param method: 请求方法(GET/POST/PUT/DELETE)
        :param url: 请求地址
        :param ran_env: 随机请求环境 None为随机请求环境 默认为chrome124(具体环境进入代码查看)
        :param headers:  请求头(字典类型)
        :param cookies:  cookies(字典类型)
        :param proxy_url: http/socks5h代理
        :param kwargs:  其他参数 如 data=data json=data等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        proxies = None if proxy_url is None else {'http': f'{proxy_url}', 'https': f'{proxy_url}'}
        impersonate = random.choice(ENV_LIST) if ran_env is None else ran_env

        try:
            if method == 'GET':
                response = request('GET', url, headers=headers, cookies=cookies, proxies=proxies,
                                   impersonate=impersonate, timeout=30, verify=False, **kwargs)
            elif method == 'POST':
                response = request('POST', url, headers=headers, cookies=cookies, proxies=proxies,
                                   impersonate=impersonate, timeout=30, verify=False, **kwargs)
            elif method == 'PUT':
                response = request('PUT', url, headers=headers, cookies=cookies, proxies=proxies,
                                   impersonate=impersonate, timeout=30, verify=False, **kwargs)
            elif method == 'DELETE':
                response = request('DELETE', url, headers=headers, cookies=cookies, proxies=proxies,
                                   impersonate=impersonate, timeout=30, verify=False, **kwargs)
            else:
                return {"code": 500, "content": "请求方法错误", "cookies": None, "headers": None}

            cookies = {}
            headers = {}
            # 根据 响应头 返回不同类型的内容
            content_type = response.headers.get('Content-Type', '').lower()

            if "application/json" in content_type:
                # 处理 JSON 格式
                content = response.json()
            elif "text/" in content_type:
                # 处理文本格式
                content = response.text
            elif 'image/' in content_type:
                # 处理图片格式
                content = base64.b64encode(response.content).decode('utf-8')
            elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                # 处理二进制数据
                content = response.content
            else:
                # 默认处理方式
                content = response.text
            status_code = response.status_code
            cookies = {key: value for key, value in response.cookies.items()}
            headers = dict(response.headers)
        except Exception as e:
            # 处理超时异常
            if 'timeout' in str(e).lower() or 'timed out' in str(e).lower():
                status_code = 408  # 请求超时
                content = "Request Timeout"
            else:
                status_code = 500  # 网络错误
                content = f'{e}'
        return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}

    def ses_create(self, headers: dict = None, cookies: dict = None, proxy_url: str = None):
        """
        创建同步session
        :param proxy_url: http/socks5h代理
        :param headers: 请求头 (可选)
        :param cookies: cookies (可选)
        :return: session会话
        """
        if self.session:
            self.ses_close()
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)
        if proxy_url:
            proxies = {'http': f'{proxy_url}', 'https': f'{proxy_url}'}
            self.session.proxies.update(proxies)
        return self.session

    def ses_close(self):
        """
        关闭同步session
        :return:
        """
        if self.session:
            self.session.close()

    # 同步网络请求3
    @staticmethod
    def req3(session, method: str, url: str, **kwargs) -> dict:
        """
        同步网络请求3
        :param session: 同步session
        :param method: 请求方法(GET/POST/PUT/DELETE)
        :param url: 请求地址
        :param kwargs:  其他参数 如 data=data json=data等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        cookies = {}
        headers = {}
        try:
            response = session.request(method=method, url=url, timeout=30, verify=False, **kwargs)
            # 根据 响应头 返回不同类型的内容
            content_type = response.headers.get('Content-Type', '').lower()
            # 根据 Content-Type 判断并处理数据
            if "application/json" in content_type:
                # 处理 JSON 格式
                content = response.json()
            elif "text/" in content_type:
                # 处理文本格式
                content = response.text
            elif 'image/' in content_type:
                # 处理图片格式
                content = base64.b64encode(response.content).decode('utf-8')
            elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                # 处理二进制数据
                content = response.content  # 返回字节流
            else:
                # 默认处理方式
                content = response.text
            status_code = response.status_code
            cookies = {key: value for key, value in response.cookies.items()}
            headers = dict(response.headers)
        except requests.exceptions.Timeout:
            status_code = 408  # 请求超时
            content = "Request Timeout"
        except Exception as e:
            status_code = 500  # 网络错误
            content = str(e)
        return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}

    # 异步网络请求
    @staticmethod
    async def _req(method: str, url: str, headers: dict = None, cookies: dict = None,
                   proxy_url: str = None, **kwargs) -> dict:
        """
        异步网络请求
        :param method: 请求方法 GET POST PUT DELETE
        :param url: 请求地址
        :param headers:  请求头
        :param cookies:  cookies
        :param proxy_url:  http/socks5h代理
        :param kwargs:  其他参数 如 data=data json=data ssl=False 等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        connector = None if proxy_url is None else ProxyConnector.from_url(proxy_url)
        try:
            # 使用 aiohttp 的 ClientSession 并指定连接器
            async with ClientSession(headers=headers, cookies=cookies, connector=connector) as session:
                async with session.request(method, url, timeout=30, ssl=False, **kwargs) as response:
                    # 根据 响应头 返回不同类型的内容
                    content_type = response.headers.get('Content-Type', '').lower()
                    if "application/json" in content_type:
                        # 处理 JSON 格式
                        content = await response.json()
                    elif "text/" in content_type:
                        # 处理文本格式
                        content = await response.text()

                    elif "image/" in content_type:
                        # 处理图片，转为 Base64
                        raw_content = await response.read()
                        content = base64.b64encode(raw_content).decode('utf-8')  # 转为 Base64 字符串
                    elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                        # 处理二进制数据
                        content = await response.read()
                    else:
                        # 默认处理方式
                        content = await response.text()
                    status_code = response.status
                    cookies = {key: morsel.value for key, morsel in response.cookies.items()}
                    headers = dict(response.headers)
                    return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}
        except Exception as e:
            return {"code": 500, "content": str(e), "cookies": None, "headers": None}

    # 异步网络请求2
    @staticmethod
    async def _req2(method: str, url: str, headers: dict = None, cookies: dict = None,
                    ran_env: str | None = 'chrome124', proxy_url: str = None, **kwargs) -> dict:
        """
        异步网络请求2
        :param method: 请求方法(GET/POST/PUT/DELETE)
        :param url: 请求地址
        :param ran_env: 随机请求环境 None为随机请求环境 默认为chrome124(具体环境进入代码查看)
        :param headers:  请求头(字典类型)
        :param cookies:  cookies(字典类型)
        :param proxy_url: http/socks5h代理
        :param kwargs:  其他参数 如 data=data json=data等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        proxies = None if proxy_url is None else {'http': f'{proxy_url}', 'https': f'{proxy_url}'}
        impersonate = random.choice(ENV_LIST) if ran_env is None else ran_env
        try:
            async with AsyncSession(impersonate=impersonate, headers=headers, cookies=cookies, proxies=proxies,
                                    verify=False) as session:
                response = await session.request(method=method, url=url, timeout=30, **kwargs)
            # 根据 响应头 返回不同类型的内容
            content_type = response.headers.get('Content-Type', '').lower()
            if "application/json" in content_type:
                # 处理 JSON 格式
                content = response.json()
            elif "text/" in content_type:
                # 处理文本格式
                content = response.text
            elif 'image/' in content_type:
                # 处理图片格式
                content = base64.b64encode(response.content).decode('utf-8')
            elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                # 处理二进制数据
                content = response.content
            else:
                # 默认处理方式
                content = response.text
            status_code = response.status_code
            cookies = {key: value for key, value in response.cookies.items()}
            headers = dict(response.headers)
        except Exception as e:
            # 处理超时异常
            if 'timeout' in str(e).lower() or 'timed out' in str(e).lower():
                status_code = 408  # 请求超时
                content = "Request Timeout"
            else:
                status_code = 500  # 网络错误
                content = str(e)
            cookies = {}
            headers = {}
        return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}

    async def _ses_create(self, headers: dict = None, cookies: dict = None, proxy_url: str = None,
                          ran_env: str | None = 'chrome124'):
        """
        创建异步session
        :param headers: 请求头 (可选)
        :param cookies: cookies (可选)
        :param proxy_url: http/socks5h代理(可选)
        :return: session会话
        """
        if self.async_session:
            await self.async_session.close()
        proxies = None if proxy_url is None else {'http': f'{proxy_url}', 'https': f'{proxy_url}'}
        impersonate = random.choice(ENV_LIST) if ran_env is None else ran_env
        self.async_session = AsyncSession(
            impersonate=impersonate,
            headers=headers,
            cookies=cookies,
            proxies=proxies,
            verify=False
        )
        return self.async_session

    async def _ses_close(self):
        """
        关闭异步session
        :return:
        """
        if self.async_session:
            await self.async_session.close()

    # 异步网络请求3
    @staticmethod
    async def _req3(session, method: str, url: str, **kwargs) -> dict:
        """
        异步网络请求3
        :param session: 异步session
        :param method: 请求方法(GET/POST/PUT/DELETE)
        :param url: 请求地址
        :param headers:  请求头(字典类型)
        :param cookies:  cookies(字典类型)
        :param kwargs:  其他参数 如 data=data json=data等
        :return:
                返回 {"code": 200, "content": content, "cookies": response.cookies, "headers": response.headers}
        """
        cookies = {}
        headers = {}
        try:
            response = await session.request(method=method, url=url, timeout=30, **kwargs)
            # 根据 响应头 返回不同类型的内容
            content_type = response.headers.get('Content-Type', '').lower()

            if "application/json" in content_type:
                # 处理 JSON 格式
                content = response.json()
            elif "text/" in content_type:
                # 处理文本格式
                content = response.text
            elif 'image/' in content_type:
                # 处理图片格式
                content = base64.b64encode(response.content).decode('utf-8')
            elif "application/octet-stream" in content_type or "application/pdf" in content_type:
                # 处理二进制数据
                content = response.content
            else:
                # 默认处理方式
                content = response.text
            status_code = response.status_code
            cookies = {key: value for key, value in response.cookies.items()}
            headers = dict(response.headers)
        except exceptions.Timeout:
            status_code = 408  # 请求超时
            content = "Request Timeout"
        except Exception as e:
            status_code = 500  # 网络错误
            content = str(e)
        return {"code": status_code, "content": content, "cookies": cookies, "headers": headers}


async def test():
    pass

if __name__ == '__main__':
    import asyncio

    asyncio.run(test())
