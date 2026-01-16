import uuid
from tortoise import fields
from tortoise.models import Model


# 项目名称模型
class ProjectName(Model):
    """
    项目名称
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4, description='ID')
