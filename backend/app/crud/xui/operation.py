"""
XUI 操作 CRUD（初始化、重启等）
"""
import json
from uuid import UUID
from fastapi import HTTPException
from typing import List, Dict, Any

from app.models.xui import XuiServer, XuiInbound
from app.schemas.xui.user import XuiOperationResponse
from app.core.tools import aes_decrypt
from app.clients.xui import XuiClient
from app.utils.logs import getLogger

logger = getLogger('app')


class XuiOperationCRUD:
    """XUI 操作 CRUD"""
    
    async def _get_xui_client(self, server_id: UUID) -> XuiClient:
        """获取 XUI 客户端实例"""
        server = await XuiServer.get_or_none(id=server_id)
        if not server:
            raise HTTPException(status_code=404, detail='XUI 服务器不存在')
        
        # 优先使用 domain，如果没有则使用 host
        connect_host = server.domain if server.domain else server.host
        
        # 解密密码（使用 host 作为加密 key）
        try:
            password = aes_decrypt(server.password, server.host)
        except Exception as e:
            logger.error(f'解密 XUI 密码失败: {e}')
            raise HTTPException(status_code=500, detail='解密密码失败')
        
        return XuiClient(
            host=connect_host,
            port=server.port,
            username=server.username,
            password=password,
            is_ssl=server.is_ssl,
            web_path=server.web_path
        )
    
    async def initialize_panel(
        self,
        server_id: UUID,
        inbound_configs: List[Dict[str, Any]],
        configure_cert: bool = False
    ) -> XuiOperationResponse:
        """初始化 XUI 面板"""
        try:
            # 获取服务器信息
            server = await XuiServer.get_or_none(id=server_id)
            if not server:
                raise HTTPException(status_code=404, detail='XUI 服务器不存在')
            
            # 获取客户端
            client = await self._get_xui_client(server_id)
            
            # 准备证书配置
            cert_file = server.cert_file if configure_cert else None
            key_file = server.key_file if configure_cert else None
            
            # 一键初始化
            success = await client.initialize_xui_panel(
                inbound_configs=inbound_configs,
                cert_file=cert_file,
                key_file=key_file
            )
            
            if success:
                return XuiOperationResponse(
                    success=True,
                    message='XUI 面板初始化成功',
                    data={'server_id': str(server_id)}
                )
            else:
                return XuiOperationResponse(
                    success=False,
                    message='XUI 面板初始化失败'
                )
        
        except Exception as e:
            logger.error(f'初始化 XUI 面板失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'初始化失败: {str(e)}'
            )
    
    async def restart_xray(self, server_id: UUID) -> XuiOperationResponse:
        """重启 Xray 服务"""
        try:
            client = await self._get_xui_client(server_id)
            success = await client.restart_xray()
            
            if success:
                return XuiOperationResponse(
                    success=True,
                    message='Xray 服务重启成功'
                )
            else:
                return XuiOperationResponse(
                    success=False,
                    message='Xray 服务重启失败'
                )
        
        except Exception as e:
            logger.error(f'重启 Xray 服务失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'重启失败: {str(e)}'
            )
    
    async def restart_panel(self, server_id: UUID) -> XuiOperationResponse:
        """重启 XUI 面板"""
        try:
            client = await self._get_xui_client(server_id)
            success = await client.restart_panel()
            
            if success:
                return XuiOperationResponse(
                    success=True,
                    message='XUI 面板重启成功'
                )
            else:
                return XuiOperationResponse(
                    success=False,
                    message='XUI 面板重启失败'
                )
        
        except Exception as e:
            logger.error(f'重启 XUI 面板失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'重启失败: {str(e)}'
            )
    
    async def configure_certificate(
        self,
        server_id: UUID,
        cert_file: str,
        key_file: str
    ) -> XuiOperationResponse:
        """配置 SSL 证书"""
        try:
            client = await self._get_xui_client(server_id)
            success = await client.configure_certificate(
                cert_file=cert_file,
                key_file=key_file
            )
            
            if success:
                # 更新数据库中的证书配置
                server = await XuiServer.get(id=server_id)
                server.cert_file = cert_file
                server.key_file = key_file
                await server.save()
                
                return XuiOperationResponse(
                    success=True,
                    message='SSL 证书配置成功'
                )
            else:
                return XuiOperationResponse(
                    success=False,
                    message='SSL 证书配置失败'
                )
        
        except Exception as e:
            logger.error(f'配置 SSL 证书失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'配置失败: {str(e)}'
            )
    
    async def configure_outbound_routing(
        self,
        server_id: UUID,
        inbound_ids: List[UUID]
    ) -> XuiOperationResponse:
        """配置出站和路由"""
        try:
            client = await self._get_xui_client(server_id)
            
            # 获取入站信息
            inbounds = await XuiInbound.filter(id__in=inbound_ids)
            if not inbounds:
                raise HTTPException(status_code=404, detail='未找到入站配置')
            
            # 构建入站标签列表
            inbound_tags = [
                {'host': inbound.listen_host, 'port': inbound.listen_port}
                for inbound in inbounds
            ]
            
            # 配置出站和路由
            success = await client.configure_outbound_and_routing(inbound_tags)
            
            if success:
                return XuiOperationResponse(
                    success=True,
                    message='出站和路由配置成功'
                )
            else:
                return XuiOperationResponse(
                    success=False,
                    message='出站和路由配置失败'
                )
        
        except Exception as e:
            logger.error(f'配置出站和路由失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'配置失败: {str(e)}'
            )
    
    async def get_server_status(self, server_id: UUID) -> XuiOperationResponse:
        """获取服务器状态"""
        try:
            client = await self._get_xui_client(server_id)
            status = await client.get_server_status()
            
            return XuiOperationResponse(
                success=True,
                message='获取服务器状态成功',
                data=status
            )
        
        except Exception as e:
            logger.error(f'获取服务器状态失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'获取失败: {str(e)}'
            )
    
    async def sync_inbounds_from_panel(self, server_id: UUID) -> XuiOperationResponse:
        """
        从 XUI 面板同步入站配置到数据库
        
        同时同步到 ServerInfo 模型：
        - 使用 XUI 服务器的名称作为 ServerGroup 名称
        - 创建或更新 ServerInfo 记录
        
        Args:
            server_id: XUI 服务器 ID
            
        Returns:
            同步结果
        """
        try:
            from app.models.xui import XuiInbound, XuiProtocol
            from app.models.server import ServerInfo, ServerGroup, ServerCountry
            from app.core.tools import aes_encrypt
            
            # 获取服务器信息
            server = await XuiServer.get_or_none(id=server_id)
            if not server:
                raise HTTPException(status_code=404, detail='XUI 服务器不存在')
            
            # 获取客户端
            client = await self._get_xui_client(server_id)
            
            # 从面板获取入站列表
            result = await client.get_inbounds()
            if not result or not result.get('success'):
                raise Exception('获取入站列表失败')
            
            inbounds_data = result.get('obj', [])
            
            # 统计信息
            created_count = 0
            updated_count = 0
            skipped_count = 0
            server_info_created = 0
            server_info_updated = 0
            errors = []
            
            for inbound_data in inbounds_data:
                try:
                    # 提取入站信息
                    inbound_id = inbound_data.get('id')
                    listen = inbound_data.get('listen', '')
                    port = inbound_data.get('port')
                    protocol_str = inbound_data.get('protocol', '').lower()
                    remark = inbound_data.get('remark', '')
                    enable = inbound_data.get('enable', True)
                    
                    # 端口过滤规则：跳过 20000-21999 和 30000-31999 范围的端口
                    if (20000 <= port <= 21999) or (30000 <= port <= 31999):
                        logger.info(f'跳过端口 {port}（在过滤范围内）')
                        skipped_count += 1
                        continue
                    
                    # 解析 settings 获取默认账号
                    settings_str = inbound_data.get('settings', '{}')
                    try:
                        settings = json.loads(settings_str) if isinstance(settings_str, str) else settings_str
                        accounts = settings.get('accounts', [])
                        default_username = accounts[0].get('user', 'cqrxy') if accounts else 'cqrxy'
                        default_password = accounts[0].get('pass', 'Zpaily88') if accounts else 'Zpaily88'
                    except Exception as e:
                        logger.warning(f'解析 settings 失败: {e}')
                        default_username = 'cqrxy'
                        default_password = 'Zpaily88'
                    
                    # 确定协议类型
                    if protocol_str == 'http':
                        protocol = XuiProtocol.HTTP
                    elif protocol_str == 'socks':
                        protocol = XuiProtocol.SOCKS
                    else:
                        logger.warning(f'未知协议类型: {protocol_str}，跳过')
                        skipped_count += 1
                        continue
                    
                    # 确定监听地址（如果为空则使用服务器地址）
                    listen_host = listen if listen else server.host
                    
                    # 检查是否已存在
                    existing = await XuiInbound.get_or_none(
                        server_id=server_id,
                        listen_host=listen_host,
                        listen_port=port
                    )
                    
                    # 加密默认密码
                    encrypted_password = aes_encrypt(
                        default_password,
                        f"{listen_host}:{port}"
                    )
                    
                    if existing:
                        # 更新现有记录
                        existing.inbound_id = inbound_id
                        existing.protocol = protocol
                        existing.remark = remark
                        existing.status = 1 if enable else 2
                        existing.default_username = default_username
                        existing.default_password = encrypted_password
                        await existing.save()
                        updated_count += 1
                        logger.info(f'更新入站: {listen_host}:{port}')
                    else:
                        # 创建新记录
                        await XuiInbound.create(
                            server_id=server_id,
                            inbound_id=inbound_id,
                            listen_host=listen_host,
                            listen_port=port,
                            protocol=protocol,
                            remark=remark,
                            status=1 if enable else 2,
                            default_username=default_username,
                            default_password=encrypted_password
                        )
                        created_count += 1
                        logger.info(f'创建入站: {listen_host}:{port}')
                    
                    # 同步到 ServerInfo 模型
                    try:
                        # 使用 XUI 服务器名称作为分组名称（截断到 20 字符）
                        group_name = server.name[:20] if len(server.name) > 20 else server.name
                        
                        # 查找或创建 ServerGroup（使用 XUI 服务器名称作为分组名称）
                        group = await ServerGroup.get_or_none(name=group_name)
                        
                        if not group:
                            # 如果分组不存在，需要先获取一个默认国家
                            # 尝试获取第一个国家，如果没有则创建一个默认国家
                            default_country = await ServerCountry.first()
                            if not default_country:
                                default_country = await ServerCountry.create(
                                    short_name='UN',
                                    name='未知',
                                    status=1
                                )
                                logger.info(f'创建默认国家: {default_country.name}')
                            
                            # 创建新分组
                            group = await ServerGroup.create(
                                name=group_name,
                                country_id=default_country.id,
                                status=1
                            )
                            logger.info(f'创建服务器分组: {group_name}')
                        
                        # 查找或创建 ServerInfo
                        server_info = await ServerInfo.get_or_none(
                            host=listen_host,
                            port=port
                        )
                        
                        if server_info:
                            # 更新现有 ServerInfo
                            server_info.group_id = group.id
                            server_info.status = 1 if enable else 2
                            # 同步域名（如果 XUI 服务器有域名）
                            if server.domain:
                                server_info.domain = server.domain
                            # 如果 ssh_port 为空，设置默认值
                            if not server_info.ssh_port:
                                server_info.ssh_port = 9527
                            await server_info.save()
                            server_info_updated += 1
                            logger.info(f'更新服务器信息: {listen_host}:{port} -> 分组: {group_name}, 域名: {server.domain or "无"}')
                        else:
                            # 创建新 ServerInfo
                            await ServerInfo.create(
                                host=listen_host,
                                port=port,
                                ssh_port=9527,  # 默认 SSH 端口
                                domain=server.domain,  # 同步域名
                                group_id=group.id,
                                status=1 if enable else 2,
                                is_sale=1  # 默认为销售
                            )
                            server_info_created += 1
                            logger.info(f'创建服务器信息: {listen_host}:{port} -> 分组: {group_name}, 域名: {server.domain or "无"}')
                    
                    except Exception as e:
                        error_msg = f'同步 ServerInfo 失败 (port={port}): {str(e)}'
                        logger.error(error_msg)
                        errors.append(error_msg)
                
                except Exception as e:
                    error_msg = f'处理入站失败 (port={port}): {str(e)}'
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # 构建响应消息
            message = f'同步完成: 创建 {created_count} 个入站，更新 {updated_count} 个入站，跳过 {skipped_count} 个'
            message += f' | 服务器信息: 创建 {server_info_created} 个，更新 {server_info_updated} 个'
            if errors:
                message += f'，{len(errors)} 个错误'
            
            return XuiOperationResponse(
                success=True,
                message=message,
                data={
                    'inbound_created': created_count,
                    'inbound_updated': updated_count,
                    'inbound_skipped': skipped_count,
                    'server_info_created': server_info_created,
                    'server_info_updated': server_info_updated,
                    'errors': errors
                }
            )
        
        except Exception as e:
            logger.error(f'同步入站配置失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'同步失败: {str(e)}'
            )
    
    async def get_xray_config_from_panel(self, server_id: UUID) -> XuiOperationResponse:
        """
        从 XUI 面板获取 Xray 配置（出站和路由）
        
        Args:
            server_id: XUI 服务器 ID
            
        Returns:
            Xray 配置信息
        """
        try:
            # 获取客户端
            client = await self._get_xui_client(server_id)
            
            # 获取 Xray 配置
            config = await client.get_xray_config()
            
            if not config:
                raise Exception('获取 Xray 配置失败')
            
            # 提取关键信息
            outbounds = config.get('outbounds', [])
            routing = config.get('routing', {})
            rules = routing.get('rules', [])
            
            # 统计信息
            outbound_count = len(outbounds)
            rule_count = len(rules)
            
            # 分析出站
            outbound_summary = []
            for outbound in outbounds:
                tag = outbound.get('tag', 'N/A')
                protocol = outbound.get('protocol', 'N/A')
                send_through = outbound.get('sendThrough', 'N/A')
                outbound_summary.append({
                    'tag': tag,
                    'protocol': protocol,
                    'sendThrough': send_through
                })
            
            # 分析路由规则
            rule_summary = []
            for rule in rules:
                rule_type = rule.get('type', 'N/A')
                inbound_tag = rule.get('inboundTag', [])
                outbound_tag = rule.get('outboundTag', 'N/A')
                rule_summary.append({
                    'type': rule_type,
                    'inboundTag': inbound_tag,
                    'outboundTag': outbound_tag
                })
            
            return XuiOperationResponse(
                success=True,
                message=f'获取成功: {outbound_count} 个出站，{rule_count} 条路由规则',
                data={
                    'outbound_count': outbound_count,
                    'rule_count': rule_count,
                    'outbounds': outbound_summary,
                    'rules': rule_summary,
                    'full_config': config  # 完整配置
                }
            )
        
        except Exception as e:
            logger.error(f'获取 Xray 配置失败: {e}')
            return XuiOperationResponse(
                success=False,
                message=f'获取失败: {str(e)}'
            )


xui_operation_crud = XuiOperationCRUD()
