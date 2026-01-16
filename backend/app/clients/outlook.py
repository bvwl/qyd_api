import time
import base64
import hashlib
import os
import traceback
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Tuple, Dict, List
from pydantic import BaseModel, Field
from app.models.mail import EmailInfo
from loguru import logger
from app.utils.retry import async_retry
from app.utils.req import Req


# 定义结果模型
class TokenResult(BaseModel):
    """
    令牌获取结果模型
    用于返回授权成功后的 access_token 和 refresh_token
    """
    access_token: str = Field(..., description='访问令牌')
    refresh_token: str | None = Field(None, description='刷新令牌')
    client_id: str = Field(..., description='使用的客户端 ID')
    created_at: float = Field(default_factory=time.time, description='Token 创建时间戳')


class AzureAuthManager(Req):
    """
    Azure 授权管理类 (免注册模式)
    
    核心设计理念：
    1. 免注册应用：直接使用微软官方公共客户端 ID (Client ID)，无需用户手动在 Azure Portal 注册应用。
    2. PKCE 安全流程：使用 Proof Key for Code Exchange (PKCE) 增强 OAuth2 安全性，适用于公共客户端。
    3. 自动化集成：集成了令牌获取、刷新、邮件发送和读取等核心功能。
    4. 代理支持：根据服务器端口自动配置 HTTP 或 SOCKS5 代理。
    """

    # 使用 Microsoft Graph PowerShell 的 Client ID (客户端 ID)
    # 这是一个微软官方的第一方应用 ID，具有以下优势：
    # 1. 公共客户端：支持个人账号 (Outlook/Hotmail) 和组织账号 (Office 365)。
    # 2. 宽容的重定向：支持 localhost 重定向，便于本地开发和自动化工具使用。
    # 3. 稳定性：作为官方 ID，比自建应用更稳定，不易触发"未验证应用"警告或被风控封禁。
    CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

    # 官方应用支持的重定向 URI (回调地址)
    # 对于移动应用或桌面应用模式，通常使用 localhost
    REDIRECT_URI = "http://localhost"

    # Graph API 基础地址 (接口地址)
    GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

    # 请求的权限范围 (Scopes)
    # openid, profile, offline_access: 基础身份认证和获取 refresh_token 必须
    # User.Read: 读取用户基本信息
    # Mail.ReadWrite: 读取和移动/删除邮件
    # Mail.Send: 发送邮件
    SCOPES = [
        "openid",
        "profile",
        "offline_access",
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/Mail.Send"
    ]

    def __init__(self, email: str):
        super().__init__()
        self.session = None
        self.email = email
        self.token_file = "azure_token.json"
        self.proxy = None
        self.client_id = None
        self.access_token = None
        # 使用 refresh_token_value 存储实际的 refresh_token，避免与方法名冲突
        self.refresh_token_value = None

    # 读取配置
    async def read_config(self) -> int:
        """
        从数据库读取邮箱配置和代理信息
        
        逻辑说明：
        1. 查询 EmailInfo 模型，预加载 server_info 关联表。
        2. 如果存在 server_info，根据端口号范围配置代理类型：
           - 20000 <= port < 30000: 使用 HTTP 代理
           - 30000 <= port < 40000: 使用 SOCKS5 代理
        3. 加载 client_id, access_token, refresh_token 到内存。
        
        :return: 
            0: 未配置 (无 client_id 且无 token)
            1: 已配置 (完整配置)
            2: 仅配置了客户端ID (等待授权)
        """
        mail_info = await EmailInfo.get_or_none(email=self.email).prefetch_related("server_info")
        if mail_info:
            self.client_id = mail_info.client_id
            self.access_token = mail_info.access_token
            self.refresh_token_value = mail_info.refresh_token
            server = await mail_info.server_info
            if server:
                host = server.domain or server.host
                port = server.port
                # 根据端口范围区分代理协议
                if 20000 <= port < 30000:
                    self.proxy = f"http://cqrxy:Zpaily88@{host}:{port}"
                elif 30000 <= port < 40000:
                    self.proxy = f"socks5://cqrxy:Zpaily88@{host}:{port}"

        if self.client_id and not self.access_token and not self.refresh_token_value:
            return 2
        elif not self.client_id and not self.access_token and not self.refresh_token_value:
            return 0
        return 1

    # 生成 PKCE 验证对 (code_verifier, code_challenge)
    async def _generate_pkce_pair(self) -> Tuple[str, str]:
        """
        生成 PKCE (Proof Key for Code Exchange) 验证对
        
        PKCE 是 OAuth 2.0 的安全扩展，用于防止授权码拦截攻击。
        流程：
        1. 生成随机字符串 code_verifier。
        2. 对 verifier 进行 SHA256 哈希并 Base64 编码，生成 code_challenge。
        3. 授权请求带上 challenge，换 Token 请求带上 verifier，服务器验证两者匹配。
        
        :return: (code_verifier, code_challenge)
        """
        # 生成随机 code_verifier (32字节随机数 -> Base64)
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

        # 生成 code_challenge (S256 算法: Base64(SHA256(verifier)))
        m = hashlib.sha256()
        m.update(code_verifier.encode('utf-8'))
        code_challenge = base64.urlsafe_b64encode(m.digest()).decode('utf-8').rstrip('=')

        return code_verifier, code_challenge

    # 获取授权 URL
    async def generate_auth_url(self) -> Tuple[str, str]:
        """
        生成授权 URL 和 PKCE 验证码
        
        用于前端展示授权链接，用户点击后登录微软账号并授权。
        
        :return: (auth_url, verifier) 
                 auth_url: 用户浏览器访问的地址
                 verifier: 后续换取 Token 时需要的验证码 (需暂存)
        """
        # 1. 生成 PKCE 参数 (验证码和挑战码)
        verifier, challenge = await self._generate_pkce_pair()

        # 2. 构造授权 URL 参数
        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",  # 请求授权码
            "redirect_uri": self.REDIRECT_URI,
            "response_mode": "query",
            "scope": " ".join(self.SCOPES),  # 申请的权限
            "prompt": "select_account",  # 强制显示账号选择界面
            "code_challenge": challenge,  # PKCE 挑战码
            "code_challenge_method": "S256"
        }
        # 使用 /common 端点以同时支持个人 (Personal) 和组织 (Work/School) 账号
        auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"

        return auth_url, verifier

    # 获取令牌
    @async_retry()
    async def get_token_from_url(self, full_url: str, code_verifier: str) -> TokenResult | int:
        """
        使用授权回调 URL 换取 Access Token
        
        流程：
        1. 解析回调 URL 中的 code 参数。
        2. 使用 code + code_verifier 向 token 端点请求令牌 (PKCE 验证)。
        3. 保存 access_token 和 refresh_token 到数据库。
        
        :param full_url: 用户授权后跳转的完整回调 URL (包含 code)
        :param code_verifier: 生成授权 URL 时对应的 verifier
        :return: TokenResult 对象或 0 (失败)
        """
        # 解析 Code
        try:
            parsed = urlparse(full_url)
            qs = parse_qs(parsed.query)

            # 检查是否有错误参数
            if "error" in qs:
                error_code = qs["error"][0]
                error_desc = qs.get("error_description", ["未知错误"])[0]
                logger.error(f"[{self.email}] ❌ 授权失败: {error_code} - {error_desc}")
                return 0

            if "code" not in qs:
                logger.error(f"\n[{self.email}] ❌ 错误: 未找到授权码。请确认复制了完整的跳转链接。")
                return 0

            code = qs["code"][0]
        except Exception as e:
            # 简单的错误提示优化
            if "invalid_scope" in str(e):
                logger.error(f"\n[{self.email}] ❌ 错误: 权限范围无效。这通常是因为该账号类型不支持某些请求的权限。")
            logger.error(f"[{self.email}] ❌ 解析 URL 失败: {e}")
            return 0

        logger.info(f"[{self.email}] 已获取授权码，正在请求 Token...")

        bol = await self.read_config()
        if bol == 0:
            logger.error(f"[{self.email}] 未找到授权信息")
            return 0
            
        # 使用 Code 换取 Token
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.SCOPES),
            "code": code,
            "redirect_uri": self.REDIRECT_URI,
            "grant_type": "authorization_code", # 授权码模式
            "code_verifier": code_verifier,     # PKCE 验证
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # 发送请求 (带代理)
        res = await self._req("POST", token_url, data=data, headers=headers, proxy_url=self.proxy)
        status_code = res['code']
        content = res.get("content")
        
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        elif status_code != 200:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
            
        # 更新数据库
        email_info = await EmailInfo.get_or_none(email=self.email)
        if email_info:
            email_info.access_token = content.get("access_token")
            email_info.refresh_token = content.get("refresh_token")
            await email_info.save()
            
        return TokenResult(
            access_token=content.get("access_token"),
            refresh_token=content.get("refresh_token"),
            client_id=self.client_id
        )

    # 刷新 Token
    @async_retry()
    async def refresh_token(self) -> int:
        """
        使用 refresh_token 刷新访问令牌 (Access Token)
        
        当 Access Token 过期 (通常 1 小时) 时调用。
        :return: 1 (成功) 或 0 (失败)
        """
        bol = await self.read_config()
        if bol != 1 or not self.refresh_token_value:
            logger.error(f"[{self.email}] 未找到授权信息")
            return 0
            
        logger.info(f"[{self.email}] Token 即将过期或已过期，正在刷新...")
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.SCOPES),
            "refresh_token": self.refresh_token_value,
            "grant_type": "refresh_token", # 刷新令牌模式
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        res = await self._req("POST", token_url, data=data, headers=headers, proxy_url=self.proxy)
        status_code = res['code']
        content = res.get("content")
        
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        elif status_code != 200:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
            
        logger.success(f"[{self.email}] ✅ Token 刷新成功！")
        access_token = content.get("access_token")
        refresh_token = content.get("refresh_token")
        
        # 更新内存和数据库
        self.access_token = access_token
        self.refresh_token_value = refresh_token or self.refresh_token_value
        email_info = await EmailInfo.get_or_none(email=self.email)
        if email_info:
            email_info.access_token = access_token
            email_info.refresh_token = refresh_token or self.refresh_token_value
            await email_info.save()
        return 1

    def _get_headers(self) -> Dict[str, str]:
        """构造 Graph API 标准请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    # 获取用户信息
    @async_retry()
    async def get_user_info(self) -> Dict | int:
        """
        调用 /me 接口获取当前用户信息
        用于验证 Token 有效性和获取用户 Profile
        """
        url = f"{self.GRAPH_API_URL}/me"
        res = await self._req("GET", url, headers=self._get_headers(), proxy_url=self.proxy)
        status_code = res['code']
        content = res.get("content")
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        if status_code != 200:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
        return content

    # 获取邮件列表
    @async_retry()
    async def get_messages(self, folder_id: str = 'inbox', top: int = 10) -> Dict | int:
        """
        获取指定文件夹的邮件列表
        
        :param folder_id: 文件夹 ID，默认为收件箱 'inbox'，也可以是 'junkemail' 等
        :param top: 获取数量限制
        :return: 邮件列表数据字典
        """
        url = f"{self.GRAPH_API_URL}/me/mailFolders/{folder_id}/messages"
        params = {
            "$top": top,
            "$select": "id,subject,from,receivedDateTime,bodyPreview,body", # 只查询必要字段
            "$orderby": "receivedDateTime desc" # 按时间倒序
        }
        res = await self._req("GET", url, headers=self._get_headers(), params=params, proxy_url=self.proxy)
        status_code = res['code']
        content = res.get("content")
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        if status_code != 200:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
        return content

    # 移动邮件
    @async_retry()
    async def move_message(self, message_id: str, destination_id: str = 'inbox') -> int:
        """
        将邮件移动到指定文件夹
        
        通常用于将垃圾邮件箱的误判邮件移回收件箱
        :param message_id: 邮件 ID
        :param destination_id: 目标文件夹 ID
        """
        url = f"{self.GRAPH_API_URL}/me/messages/{message_id}/move"
        data = {"destinationId": destination_id}
        res = await self._req("POST", url, headers=self._get_headers(), json=data, proxy_url=self.proxy)
        status_code = res['code']
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        elif status_code != 201:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
        return 1

    # 发送邮件
    @async_retry()
    async def send_message(self, subject: str, content: str, to_recipients: list[str] | str,
                           content_type: str = 'Text') -> int:
        """
        发送邮件
        
        :param subject: 邮件主题
        :param content: 邮件内容
        :param to_recipients: 收件人列表或单个收件人邮箱
        :param content_type: 内容类型 'Text' 或 'HTML'
        """
        url = f"{self.GRAPH_API_URL}/me/sendMail"

        to_list = []
        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]

        for email in to_recipients:
            to_list.append({
                "emailAddress": {
                    "address": email
                }
            })

        data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": content_type,
                    "content": content
                },
                "toRecipients": to_list
            },
            "saveToSentItems": "true" # 保存到已发送文件夹
        }
        res = await self._req("POST", url, headers=self._get_headers(), json=data, proxy_url=self.proxy)
        status_code = res['code']
        if status_code >= 500:
            raise Exception(f"请求失败: {status_code}")
        elif status_code != 202:
            logger.error(f"[{self.email}] ❌ 响应状态码: {status_code}")
            return 0
        logger.success(f"[{self.email}] ✅ 邮件发送成功！")
        return 1

    # 获取邮件主逻辑
    async def get_emails_main(self, from_email: str, num: int = 1, top: int = 10) -> int | List:
        """
        获取符合特定发件人的邮件主流程
        
        流程：
        1. 加载配置并刷新 Token。
        2. 检查垃圾邮件箱 (Junk Email)：
           - 如果发现有邮件，尝试将其移动到收件箱 (防止误判)。
        3. 检查收件箱 (Inbox)：
           - 遍历邮件，匹配发件人 (from_email)。
           - 提取符合条件的邮件内容。
        
        :param from_email: 目标发件人邮箱 (支持模糊匹配)
        :param num: 需要获取的匹配邮件数量
        :param top: API 单次查询的邮件数量
        :return: 邮件列表 或 0 (无匹配)
        """
        try:
            # 加载环境
            await self.read_config()

            # 刷新令牌
            if not await self.refresh_token():
                return 0

            # 检查垃圾邮件
            junk_msgs = await self.get_messages(folder_id='junkemail', top=top)
            # 防御：只在返回为 dict 且包含 value 时再遍历
            if isinstance(junk_msgs, dict) and 'value' in junk_msgs:
                for msg in junk_msgs.get('value', []):
                    logger.info(f"[{self.email}] {msg.get('subject')}")
                    # 移动到收件箱
                    bol = await self.move_message(msg.get('id'), 'inbox')
                    if bol:
                        logger.info(f"[{self.email}] 移动邮件 {msg.get('id')} 成功")
                    else:
                        logger.info(f"[{self.email}] 移动邮件 {msg.get('id')} 失败")

            # 获取收件箱邮件
            out_list = []
            inbox_msgs = await self.get_messages(folder_id='inbox', top=top)
            if isinstance(inbox_msgs, dict) and 'value' in inbox_msgs:
                for i, msg in enumerate(inbox_msgs.get("value", []), 1):
                    from_addr = msg.get('from', {}).get('emailAddress', {}).get('address')
                    content = msg.get('body', {}).get('content', '')
                    # 匹配发件人
                    if from_email in (from_addr or ''):
                        out_list.append({
                            "from_email": from_addr,
                            'title': msg.get('subject'),
                            "content": content
                        })
                    if i >= num:
                        break
                if not out_list:
                    return 0
                return out_list
            return 0
        except Exception as e:
            # 打印完整堆栈，便于定位类似 'str' object is not callable 之类的错误
            logger.error(f"[{self.email}] get_emails_main 发生异常: {e}\n{traceback.format_exc()}")
            return 0

    # 发送邮件主逻辑
    async def send_email_main(self, to_email: str, subject: str, content: str, content_type: str = 'Text') -> int:
        """
        发送邮件封装方法
        包含配置加载和 Token 刷新逻辑
        """
        # 加载环境
        await self.read_config()
        # 刷新令牌
        if not await self.refresh_token():
            return 0
        # 发送邮件
        bol = await self.send_message(subject, content, to_email, content_type)
        if bol:
            logger.info(f"[{self.email}] 发送邮件 {to_email} 成功")
            return 1
        else:
            logger.info(f"[{self.email}] 发送邮件 {to_email} 失败")
            return 0

    # 用授权码换取令牌主逻辑
    async def get_token_main(self, url: str, code_verifier: str) -> TokenResult | int:
        """
        用授权码换取令牌封装方法
        包含配置加载
        """
        # 加载令牌（如果有）
        await self.read_config()
        res = await self.get_token_from_url(url, code_verifier)
        if not res:
            return 0
        logger.info(f"[{self.email}] 获取令牌成功")
        return res
