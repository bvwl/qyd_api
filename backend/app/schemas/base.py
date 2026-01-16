from pydantic import BaseModel, Field


class BaseOut(BaseModel):
    """
    基础输出模型
    """
    message: str = Field('成功', description='提示信息')
    count: int = Field(1, description='总数')
