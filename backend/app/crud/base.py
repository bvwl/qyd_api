from typing import Generic, Type, TypeVar, List, Dict, Any, Optional, Iterable
from uuid import UUID
from tortoise.models import Model
from tortoise.queryset import QuerySet

# 限定模型类型为 Tortoise Model
ModelType = TypeVar("ModelType", bound=Model)


class CRUDBase(Generic[ModelType]):
    """
    Tortoise ORM 通用 CRUD 基类

    设计目标：
    1. 封装常见的单表增删改查逻辑，减少重复代码
    2. 通过配置化的 QUERY_FIELD_RULES/QUERY_FIELD_MAP，统一处理常见的查询过滤
    3. 通过 RELATED_FIELDS 和钩子方法，为子类预留“关联字段处理”和“业务校验”的扩展点

    使用方式（子类通常只需要做三件事）：
    1. 设置 QUERY_FIELD_RULES：声明前端可用的查询参数，以及对应的查询类型（exact/contains/gte/...）
    2. 按需设置 QUERY_FIELD_MAP：将“查询参数名”映射到“模型字段名”（常用于 xxx_start/xxx_end 这类范围参数）
    3. 按需设置 RELATED_FIELDS/FETCH_RELATED_FIELDS/PREFETCH_RELATED_FIELDS，并重写钩子方法

    注意：
    - 基类只负责“单个模型”的通用逻辑，不承载复杂业务规则（如多表联查、状态机等）
    - 复杂业务条件（如邮箱 email_type 组合过滤）建议放在具体 CRUD 子类中实现
    """
    # 查询规则：查询参数名 -> 查询类型（exact/contains/gt 等）
    QUERY_FIELD_RULES: Dict[str, str] = {}
    # 关联字段映射：输入中的字段名 -> 模型上的关联属性名（如 group_id -> group）
    RELATED_FIELDS: Dict[str, str] = {}
    # 查询时需要一并加载的外键字段（如 group、country）
    FETCH_RELATED_FIELDS: Iterable[str] = ()
    # 查询时需要一并加载的多对多 / 反向关联字段
    PREFETCH_RELATED_FIELDS: Iterable[str] = ()
    # 查询参数到模型字段的映射（常用于时间范围：create_time_start -> create_time）
    QUERY_FIELD_MAP: Dict[str, str] = {}

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ========== 1. 通用查询构建（核心：关联预加载 + 条件过滤） ==========
    def _build_query(self, **kwargs) -> QuerySet[ModelType]:
        """
        构建查询集（自动预加载关联字段，并按 QUERY_FIELD_RULES/QUERY_FIELD_MAP 过滤）

        使用说明：
        - kwargs 中的 key 视为“查询参数名”，必须先在 QUERY_FIELD_RULES 中配置，否则会被忽略
        - 若 QUERY_FIELD_MAP 中存在对应项，则会先映射为模型字段名；否则直接使用参数名作为模型字段名
        例如：
        - QUERY_FIELD_RULES = {"email": "contains", "create_time_start": "gte"}
        - QUERY_FIELD_MAP = {"create_time_start": "create_time"}
        则传入 create_time_start=xxx 时，会生成过滤条件 create_time__gte=xxx
        """
        query = self.model.all()
        if self.FETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.FETCH_RELATED_FIELDS)
        if self.PREFETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.PREFETCH_RELATED_FIELDS)

        for field_name, value in kwargs.items():
            if field_name in self.QUERY_FIELD_RULES and value is not None:
                query_type = self.QUERY_FIELD_RULES[field_name]
                model_field = self.QUERY_FIELD_MAP.get(field_name, field_name)
                filter_key = f"{model_field}__{query_type}" if query_type != "exact" else model_field
                query = query.filter(**{filter_key: value})

        return query

    # ========== 2. 关联字段处理钩子（子类重写） ==========
    async def _handle_related_fields(self, db_obj: ModelType, related_data: Dict[str, Any], is_created: bool) -> None:
        """
        处理关联字段的创建/更新（子类重写实现具体逻辑）
        :param db_obj: 主模型对象
        :param related_data: 关联字段数据（如 {"role_id": 1, "tag_ids": [1,2]}）
        :param is_created: 是否是创建后
        """
        pass

    # ========== 3. 基础钩子（子类重写做校验） ==========
    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        pass

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: ModelType) -> None:
        pass

    async def _before_upsert(self, filter_kwargs: Dict[str, Any], obj_in: Dict[str, Any]) -> None:
        pass

    async def _after_upsert(self, db_obj: ModelType, is_created: bool) -> None:
        pass

    # ========== 4. 基础 CRUD 方法 ==========
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """创建数据（支持关联字段）"""
        # 分离普通字段/关联字段
        common_fields = {k: v for k, v in obj_in.items() if k not in self.RELATED_FIELDS}
        related_fields = {k: v for k, v in obj_in.items() if k in self.RELATED_FIELDS}

        # 前置校验
        await self._before_create(common_fields)
        # 创建主表数据
        db_obj = await self.model.create(**common_fields)
        if not db_obj:
            raise ValueError("创建数据失败")

        # 处理关联字段
        if related_fields:
            await self._handle_related_fields(db_obj, related_fields, is_created=True)

        # 预加载关联字段后返回（保证数据完整）
        query = self.model.get(id=db_obj.id)
        if self.FETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.FETCH_RELATED_FIELDS)
        if self.PREFETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.PREFETCH_RELATED_FIELDS)
        return await query

    async def get(self, id: UUID) -> Optional[ModelType]:
        """查询单条数据（自动预加载关联字段）"""
        query = self.model.get_or_none(id=id)
        if self.FETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.FETCH_RELATED_FIELDS)
        if self.PREFETCH_RELATED_FIELDS:
            query = query.prefetch_related(*self.PREFETCH_RELATED_FIELDS)
        return await query

    async def get_multi(
            self,
            page: int = 1,
            limit: int = 10,
            order_by: str = "-create_time", **kwargs,
    ) -> List[ModelType]:
        """
        分页查询（自动预加载关联字段）

        使用说明：
        - 常规字段过滤由 _build_query 完成（依赖 QUERY_FIELD_RULES/QUERY_FIELD_MAP）
        - order_by 支持 id/create_time 等模型字段及其降序（-create_time）
        - page/limit 控制分页
        """
        query = self._build_query(**kwargs)
        # 排序 + 分页
        query = query.order_by(order_by).limit(limit).offset((page - 1) * limit)
        return await query

    async def get_count(self, **kwargs) -> int:
        """
        统计符合条件的数据数量（不做关联预加载，以提升性能）

        使用说明：
        - 参数语义与 _build_query 一致：依赖 QUERY_FIELD_RULES/QUERY_FIELD_MAP
        - 适合配合列表查询一起使用，用于前端分页总数展示
        """
        query = self.model.all()
        for field_name, value in kwargs.items():
            if field_name in self.QUERY_FIELD_RULES and value is not None:
                query_type = self.QUERY_FIELD_RULES[field_name]
                model_field = self.QUERY_FIELD_MAP.get(field_name, field_name)
                filter_key = f"{model_field}__{query_type}" if query_type != "exact" else model_field
                query = query.filter(**{filter_key: value})
        return await query.count()

    async def update(
            self,
            id: UUID,
            update_data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """更新数据（支持关联字段）"""
        db_obj = await self.get(id)
        if not db_obj:
            raise ValueError("数据不存在")

        # 分离普通字段/关联字段
        common_fields = {k: v for k, v in update_data.items() if k not in self.RELATED_FIELDS}
        related_fields = {k: v for k, v in update_data.items() if k in self.RELATED_FIELDS}

        # 过滤普通字段 None 值
        filtered_common = {k: v for k, v in common_fields.items() if v is not None}
        if not filtered_common and not related_fields:
            raise ValueError("没有要更新的有效字段")

        # 更新普通字段
        if filtered_common:
            await self._before_update(id, filtered_common, db_obj)
            await db_obj.update_from_dict(filtered_common)
            await db_obj.save()

        # 处理关联字段
        if related_fields:
            await self._handle_related_fields(db_obj, related_fields, is_created=False)

        # 预加载关联字段后返回
        return await self.get(id)

    async def delete(self, id: UUID) -> bool:
        """删除数据"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        await db_obj.delete()
        return True

    async def upsert(
            self,
            filter_kwargs: Dict[str, Any],
            obj_in: Dict[str, Any]
    ) -> ModelType:
        """创建或更新（幂等操作，支持关联字段）"""
        if not filter_kwargs:
            raise ValueError("upsert 条件字段（filter_kwargs）不能为空")

        # 前置通用校验
        await self._before_upsert(filter_kwargs, obj_in)
        # 查询数据是否存在
        db_obj = await self.model.get_or_none(**filter_kwargs)
        is_created = False

        if db_obj:
            # 存在则更新
            await self.update(db_obj.id, obj_in)
        else:
            # 不存在则创建
            db_obj = await self.create(obj_in)
            is_created = True

        # 后置通用操作
        await self._after_upsert(db_obj, is_created)
        # 预加载关联字段后返回
        return await self.get(db_obj.id)
