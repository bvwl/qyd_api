from datetime import datetime, timedelta
from loguru import logger
from fastapi import APIRouter, Body, HTTPException, Query, BackgroundTasks
from app.clients.outlook import AzureAuthManager
from app.schemas.mail.info import EmailType
from app.schemas.mail.outlook import AuthUrlOut, GetTokenIn, SendMailIn, GetEmailsIn, GetEmailsOut
from app.schemas.base import BaseOut
from app.crud.mail.info import email_info_crud
from app.utils.time_tool import parse_time, CN_TZ

app = APIRouter()


@app.get("/auth/url", response_model=AuthUrlOut, summary="获取授权URL", description="生成微软OAuth2授权URL和PKCE验证码")
async def get_auth_url(email: str = Query(..., description="邮箱地址")):
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
async def get_token(item: GetTokenIn = Body(..., description="获取Token参数")):
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
async def send_mail(item: SendMailIn = Body(..., description="发送邮件参数")):
    """
    发送邮件
    """
    try:
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
async def get_emails(item: GetEmailsIn = Body(..., description="获取邮件参数")):
    """
    获取邮件列表
    """
    try:
        manager = AzureAuthManager(item.email)
        res = await manager.get_emails_main(item.from_email, item.num, item.top)
        if res == 0:
            return GetEmailsOut(code=0, message="获取失败或无邮件", data=[])
        return GetEmailsOut(code=1, message="获取成功", data=res)
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
):
    if not any([ create_time_start, create_time_end, update_time_start, update_time_end]):
        return BaseOut(message="请选择时间范围")
    background_tasks.add_task(check_and_update_emails_logic, status, email_type, create_time_start, create_time_end,
                              update_time_start, update_time_end)
    return BaseOut(message="开始检查邮箱状态")


# 检测邮箱状态并更新
async def check_and_update_emails_logic(
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
) -> int:
    emails = await email_info_crud.get_multi(
        status=status,
        limit=10000,
        email_type=email_type,
        create_time_start=parse_time(create_time_start),
        create_time_end=parse_time(create_time_end, True),
        update_time_start=parse_time(update_time_start),
        update_time_end=parse_time(update_time_end, True),
    )
    for email in emails:
        manager = AzureAuthManager(email.email)
        res = await manager.get_emails_main('@', 1, 1)
        email.status = 4 if res == 0 else 1
        await email.save()
    return len(emails)


# 自动检查邮箱状态
async def auto_check_email_status(days: int = 15):
    """
    自动检查 N 天前未更新的正常邮箱状态
    """
    logger.info(f"开始自动检查邮箱状态，检查 {days} 天前未更新的邮箱")
    # 计算 N 天前的时间点，并转换为 13 位时间戳，便于统一解析
    check_time = datetime.now(CN_TZ) - timedelta(days=days)
    check_ts = int(check_time.timestamp() * 1000)
    await check_and_update_emails_logic(
        status=1,
        email_type=EmailType.IP_OK_TOKEN_OK,
        update_time_end=check_ts,
    )
