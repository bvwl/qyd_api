"""
项目提现 CRUD
"""
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException

from app.models.project import ProjectWithdrawal, ProjectInfo
from app.schemas.project.withdrawal import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    """项目提现 CRUD 操作"""
    
    def _calculate_change_and_history(
        self, 
        current_value: Decimal | None,
        new_value: Decimal | None,
        history: dict | None,
        decimal_places: int = 18
    ) -> tuple[Decimal, Decimal, dict]:
        """
        计算变动和更新历史记录
        
        Args:
            current_value: 当前值
            new_value: 新值
            history: 历史记录
            decimal_places: 小数位数
            
        Returns:
            (新值, 变动值, 更新后的历史记录)
        """
        if new_value is None:
            return current_value, Decimal(0), history
        
        # 获取当前时间戳（精确到秒）
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 初始化历史记录
        if history is None:
            history = {}
        
        # 计算变动
        if current_value is None:
            change = new_value
        else:
            change = new_value - current_value
        
        # 保留指定小数位数
        new_value = new_value.quantize(Decimal(10) ** -decimal_places)
        change = change.quantize(Decimal(10) ** -decimal_places)
        
        # 添加到历史记录（使用字符串保存，避免精度丢失）
        history[now] = str(new_value)
        
        return new_value, change, history
    
    async def create(self, item: Create) -> Out:
        """
        创建项目提现记录
        """
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=item.project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 检查是否已存在记录
        existing = await ProjectWithdrawal.get_or_none(project_id=item.project_id)
        if existing:
            raise HTTPException(status_code=400, detail='该项目已存在提现记录，请使用更新接口')
        
        # 准备数据
        create_data = {
            'project_id': item.project_id,
            'remark': item.remark,
        }
        
        # 处理平台币
        if item.platform_coin is not None:
            new_value, change, history = self._calculate_change_and_history(
                None, item.platform_coin, None, 18
            )
            create_data['platform_coin'] = new_value
            create_data['platform_coin_change'] = change
            create_data['platform_coin_history'] = history
        
        # 处理稳定币
        if item.stable_coin is not None:
            new_value, change, history = self._calculate_change_and_history(
                None, item.stable_coin, None, 18
            )
            create_data['stable_coin'] = new_value
            create_data['stable_coin_change'] = change
            create_data['stable_coin_history'] = history
        
        # 处理人民币
        if item.rmb is not None:
            new_value, change, history = self._calculate_change_and_history(
                None, item.rmb, None, 2
            )
            create_data['rmb'] = new_value
            create_data['rmb_change'] = change
            create_data['rmb_history'] = history
        
        # 创建记录
        res = await ProjectWithdrawal.create(**create_data)
        await res.fetch_related('project')
        
        return Out.model_validate(res)
    
    async def get(self, id: UUID) -> Out:
        """获取单条记录"""
        res = await ProjectWithdrawal.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        await res.fetch_related('project')
        return Out.model_validate(res)
    
    async def get_by_project(self, project_id: UUID) -> Out | None:
        """根据项目ID获取记录"""
        res = await ProjectWithdrawal.get_or_none(project_id=project_id)
        if not res:
            return None
        
        await res.fetch_related('project')
        return Out.model_validate(res)
    
    async def get_multi(
        self,
        project_id: UUID | None = None,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False,
        order_by: str = '-create_time',
        create_time_start: str | int | None = None,
        create_time_end: str | int | None = None,
        update_time_start: str | int | None = None,
        update_time_end: str | int | None = None,
        user_project_ids: list[str] | None = None,
    ) -> OutList:
        """条件查询"""
        query = ProjectWithdrawal.all()
        
        # 数据权限过滤
        if user_project_ids is not None:
            if len(user_project_ids) == 0:
                return OutList(message='成功', count=0, num=0, items=[])
            query = query.filter(project_id__in=user_project_ids)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
        if update_time_start:
            query = query.filter(update_time__gte=parse_time(update_time_start))
        if update_time_end:
            query = query.filter(update_time__lte=parse_time(update_time_end, is_end=True))
        
        if order_by:
            query = query.order_by(order_by)
        
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        
        res = await query.prefetch_related('project')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        
        return OutList(message='成功', count=count, num=num, items=items)
    
    async def update(self, id: UUID, item: Update) -> Out:
        """
        更新项目提现记录
        只更新传入的字段，自动计算变动和更新历史
        """
        res = await ProjectWithdrawal.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        await res.fetch_related('project')
        
        update_data = {}
        
        # 处理平台币
        if item.platform_coin is not None:
            new_value, change, history = self._calculate_change_and_history(
                res.platform_coin, item.platform_coin, res.platform_coin_history, 18
            )
            update_data['platform_coin'] = new_value
            update_data['platform_coin_change'] = change
            update_data['platform_coin_history'] = history
        
        # 处理稳定币
        if item.stable_coin is not None:
            new_value, change, history = self._calculate_change_and_history(
                res.stable_coin, item.stable_coin, res.stable_coin_history, 18
            )
            update_data['stable_coin'] = new_value
            update_data['stable_coin_change'] = change
            update_data['stable_coin_history'] = history
        
        # 处理人民币
        if item.rmb is not None:
            new_value, change, history = self._calculate_change_and_history(
                res.rmb, item.rmb, res.rmb_history, 2
            )
            update_data['rmb'] = new_value
            update_data['rmb_change'] = change
            update_data['rmb_history'] = history
        
        # 处理备注
        if item.remark is not None:
            update_data['remark'] = item.remark
        
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('project')
        
        return Out.model_validate(res)
    
    async def delete(self, id: UUID) -> BaseOut:
        """删除记录"""
        res = await ProjectWithdrawal.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        await res.delete()
        return BaseOut(message='成功', count=1)
    
    async def upsert(self, item: Create) -> Out:
        """
        创建或更新项目提现记录
        - 如果记录存在，只更新传入的非空字段
        - 如果记录不存在，创建新记录
        """
        # 查询现有记录
        existing = await ProjectWithdrawal.get_or_none(project_id=item.project_id)
        
        if existing:
            # 记录存在，更新
            await existing.fetch_related('project')
            
            update_data = {}
            
            # 处理平台币
            if item.platform_coin is not None:
                new_value, change, history = self._calculate_change_and_history(
                    existing.platform_coin, item.platform_coin, existing.platform_coin_history, 18
                )
                update_data['platform_coin'] = new_value
                update_data['platform_coin_change'] = change
                update_data['platform_coin_history'] = history
            
            # 处理稳定币
            if item.stable_coin is not None:
                new_value, change, history = self._calculate_change_and_history(
                    existing.stable_coin, item.stable_coin, existing.stable_coin_history, 18
                )
                update_data['stable_coin'] = new_value
                update_data['stable_coin_change'] = change
                update_data['stable_coin_history'] = history
            
            # 处理人民币
            if item.rmb is not None:
                new_value, change, history = self._calculate_change_and_history(
                    existing.rmb, item.rmb, existing.rmb_history, 2
                )
                update_data['rmb'] = new_value
                update_data['rmb_change'] = change
                update_data['rmb_history'] = history
            
            # 处理备注
            if item.remark is not None:
                update_data['remark'] = item.remark
            
            if update_data:
                await existing.update_from_dict(update_data)
                await existing.save()
            
            await existing.fetch_related('project')
            return Out.model_validate(existing)
        else:
            # 记录不存在，创建
            return await self.create(item)


project_withdrawal_crud = CRUD()
