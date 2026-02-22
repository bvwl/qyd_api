from datetime import datetime, timedelta
from loguru import logger
from fastapi import APIRouter, Body, HTTPException, Query, BackgroundTasks, Depends
from app.clients.outlook import AzureAuthManager
from app.schemas.mail.info import EmailType
from app.schemas.mail.outlook import AuthUrlOut, GetTokenIn, SendMailIn, GetEmailsIn, GetEmailsOut
from app.schemas.base import BaseOut
from app.crud.mail.info import email_info_crud
from app.models.mail import EmailInfo
from app.utils.time_tool import parse_time, CN_TZ
from app.apis.deps import get_current_user
from app.utils.logs import getLogger

# 使用 scheduler 日志记录器用于定时任务
scheduler_logger = getLogger('scheduler')

app = APIRouter()


async def check_rate_limit(email: str, operation: str = "操作") -> None:
    """
    检查邮箱操作频率限制
    30秒内只能执行一次操作
    
    Args:
        email: 邮箱地址
        operation: 操作名称（用于错误提示）
        
    Raises:
        HTTPException: 如果操作过于频繁
    """
    email_info = await EmailInfo.get_or_none(email=email)
    if not email_info:
        raise HTTPException(status_code=404, detail=f"邮箱 {email} 不存在")
    
    # 检查更新时间
    now = datetime.now(CN_TZ)
    if email_info.update_time:
        # 确保 update_time 有时区信息
        update_time = email_info.update_time
        if update_time.tzinfo is None:
            update_time = update_time.replace(tzinfo=CN_TZ)
        else:
            update_time = update_time.astimezone(CN_TZ)
        
        time_diff = (now - update_time).total_seconds()
        
        if time_diff < 30:
            remaining = 30 - int(time_diff)
            raise HTTPException(
                status_code=400, 
                detail=f"{operation}过于频繁，请在 {remaining} 秒后重试"
            )
    
    # 更新时间戳
    await EmailInfo.filter(email=email).update(update_time=now)


