"""
XUI 面板 API 客户端
用于管理 X-UI 面板的入站、出站、路由配置等
"""
import base64
import json
import os
from typing import Optional, Dict, List, Any, Tuple

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from app.utils.logs import getLogger
from app.utils.retry import async_retry

# 获取日志记录器
logger = getLogger('app')


class XuiClient:
    """
    X-UI 面板 API 客户端
    
    用于管理 X-UI 面板的入站、出站、路由配置等功能
    """
    
    def __init__(
        self,
        host: str,
        port: int = 10010,
        username: str = 'admin',
        password: str = 'admin',
        is_ssl: bool = False,
        web_path: str = '/web3'
    ):
        """
        初始化 XUI 客户端
        
        Args:
            host: XUI 面板主机地址
            port: XUI 面板端口
            username: 登录用户名
            password: 登录密码
            is_ssl: 是否使用 HTTPS
            web_path: Web 路径前缀
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.is_ssl = is_ssl
        self.web_path = web_path
        
        # 构建基础 URL
        protocol = 'https' if is_ssl else 'http'
        self.base_url = f'{protocol}://{host}:{port}{web_path}'
        
        # 请求头
        self._json_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._form_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*'
        }
        
        # 会话 cookies
        self._cookies: Dict[str, str] = {}
        self._is_logged_in = False

    async def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        proxy_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步 HTTP 请求
        
        Args:
            method: 请求方法 (GET, POST, PUT, DELETE)
            url: 请求 URL
            headers: 请求头
            cookies: Cookies
            proxy_url: 代理 URL (http/socks5)，如果为 None 则尝试从环境变量读取
            **kwargs: 其他参数 (data, json, ssl 等)
            
        Returns:
            包含响应信息的字典:
            {
                "code": 状态码,
                "content": 响应内容,
                "cookies": 响应 cookies,
                "headers": 响应头
            }
        """
        connector = None
        
        # 如果没有指定代理，尝试从环境变量读取
        if proxy_url is None:
            # 优先使用 HTTPS_PROXY，其次 HTTP_PROXY
            env_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy') or \
                       os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            if env_proxy:
                proxy_url = env_proxy
                logger.debug(f'使用环境变量代理: {proxy_url}')
        
        if proxy_url:
            connector = ProxyConnector.from_url(proxy_url)
        
        try:
            async with ClientSession(
                headers=headers,
                cookies=cookies,
                connector=connector
            ) as session:
                async with session.request(
                    method,
                    url,
                    timeout=30,
                    ssl=False,
                    **kwargs
                ) as response:
                    # 根据 Content-Type 处理响应
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if 'application/json' in content_type:
                        content = await response.json()
                    elif 'text/' in content_type:
                        content = await response.text()
                    elif 'image/' in content_type:
                        raw_content = await response.read()
                        content = base64.b64encode(raw_content).decode('utf-8')
                    elif 'application/octet-stream' in content_type or 'application/pdf' in content_type:
                        content = await response.read()
                    else:
                        content = await response.text()
                    
                    return {
                        'code': response.status,
                        'content': content,
                        'cookies': {key: morsel.value for key, morsel in response.cookies.items()},
                        'headers': dict(response.headers)
                    }
        except Exception as e:
            logger.error(f"请求失败: {method} {url}, 错误: {e}")
            return {
                'code': 500,
                'content': str(e),
                'cookies': None,
                'headers': None
            }

    @async_retry(max_retries=3)
    async def login(self) -> bool:
        """
        登录 XUI 面板
        
        Returns:
            是否登录成功
            
        Raises:
            Exception: 登录失败时抛出异常
        """
        url = f'{self.base_url}/login'
        headers = self._form_headers.copy()
        params = {
            'username': self.username,
            'password': self.password
        }
        
        logger.info(f'正在登录 XUI 面板: {self.host}:{self.port}')
        
        res = await self._request('POST', url, headers=headers, data=params, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'登录失败，HTTP 状态码: {res.get("code")}, 错误: {res.get("content")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'登录失败: {error_msg}')
        
        # 保存 cookies
        self._cookies = res.get('cookies', {})
        self._is_logged_in = True
        
        logger.info(f'XUI 面板登录成功: {self.host}:{self.port}')
        return True
    
    async def ensure_logged_in(self):
        """确保已登录，如果未登录则自动登录"""
        if not self._is_logged_in:
            await self.login()

    # =============== 入站管理 ===============
    
    @async_retry(max_retries=3)
    async def get_inbounds(self) -> Optional[Dict[str, Any]]:
        """
        获取入站列表
        
        Returns:
            入站列表响应数据
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/inbound/list'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'获取入站列表失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'获取入站列表失败: {error_msg}')
        
        logger.info(f'成功获取入站列表，共 {len(content.get("obj", []))} 条')
        return content
    
    @async_retry(max_retries=3)
    async def add_inbound(
        self,
        host: str,
        port: int,
        protocol: str = 'auto',
        username: str = 'cqrxy',
        password: str = 'Zpaily88',
        remark: Optional[str] = None
    ) -> Optional[int]:
        """
        添加入站规则
        
        Args:
            host: 监听地址
            port: 监听端口
            protocol: 协议类型 ('http', 'socks', 'auto')
            username: 认证用户名
            password: 认证密码
            remark: 备注名称
            
        Returns:
            入站 ID，如果端口已存在则返回 None
        """
        await self.ensure_logged_in()
        
        # 端口范围检查
        if not (20000 <= port <= 33000):
            raise ValueError(f'端口必须在 20000-33000 范围内: {port}')
        
        # 自动判断协议
        if protocol == 'auto':
            protocol = 'http' if port < 30000 else 'socks'
        
        if protocol not in ['http', 'socks']:
            raise ValueError(f'不支持的协议: {protocol}')
        
        # 构建入站配置
        payload = self._build_inbound_payload(
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password,
            remark=remark or f'{host}-{protocol}'
        )
        
        url = f'{self.base_url}/panel/api/inbounds/add'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies, json=payload)
        
        if res.get('code') != 200:
            raise Exception(f'添加入站失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict):
            raise Exception(f'添加入站失败: 响应格式错误')
        
        # 检查端口是否已存在
        if 'Port already exists' in content.get('msg', ''):
            logger.warning(f'端口 {port} 已存在，跳过添加')
            return None
        
        if not content.get('success'):
            error_msg = content.get('msg', '未知错误')
            raise Exception(f'添加入站失败: {error_msg}')
        
        inbound_id = content.get('obj', {}).get('id')
        logger.info(f'成功添加入站: {host}:{port} ({protocol}), ID: {inbound_id}')
        return inbound_id
    
    def _build_inbound_payload(
        self,
        host: str,
        port: int,
        protocol: str,
        username: str,
        password: str,
        remark: str
    ) -> Dict[str, Any]:
        """构建入站配置 payload"""
        base_payload = {
            'up': 0,
            'down': 0,
            'total': 0,
            'remark': remark,
            'enable': True,
            'expiryTime': 0,
            'listen': host,
            'port': port,
            'protocol': protocol,
            'sniffing': json.dumps({
                'enabled': False,
                'destOverride': ['http', 'tls', 'quic', 'fakedns'],
                'metadataOnly': False,
                'routeOnly': False
            }),
            'allocate': json.dumps({
                'strategy': 'always',
                'refresh': 5,
                'concurrency': 3
            })
        }
        
        if protocol == 'http':
            base_payload['settings'] = json.dumps({
                'accounts': [{'user': username, 'pass': password}],
                'allowTransparent': False
            })
        elif protocol == 'socks':
            base_payload['settings'] = json.dumps({
                'auth': 'password',
                'accounts': [{'user': username, 'pass': password}],
                'udp': True,
                'ip': '127.0.0.1'
            })
        
        return base_payload

    @async_retry(max_retries=3)
    async def update_inbound(self, inbound_id: int, inbound_config: Dict[str, Any]) -> bool:
        """
        更新入站配置
        
        Args:
            inbound_id: 入站 ID
            inbound_config: 入站配置字典
            
        Returns:
            是否更新成功
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/inbound/update/{inbound_id}'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies, json=inbound_config)
        
        if res.get('code') != 200:
            raise Exception(f'更新入站失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'更新入站失败: {error_msg}')
        
        logger.info(f'成功更新入站 ID: {inbound_id}')
        return True
    
    async def add_user_to_inbound(
        self,
        host: str,
        port: int,
        username: str,
        password: str
    ) -> bool:
        """
        向入站添加用户
        
        Args:
            host: 主机地址
            port: 端口
            username: 用户名
            password: 密码
            
        Returns:
            是否添加成功
        """
        return await self._modify_inbound_user(host, port, username, password, is_add=True)
    
    async def remove_user_from_inbound(
        self,
        host: str,
        port: int,
        username: str,
        password: str
    ) -> bool:
        """
        从入站删除用户
        
        Args:
            host: 主机地址
            port: 端口
            username: 用户名
            password: 密码
            
        Returns:
            是否删除成功
        """
        return await self._modify_inbound_user(host, port, username, password, is_add=False)
    
    async def _modify_inbound_user(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        is_add: bool = True
    ) -> bool:
        """
        修改入站用户（添加或删除）
        
        Args:
            host: 主机地址
            port: 端口
            username: 用户名
            password: 密码
            is_add: True 为添加，False 为删除
        """
        # 获取当前入站配置
        inbound_list = await self.get_inbounds()
        if not inbound_list:
            raise Exception('获取入站配置失败')
        
        inbounds = inbound_list.get('obj', [])
        
        # 查找匹配的入站
        target_inbound = None
        for inbound in inbounds:
            if inbound.get('listen') == host and inbound.get('port') == port:
                target_inbound = inbound
                break
        
        if not target_inbound:
            raise Exception(f'未找到匹配的入站: {host}:{port}')
        
        # 解析 settings
        settings = json.loads(target_inbound.get('settings', '{}'))
        accounts = settings.get('accounts', [])
        
        user_account = {'user': username, 'pass': password}
        
        # 添加或删除用户
        if is_add:
            if user_account not in accounts:
                accounts.append(user_account)
                logger.info(f'添加用户到入站: {username}@{host}:{port}')
            else:
                logger.warning(f'用户已存在: {username}@{host}:{port}')
                return True
        else:
            if user_account in accounts:
                accounts.remove(user_account)
                logger.info(f'从入站删除用户: {username}@{host}:{port}')
            else:
                logger.warning(f'用户不存在: {username}@{host}:{port}')
                return True
        
        # 更新 settings
        settings['accounts'] = accounts
        target_inbound['settings'] = json.dumps(settings)
        
        # 移除 id 字段并更新
        inbound_id = target_inbound.pop('id')
        return await self.update_inbound(inbound_id, target_inbound)

    # =============== 配置管理（出站和路由） ===============
    
    @async_retry(max_retries=3)
    async def get_xray_config(self) -> Dict[str, Any]:
        """
        获取 Xray 配置（包含出站和路由信息）
        
        Returns:
            Xray 配置字典
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/xray/'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'获取 Xray 配置失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'获取 Xray 配置失败: {error_msg}')
        
        xray_setting = content.get('obj', '{}')
        if isinstance(xray_setting, str):
            xray_setting = json.loads(xray_setting)
        
        config = xray_setting.get('xraySetting', {})
        logger.info('成功获取 Xray 配置')
        return config
    
    @async_retry(max_retries=3)
    async def update_xray_config(self, config: Dict[str, Any]) -> bool:
        """
        更新 Xray 配置
        
        Args:
            config: Xray 配置字典
            
        Returns:
            是否更新成功
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/xray/update'
        headers = self._form_headers.copy()
        
        # 将配置转换为 JSON 字符串用于表单提交
        xray_setting_json = json.dumps(config, ensure_ascii=False)
        payload = {'xraySetting': xray_setting_json}
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies, data=payload)
        
        if res.get('code') != 200:
            raise Exception(f'更新 Xray 配置失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'更新 Xray 配置失败: {error_msg}')
        
        logger.info('成功更新 Xray 配置')
        return True
    
    async def configure_outbound_and_routing(
        self,
        inbound_tags: List[Dict[str, Any]]
    ) -> bool:
        """
        配置出站和路由规则
        
        Args:
            inbound_tags: 入站标签列表，格式: [{'host': 'xxx', 'port': xxx}, ...]
            
        Returns:
            是否配置成功
        """
        # 获取当前配置
        current_config = await self.get_xray_config()
        if not current_config:
            raise Exception('获取当前 Xray 配置失败')
        
        # 生成新的 outbound 和 routing 规则
        new_outbounds, new_rules = self._generate_outbound_and_rules(
            inbound_tags,
            current_config
        )
        
        # 更新配置
        current_config['outbounds'] = new_outbounds
        current_config['routing']['rules'] = new_rules
        
        # 提交更新
        return await self.update_xray_config(current_config)
    
    def _generate_outbound_and_rules(
        self,
        inbound_tags: List[Dict[str, Any]],
        current_config: Dict[str, Any]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        生成出站和路由规则
        
        Args:
            inbound_tags: 入站标签列表
            current_config: 当前配置
            
        Returns:
            (新的 outbounds 列表, 新的 rules 列表)
        """
        # 获取现有配置
        existing_outbounds = []
        existing_rules = current_config.get('routing', {}).get('rules', [])
        
        # 用于去重
        existing_outbound_tags = {outbound.get('tag') for outbound in existing_outbounds}
        existing_rule_inbound_tags = set()
        
        # 收集现有规则的 inboundTag
        for rule in existing_rules:
            inbound_tags_in_rule = rule.get('inboundTag', [])
            if isinstance(inbound_tags_in_rule, list):
                existing_rule_inbound_tags.update(inbound_tags_in_rule)
            elif isinstance(inbound_tags_in_rule, str):
                existing_rule_inbound_tags.add(inbound_tags_in_rule)
        
        # 生成新的配置
        new_outbounds = existing_outbounds.copy()
        new_rules = existing_rules.copy()
        
        for in_tag in inbound_tags:
            # 提取 host 和 port
            host = in_tag.get('host')
            port = in_tag.get('port')
            
            if not host or not port:
                logger.warning(f'无效的 inbound_tag: {in_tag}，跳过')
                continue
            
            # 生成 outbound tag
            outbound_tag = f'out-{host}'
            
            # 添加 outbound（如果不存在）
            if outbound_tag not in existing_outbound_tags:
                new_outbound = {
                    'tag': outbound_tag,
                    'protocol': 'freedom',
                    'settings': {},
                    'sendThrough': host
                }
                new_outbounds.append(new_outbound)
                existing_outbound_tags.add(outbound_tag)
                logger.info(f'添加新的 outbound: {outbound_tag}')
            
            # 生成 routing rule
            inbound_tag = f'inbound-{self.host}:{port}'
            
            # 添加 rule（如果不存在）
            if inbound_tag not in existing_rule_inbound_tags:
                new_rule = {
                    'type': 'field',
                    'inboundTag': [inbound_tag],
                    'outboundTag': outbound_tag
                }
                
                # 在系统规则之前插入
                insert_index = len(new_rules)
                for i, rule in enumerate(new_rules):
                    if (rule.get('inboundTag') == ['api'] or
                        rule.get('outboundTag') == 'blocked' or
                        rule.get('protocol') == ['bittorrent']):
                        insert_index = i
                        break
                
                new_rules.insert(insert_index, new_rule)
                existing_rule_inbound_tags.add(inbound_tag)
                logger.info(f'添加新的 routing rule: {inbound_tag} -> {outbound_tag}')
        
        return new_outbounds, new_rules

    # =============== 服务器管理 ===============
    
    @async_retry(max_retries=3)
    async def restart_xray(self) -> bool:
        """
        重启 Xray 服务
        
        Returns:
            是否重启成功
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/server/restartXrayService'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'重启 Xray 服务失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'重启 Xray 服务失败: {error_msg}')
        
        logger.info('成功重启 Xray 服务')
        return True
    
    @async_retry(max_retries=3)
    async def restart_panel(self) -> bool:
        """
        重启 XUI 面板
        
        Returns:
            是否重启成功
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/setting/restartPanel'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'重启面板失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'重启面板失败: {error_msg}')
        
        logger.info('成功重启 XUI 面板')
        return True
    
    @async_retry(max_retries=3)
    async def configure_certificate(
        self,
        cert_file: str = '/opt/xui/fullchain.pem',
        key_file: str = '/opt/xui/privkey.pem',
        web_port: int = 10010,
        web_base_path: str = '/web3/'
    ) -> bool:
        """
        配置 SSL 证书
        
        Args:
            cert_file: 证书文件路径
            key_file: 私钥文件路径
            web_port: Web 端口
            web_base_path: Web 基础路径
            
        Returns:
            是否配置成功
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/panel/setting/update'
        headers = self._form_headers.copy()
        
        payload = {
            'webListen': '',
            'webDomain': '',
            'webPort': str(web_port),
            'webCertFile': cert_file,
            'webKeyFile': key_file,
            'webBasePath': web_base_path,
            'sessionMaxAge': '360',
            'pageSize': '50',
            'expireDiff': '0',
            'trafficDiff': '0',
            'remarkModel': '-ieo',
            'datepicker': 'gregorian',
            'tgBotEnable': 'false',
            'tgBotToken': '',
            'tgBotProxy': '',
            'tgBotAPIServer': '',
            'tgBotChatId': '',
            'tgRunTime': '@daily',
            'tgBotBackup': 'false',
            'tgBotLoginNotify': 'true',
            'tgCpu': '80',
            'tgLang': 'en-US',
            'twoFactorEnable': 'false',
            'twoFactorToken': '',
            'xrayTemplateConfig': '',
            'subEnable': 'false',
            'subTitle': '',
            'subListen': '',
            'subPort': '2096',
            'subPath': '/sub/',
            'subJsonPath': '/json/',
            'subDomain': '',
            'externalTrafficInformEnable': 'false',
            'externalTrafficInformURI': '',
            'subCertFile': '',
            'subKeyFile': '',
            'subUpdates': '12',
            'subEncrypt': 'true',
            'subShowInfo': 'true',
            'subURI': '',
            'subJsonURI': '',
            'subJsonFragment': '',
            'subJsonNoises': '',
            'subJsonMux': '',
            'subJsonRules': '',
            'timeLocation': 'Local'
        }
        
        res = await self._request('POST', url, headers=headers, data=payload, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'配置证书失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'配置证书失败: {error_msg}')
        
        logger.info('成功配置 SSL 证书')
        return True
    
    @async_retry(max_retries=3)
    async def get_server_status(self) -> Dict[str, Any]:
        """
        获取服务器状态信息
        
        Returns:
            服务器状态字典
        """
        await self.ensure_logged_in()
        
        url = f'{self.base_url}/server/status'
        headers = self._json_headers.copy()
        
        res = await self._request('POST', url, headers=headers, cookies=self._cookies)
        
        if res.get('code') != 200:
            raise Exception(f'获取服务器状态失败，HTTP 状态码: {res.get("code")}')
        
        content = res.get('content')
        if not isinstance(content, dict) or not content.get('success'):
            error_msg = content.get('msg', '未知错误') if isinstance(content, dict) else str(content)
            raise Exception(f'获取服务器状态失败: {error_msg}')
        
        status_info = content.get('obj', '{}')
        if isinstance(status_info, str):
            status_info = json.loads(status_info)
        
        logger.info('成功获取服务器状态')
        return status_info


    # =============== 批量操作 ===============
    
    async def batch_add_inbounds(
        self,
        inbound_configs: List[Dict[str, Any]]
    ) -> List[Optional[int]]:
        """
        批量添加入站
        
        Args:
            inbound_configs: 入站配置列表，每项包含 host, port, protocol 等
            
        Returns:
            入站 ID 列表
        """
        results = []
        for config in inbound_configs:
            try:
                inbound_id = await self.add_inbound(**config)
                results.append(inbound_id)
            except Exception as e:
                logger.error(f'批量添加入站失败: {config}, 错误: {e}')
                results.append(None)
        
        return results
    
    async def batch_add_users(
        self,
        user_configs: List[Dict[str, Any]]
    ) -> List[bool]:
        """
        批量添加用户到入站
        
        Args:
            user_configs: 用户配置列表，每项包含 host, port, username, password
            
        Returns:
            操作结果列表
        """
        results = []
        for config in user_configs:
            try:
                success = await self.add_user_to_inbound(**config)
                results.append(success)
            except Exception as e:
                logger.error(f'批量添加用户失败: {config}, 错误: {e}')
                results.append(False)
        
        return results
    
    async def initialize_xui_panel(
        self,
        inbound_configs: List[Dict[str, Any]],
        cert_file: Optional[str] = None,
        key_file: Optional[str] = None
    ) -> bool:
        """
        初始化 XUI 面板（一键配置）
        
        Args:
            inbound_configs: 入站配置列表
            cert_file: SSL 证书文件路径
            key_file: SSL 私钥文件路径
            
        Returns:
            是否初始化成功
        """
        try:
            logger.info('开始初始化 XUI 面板')
            
            # 1. 登录
            await self.login()
            
            # 2. 批量添加入站
            logger.info(f'添加 {len(inbound_configs)} 个入站配置')
            await self.batch_add_inbounds(inbound_configs)
            
            # 3. 配置出站和路由
            logger.info('配置出站和路由规则')
            inbound_tags = [
                {'host': config['host'], 'port': config['port']}
                for config in inbound_configs
            ]
            await self.configure_outbound_and_routing(inbound_tags)
            
            # 4. 配置证书（如果提供）
            if cert_file and key_file:
                logger.info('配置 SSL 证书')
                await self.configure_certificate(cert_file=cert_file, key_file=key_file)
            
            # 5. 重启 Xray 服务
            logger.info('重启 Xray 服务')
            await self.restart_xray()
            
            # 6. 重启面板
            if cert_file and key_file:
                logger.info('重启 XUI 面板')
                await self.restart_panel()
            
            logger.info('XUI 面板初始化完成')
            return True
            
        except Exception as e:
            logger.error(f'XUI 面板初始化失败: {e}')
            raise
