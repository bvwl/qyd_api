"""
Base CRUD class for common database operations.
This provides a simplified, consistent pattern across all CRUD modules.
"""
from typing import TypeVar, Generic, Type, Any
from uuid import UUID
from fastapi import HTTPException
from tortoise import Model
from pydantic import BaseModel

from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OutSchemaType = TypeVar("OutSchemaType", bound=BaseModel)
OutListSchemaType = TypeVar("OutListSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType, OutSchemaType, OutListSchemaType]):
    """
    基础CRUD类，提供标准的数据库操作方法
    
    使用方法:
    class CRUD(CRUDBase[Model, Create, Update, Out, OutList]):
        def __init__(self):
            super().__init__(
                model=Model,
                create_schema=Create,
                update_schema=Update,
                out_schema=Out,
                out_list_schema=OutList,
                related_fields=('field1', 'field2')
            )
    """
    
    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        out_schema: Type[OutSchemaType],
        out_list_schema: Type[OutListSchemaType],
        related_fields: tuple[str, ...] = (),
        unique_field: str | None = None,
        unique_error_msg: str = '数据已存在'
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.out_schema = out_schema
        self.out_list_schema = out_list_schema
        self.related_fields = related_fields
        self.unique_field = unique_field
        self.unique_error_msg = unique_error_msg

    async def _fetch_related(self, obj: ModelType) -> None:
        """获取关联字段"""
        if self.related_fields:
            await obj.fetch_related(*self.related_fields)

    async def _check_unique(self, value: Any, exclude_id: UUID | None = None) -> None:
        """检查唯一性约束"""
        if not self.unique_field:
            return
        
        query = self.model.filter(**{self.unique_field: value})
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        if await query.exists():
            raise HTTPException(status_code=400, detail=self.unique_error_msg)

    # 创建
    async def create(self, item: CreateSchemaType) -> OutSchemaType:
        data = item.model_dump()
        
        # 检查唯一性
        if self.unique_field and self.unique_field in data:
            await self._check_unique(data[self.unique_field])
        
        res = await self.model.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        
        await self._fetch_related(res)
        return self.out_schema.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> OutSchemaType:
        query = self.model.get_or_none(id=id)
        if self.related_fields:
            # 智能判断使用 select_related 还是 prefetch_related
            select_fields = [f for f in self.related_fields if '__' in f or not f.endswith('s')]
            prefetch_fields = [f for f in self.related_fields if f not in select_fields]
            
            if select_fields:
                query = query.select_related(*select_fields)
            if prefetch_fields:
                query = query.prefetch_related(*prefetch_fields)
        
        res = await query
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        await self._fetch_related(res)
        return self.out_schema.model_validate(res)

    # 条件查询
    async def get_multi(
        self,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False,
        order_by: str = '-create_time',
        **filters: Any
    ) -> OutListSchemaType:
        query = self.model.all()
        
        # 应用关联字段
        if self.related_fields:
            select_fields = [f for f in self.related_fields if '__' in f or not f.endswith('s')]
            prefetch_fields = [f for f in self.related_fields if f not in select_fields]
            
            if select_fields:
                query = query.select_related(*select_fields)
            if prefetch_fields:
                query = query.prefetch_related(*prefetch_fields)
        
        # 应用过滤条件
        for key, value in filters.items():
            if value is not None:
                if key.endswith('_start'):
                    field = key.replace('_start', '')
                    query = query.filter(**{f'{field}__gte': parse_time(value)})
                elif key.endswith('_end'):
                    field = key.replace('_end', '')
                    query = query.filter(**{f'{field}__lte': parse_time(value, is_end=True)})
                elif isinstance(value, str):
                    query = query.filter(**{f'{key}__icontains': value})
                else:
                    query = query.filter(**{key: value})
        
        # 排序
        if order_by:
            query = query.order_by(order_by)
        
        # 计数
        count = await query.count() if res_count else -1
        
        # 分页
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        res = await query
        num = len(res)
        
        # 获取关联字段
        for obj in res:
            await self._fetch_related(obj)
        
        items = [self.out_schema.model_validate(obj) for obj in res]
        return self.out_list_schema(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: UpdateSchemaType) -> OutSchemaType:
        res = await self.model.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        # 检查唯一性
        if self.unique_field and self.unique_field in update_data:
            await self._check_unique(update_data[self.unique_field], exclude_id=id)
        
        await res.update_from_dict(update_data)
        await res.save()
        await self._fetch_related(res)
        return self.out_schema.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await self.model.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: CreateSchemaType) -> OutSchemaType:
        if not self.unique_field:
            raise HTTPException(status_code=400, detail='该模型不支持upsert操作')
        
        data = item.model_dump()
        unique_value = data.get(self.unique_field)
        
        if not unique_value:
            raise HTTPException(status_code=400, detail=f'缺少唯一字段: {self.unique_field}')
        
        record, created = await self.model.get_or_create(
            defaults=data,
            **{self.unique_field: unique_value}
        )
        
        if not created:
            update_data = item.model_dump(exclude_unset=True)
            await record.update_from_dict(update_data)
            await record.save()
        
        await self._fetch_related(record)
        return self.out_schema.model_validate(record)