@app.get("/auth/url", response_model=AuthUrlOut, summary="获取授权URL", description="生成微软OAuth2授权URL和PKCE验证码")
async def get_auth_url(
    email: str = Query(..., description="邮箱地址"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取微软授权URL
    """
    try:
        manager = AzureAuthManager(email)
        url, verifier = await manager.generate_auth_url()
        return AuthUrlOut(url=url, verifier=verifier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/token", response_model=BaseOut, summary="获取Token", description="使用授权回调URL获取Access Token")
async def get_token(
    item: GetTokenIn = Body(..., description="获取Token参数"),
    current_user: dict = Depends(get_current_user)
):
    """
    使用回调URL获取Token
    """
    try:
        manager = AzureAuthManager(item.email)
        res = await manager.get_token_main(item.url, item.verifier)
        if res:
            return BaseOut(message="获取Token成功")
        raise HTTPException(status_code=400, detail="获取Token失败")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send", response_model=BaseOut, summary="发送邮件", description="使用Outlook API发送邮件")
async def send_mail(
    item: SendMailIn = Body(..., description="发送邮件参数"),
    current_user: dict = Depends(get_current_user)
):
    """
    发送邮件
    30秒内只能发送一次
    """
    try:
        # 检查频率限制
        await check_rate_limit(item.email, "发送邮件")
        
        manager = AzureAuthManager(item.email)
        res = await manager.send_email_main(item.to_email, item.subject, item.content, item.content_type)
        if res:
            return BaseOut(message="发送成功")
        raise HTTPException(status_code=400, detail="发送失败")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages", response_model=GetEmailsOut, summary="获取邮件", description="获取收件箱中指定发件人的邮件")
async def get_emails(
    item: GetEmailsIn = Body(..., description="获取邮件参数"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取邮件列表
    30秒内只能获取一次
    """
    try:
        # 检查频率限制
        await check_rate_limit(item.email, "获取邮件")
        
        manager = AzureAuthManager(item.email)
        res = await manager.get_emails_main(item.from_email, item.num, item.top)
        if res == 0:
            return GetEmailsOut(code=0, message="获取失败或无邮件", data=[])
        return GetEmailsOut(code=1, message="获取成功", data=res)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 检查时间段内邮箱的状态
@app.get("/check", response_model=BaseOut, summary="检查邮箱状态", description="检查时间段内邮箱的状态")
async def check_email_status(
        background_tasks: BackgroundTasks,
        status: int | None = Query(None, description='状态(1:正常,4:异常)'),
        email_type: EmailType | None = Query(None, description='邮箱类型'),
        create_time_start: str | int | None = Query(
            None, description='创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        create_time_end: str | int | None = Query(
            None, description='创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        update_time_start: str | int | None = Query(
            None, description='更新时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        update_time_end: str | int | None = Query(
            None, description='更新时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        current_user: dict = Depends(get_current_user)
):
    if not any([ create_time_start, create_time_end, update_time_start, update_time_end]):
        return BaseOut(message="请选择时间范围")
    background_tasks.add_task(check_and_update_emails_logic, status, email_type, create_time_start, create_time_end,
                              update_time_start, update_time_end)
    return BaseOut(message="开始检查邮箱状态")


# 检测邮箱状态并更新
async def check_and_update_emails_logic(
        status: int | None = None,
        email_type: EmailType | None = None,
        create_time_start: str | int | None = None,
        create_time_end: str | int | None = None,
        update_time_start: str | int | None = None,
        update_time_end: str | int | None = None,
) -> int:
    """
    分批检测邮箱状态并更新
    使用分页方式避免一次性查询过多数据导致内存问题
    
    防封号策略：
    1. 打乱邮箱处理顺序（避免按固定顺序访问）
    2. 添加随机延迟（模拟人工操作）
    3. 批量处理（减少数据库查询）
    """
    import random
    import asyncio
    import os
    
    batch_size = 10  # 每批处理10条，避免一次性处理过多
    page = 1
    total_checked = 0
    
    # 从环境变量读取延迟配置（防封号）
    email_check_delay_min = float(os.getenv("EMAIL_CHECK_DELAY_MIN", "2.0"))  # 最小延迟（秒）
    email_check_delay_max = float(os.getenv("EMAIL_CHECK_DELAY_MAX", "5.0"))  # 最大延迟（秒）
    batch_delay_min = float(os.getenv("EMAIL_BATCH_DELAY_MIN", "5.0"))  # 批次间最小延迟（秒）
    batch_delay_max = float(os.getenv("EMAIL_BATCH_DELAY_MAX", "10.0"))  # 批次间最大延迟（秒）
    
    scheduler_logger.info(f"开始检查邮箱状态，条件: status={status}, email_type={email_type}, "
                f"create_time: {create_time_start} ~ {create_time_end}, "
                f"update_time: {update_time_start} ~ {update_time_end}")
    scheduler_logger.info(f"防封号配置: 邮箱间延迟 {email_check_delay_min}-{email_check_delay_max}秒, "
                f"批次间延迟 {batch_delay_min}-{batch_delay_max}秒")
    
    while True:
        try:
            # 分批查询
            scheduler_logger.debug(f"正在查询第 {page} 页，每页 {batch_size} 条...")
            result = await email_info_crud.get_multi(
                status=status,
                page=page,
                limit=batch_size,
                email_type=email_type,
                create_time_start=create_time_start,
                create_time_end=create_time_end,
                update_time_start=update_time_start,
                update_time_end=update_time_end,
            )
            
            emails = result.items
            if not emails:
                scheduler_logger.debug(f"第 {page} 页没有数据，结束检查")
                break
            
            scheduler_logger.debug(f"第 {page} 页获取到 {len(emails)} 个邮箱，开始检查...")
            
            # 🔥 防封号优化1: 打乱邮箱处理顺序
            emails_list = list(emails)
            random.shuffle(emails_list)
            scheduler_logger.debug(f"已打乱邮箱处理顺序（防止按固定顺序访问）")
            
            # 处理当前批次
            for idx, email in enumerate(emails_list, 1):
                try:
                    # 记录邮箱的 IP 和 Token 状态
                    has_ip = email.server_id is not None
                    has_token = email.access_token is not None
                    scheduler_logger.debug(f"检查邮箱 {email.email} ({idx}/{len(emails_list)}): has_ip={has_ip}, has_token={has_token}")
                    
                    manager = AzureAuthManager(email.email)
                    res = await manager.get_emails_main('@', 1, 1)
                    new_status = 2 if res == 0 else 1  # 2=异常, 1=正常
                    
                    # 只在状态变化时更新
                    if email.status != new_status:
                        await EmailInfo.filter(id=email.id).update(status=new_status)
                        scheduler_logger.info(f"邮箱 {email.email} 状态更新: {email.status} -> {new_status}")
                    
                    total_checked += 1
                    
                    # 🔥 防封号优化2: 添加随机延迟（模拟人工操作）
                    if idx < len(emails_list):  # 最后一个不需要延迟
                        delay = random.uniform(email_check_delay_min, email_check_delay_max)
                        scheduler_logger.debug(f"随机延迟 {delay:.2f} 秒（防止频繁请求）")
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    scheduler_logger.warning(f"检查邮箱 {email.email} 失败: {str(e)}")
                    continue
            
            # 如果返回的数量少于批次大小，说明已经是最后一批
            if len(emails) < batch_size:
                scheduler_logger.debug(f"第 {page} 页返回 {len(emails)} 条（少于 {batch_size}），这是最后一批")
                break
            
            # 🔥 防封号优化3: 批次之间添加更长的随机延迟
            batch_delay = random.uniform(batch_delay_min, batch_delay_max)
            scheduler_logger.debug(f"第 {page} 页处理完成，批次间延迟 {batch_delay:.2f} 秒...")
            await asyncio.sleep(batch_delay)
            
            page += 1
            
        except HTTPException as e:
            # 404 表示没有更多数据
            if e.status_code == 404:
                scheduler_logger.debug(f"第 {page} 页查询返回404，没有更多数据")
                break
            raise
        except Exception as e:
            scheduler_logger.error(f"批量检查邮箱状态失败: {str(e)}", exc_info=True)
            break
    
    scheduler_logger.info(f"邮箱状态检查完成，共检查 {total_checked} 个邮箱")
    return total_checked


# 自动检查邮箱状态
async def auto_check_email_status(days: int = 15):
    """
    自动检查 N 天前未更新的正常邮箱状态
    """
    import time
    start_time = time.time()
    
    scheduler_logger.info(f"开始自动检查邮箱状态，检查 {days} 天前未更新的邮箱")
    
    # 计算 N 天前的时间点，并转换为 13 位时间戳，便于统一解析
    check_time = datetime.now(CN_TZ) - timedelta(days=days)
    check_ts = int(check_time.timestamp() * 1000)
    
    total_checked = await check_and_update_emails_logic(
        status=1,
        email_type=EmailType.IP_OK_TOKEN_OK,
        update_time_end=check_ts,
    )
    
    elapsed = time.time() - start_time
    scheduler_logger.info(
        f"邮箱状态检查完成，共检查 {total_checked} 个邮箱，"
        f"耗时 {elapsed:.2f} 秒"
    )
