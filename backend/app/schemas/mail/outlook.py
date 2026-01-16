from pydantic import BaseModel, Field
from typing import List


class AuthUrlOut(BaseModel):
    """
    授权URL输出模型
    """
    url: str = Field(..., description="授权URL")
    verifier: str = Field(..., description="PKCE 验证码")
    message: str = Field('成功', description='提示信息')


class GetTokenIn(BaseModel):
    """
    获取Token输入模型
    """
    email: str = Field(..., description="邮箱地址")
    url: str = Field(..., description="回调URL")
    verifier: str = Field(..., description="PKCE 验证码")


class SendMailIn(BaseModel):
    """
    发送邮件输入模型
    """
    email: str = Field(..., description="发件人邮箱")
    to_email: str = Field(..., description="收件人邮箱")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")
    content_type: str = Field("Text", description="内容类型: Text/HTML")


class GetEmailsIn(BaseModel):
    """
    获取邮件输入模型
    """
    email: str = Field(..., description="邮箱地址")
    from_email: str = Field(..., description="发件人筛选")
    num: int = Field(1, description="获取数量")
    top: int = Field(10, description="API查询数量")


class EmailItem(BaseModel):
    """
    邮件项模型
    """
    from_email: str | None = Field(None, description="发件人")
    title: str | None = Field(None, description="标题")
    content: str | None = Field(None, description="内容")


class GetEmailsOut(BaseModel):
    """
    获取邮件输出模型
    """
    message: str = Field('成功', description='提示信息')
    code: int = Field(..., description="状态码 1成功 0失败")
    data: List[EmailItem] | None = Field(None, description="邮件列表")
