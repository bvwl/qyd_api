"""
安全日志工具（简化版）
只记录关键的越权操作和非法操作，避免数据库压力
"""
from enum import IntEnum
from typing import Optional
from uuid import UUID
from fastapi import Request
from app.models.user import UserLog
from app.utils.logs import getLogger
from app.utils.log_middleware import get_request_ip

# 获取安全日志记录器
security_logger = getLogger('security')


class LogAction(IntEnum):
    """操作日志类型枚举（简化版 - 只记录关键操作）"""
    # 认证失败 (1-10)
    LOGIN_FAILED = 3             # 登录失败（连续失败需要记录）
    
    # 越权操作 (31-50)
    UNAUTHORIZED_ACCESS = 32     # 未授权访问（尝试访问无权限的功能）
    ACCESS_OTHER_USER_DATA = 91  # 访问他人数据
    MODIFY_OTHER_USER_DATA = 92  # 修改他人数据
    DELETE_OTHER_USER_DATA = 93  # 删除他人数据
    
    # 非法操作 (71-90)
    ILLEGAL_PARAMETER = 71       # 非法参数
    INVALID_REQUEST = 76         # 无效请求


class SecurityLogLevel(IntEnum):
    """安全日志级别"""
    WARNING = 2   # 警告
    ERROR = 3     # 错误


async def log_security_event(
    action: LogAction,
    description: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    level: SecurityLogLevel = SecurityLogLevel.WARNING
):
    """
    记录安全事件（简化版 - 只记录到日志文件，不写数据库）
    
    Args:
        action: 操作类型
        description: 操作描述
        user_id: 用户ID
        request: FastAPI Request对象
        ip: IP地址
        user_agent: User-Agent
        level: 日志级别
    """
    try:
        # 从request中提取信息
        if request:
            if not ip:
                ip, _ = get_request_ip(request)
            if not user_agent:
                user_agent = request.headers.get('user-agent')
        
        # 只记录到日志文件（不写数据库，减少压力）
        log_message = f"[{action.name}] {description}"
        if user_id:
            log_message = f"用户={user_id} {log_message}"
        if ip:
            log_message = f"IP={ip} {log_message}"
        
        # 根据级别记录
        if level == SecurityLogLevel.WARNING:
            security_logger.warning(log_message)
        elif level == SecurityLogLevel.ERROR:
            security_logger.error(log_message)
            
    except Exception as e:
        security_logger.error(f"记录安全日志失败: {str(e)}")


async def log_unauthorized_access(
    resource: str,
    operation: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    required_role: Optional[str] = None,
    user_roles: Optional[list] = None
):
    """
    记录越权操作（重要 - 写入数据库）
    
    Args:
        resource: 资源名称
        operation: 操作类型
        user_id: 用户ID
        request: FastAPI Request对象
        required_role: 需要的角色
        user_roles: 用户当前角色
    """
    try:
        # 从request中提取信息
        ip = None
        user_agent = None
        if request:
            ip, _ = get_request_ip(request)
            user_agent = request.headers.get('user-agent')
        
        description = f"越权访问: 尝试{operation}资源[{resource}]"
        if required_role:
            description += f", 需要角色: {required_role}"
        if user_roles:
            description += f", 当前角色: {user_roles}"
        
        # 写入数据库（重要操作）
        await UserLog.create(
            user_id=user_id,
            action=LogAction.UNAUTHORIZED_ACCESS.value,
            description=description,
            ip=ip,
            user_agent=user_agent
        )
        
        # 同时记录到日志文件
        log_message = f"[UNAUTHORIZED_ACCESS] {description}"
        if user_id:
            log_message = f"用户={user_id} {log_message}"
        if ip:
            log_message = f"IP={ip} {log_message}"
        security_logger.warning(log_message)
        
    except Exception as e:
        security_logger.error(f"记录越权操作失败: {str(e)}")


async def log_data_access_violation(
    resource_type: str,
    resource_id: str,
    operation: str,
    user_id: Optional[UUID] = None,
    owner_id: Optional[UUID] = None,
    request: Optional[Request] = None
):
    """
    记录数据访问违规（重要 - 写入数据库）
    
    Args:
        resource_type: 资源类型
        resource_id: 资源ID
        operation: 操作类型
        user_id: 当前用户ID
        owner_id: 资源所有者ID
        request: FastAPI Request对象
    """
    try:
        # 从request中提取信息
        ip = None
        user_agent = None
        if request:
            ip, _ = get_request_ip(request)
            user_agent = request.headers.get('user-agent')
        
        description = f"数据访问违规: 尝试{operation}他人的{resource_type}[{resource_id}]"
        if owner_id:
            description += f", 所有者: {owner_id}"
        
        action_map = {
            'view': LogAction.ACCESS_OTHER_USER_DATA,
            'edit': LogAction.MODIFY_OTHER_USER_DATA,
            'update': LogAction.MODIFY_OTHER_USER_DATA,
            'delete': LogAction.DELETE_OTHER_USER_DATA,
        }
        
        action = action_map.get(operation.lower(), LogAction.ACCESS_OTHER_USER_DATA)
        
        # 写入数据库（重要操作）
        await UserLog.create(
            user_id=user_id,
            action=action.value,
            description=description,
            ip=ip,
            user_agent=user_agent
        )
        
        # 同时记录到日志文件
        log_message = f"[{action.name}] {description}"
        if user_id:
            log_message = f"用户={user_id} {log_message}"
        if ip:
            log_message = f"IP={ip} {log_message}"
        security_logger.error(log_message)
        
    except Exception as e:
        security_logger.error(f"记录数据访问违规失败: {str(e)}")


async def log_authentication_failure(
    email: str,
    reason: str,
    request: Optional[Request] = None,
    ip: Optional[str] = None
):
    """
    记录认证失败（只记录到日志文件，不写数据库）
    
    Args:
        email: 尝试登录的邮箱
        reason: 失败原因
        request: FastAPI Request对象
        ip: IP地址
    """
    try:
        if request and not ip:
            ip, _ = get_request_ip(request)
        
        # 只记录到日志文件
        log_message = f"[LOGIN_FAILED] 登录失败: {email}, 原因: {reason}"
        if ip:
            log_message = f"IP={ip} {log_message}"
        security_logger.warning(log_message)
        
    except Exception as e:
        security_logger.error(f"记录认证失败日志失败: {str(e)}")


async def log_invalid_parameter(
    parameter: str,
    value: any,
    reason: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None
):
    """
    记录非法参数（只记录到日志文件）
    
    Args:
        parameter: 参数名
        value: 参数值
        reason: 原因
        user_id: 用户ID
        request: FastAPI Request对象
    """
    try:
        ip = None
        if request:
            ip, _ = get_request_ip(request)
        
        # 只记录到日志文件
        log_message = f"[ILLEGAL_PARAMETER] 非法参数: {parameter}={value}, 原因: {reason}"
        if user_id:
            log_message = f"用户={user_id} {log_message}"
        if ip:
            log_message = f"IP={ip} {log_message}"
        security_logger.warning(log_message)
        
    except Exception as e:
        security_logger.error(f"记录非法参数失败: {str(e)}")


# 导出常用函数
__all__ = [
    'LogAction',
    'SecurityLogLevel',
    'log_security_event',
    'log_unauthorized_access',
    'log_data_access_violation',
    'log_authentication_failure',
    'log_invalid_parameter',
]
