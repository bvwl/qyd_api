import uuid
from tortoise import fields
from tortoise.models import Model


# =======================
# 基础模型
# =======================

class BaseModel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, description='ID')
    create_time = fields.DatetimeField(auto_now_add=True, index=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True
