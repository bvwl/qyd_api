from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, Depends

from app.models.user import UserLog
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user
from app.utils.time_tool import parse_time
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


app = APIRouter()


class UserLogOut(BaseModel):
    """用户日志输出模型"""
    id: UUID
    user_id: Optional[UUID] = None
    action: int
    description: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    create_time: datetime
    
    class Config:
        from_attributes = True


class UserLogListOut(BaseModel):
    """用户日志列表输出"""
    message: str = "成功"
    count: int = -1
    num: int = 0
    items: list[UserLogOut] = []


@app.get("", response_model=UserLogListOut, description="获取用户日志列表", summary="获取用户日志列表")
async def gets(
    user_id: UUID | None = Query(None, description="用户ID"),
    action: int | None = Query(None, description="操作类型"),
    ip: str | None = Query(None, description="IP地址"),
    description: str | None = Query(None, description="操作描述（模糊搜索）"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|user_id|action|create_time)$",
    ),
    res_count: bool = Query(False, description="是否返回总数"),
    create_time_start: str | int | None = Query(
        None,
        description="创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    create_time_end: str | int | None = Query(
        None,
        description="创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    current_user: dict = Depends(get_admin_user)  # 只有管理员可以查看日志
):
    """
    分页查询用户日志列表（仅管理员）
    """
    try:
        query = UserLog.all()
        
        # 过滤条件
        if user_id:
            query = query.filter(user_id=user_id)
        if action is not None:
            query = query.filter(action=action)
        if ip:
            query = query.filter(ip__icontains=ip)
        if description:
            query = query.filter(description__icontains=description)
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
        
        # 排序
        if order_by:
            query = query.order_by(order_by)
        
        # 计数
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        # 分页
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        
        # 查询
        res = await query
        
        if not res:
            return UserLogListOut(message='未查询到数据', count=count, num=0, items=[])
        
        num = len(res)
        items = [UserLogOut.model_validate(obj) for obj in res]
        return UserLogListOut(message='成功', count=count, num=num, items=items)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/my", response_model=UserLogListOut, description="获取当前用户的日志", summary="获取我的日志")
async def get_my_logs(
    action: int | None = Query(None, description="操作类型"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|action|create_time)$",
    ),
    res_count: bool = Query(False, description="是否返回总数"),
    create_time_start: str | int | None = Query(
        None,
        description="创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    create_time_end: str | int | None = Query(
        None,
        description="创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    查询当前用户的操作日志
    """
    try:
        user_id = UUID(current_user["user_id"])
        query = UserLog.filter(user_id=user_id)
        
        # 过滤条件
        if action is not None:
            query = query.filter(action=action)
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
        
        # 排序
        if order_by:
            query = query.order_by(order_by)
        
        # 计数
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        # 分页
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        
        # 查询
        res = await query
        
        if not res:
            return UserLogListOut(message='未查询到数据', count=count, num=0, items=[])
        
        num = len(res)
        items = [UserLogOut.model_validate(obj) for obj in res]
        return UserLogListOut(message='成功', count=count, num=num, items=items)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/actions", response_model=dict, description="获取操作类型列表", summary="获取操作类型")
async def get_actions(current_user: dict = Depends(get_current_user)):
    """
    获取所有操作类型的枚举值和说明（简化版）
    """
    from app.utils.security_log import LogAction
    
    actions = {}
    name_map = {
        'LOGIN_FAILED': '登录失败',
        'UNAUTHORIZED_ACCESS': '未授权访问',
        'ACCESS_OTHER_USER_DATA': '访问他人数据',
        'MODIFY_OTHER_USER_DATA': '修改他人数据',
        'DELETE_OTHER_USER_DATA': '删除他人数据',
        'ILLEGAL_PARAMETER': '非法参数',
        'INVALID_REQUEST': '无效请求',
    }
    
    for action in LogAction:
        actions[action.value] = {
            'code': action.name,
            'name': name_map.get(action.name, action.name),
            'value': action.value
        }
    
    return {
        'message': '成功',
        'data': actions
    }


@app.delete("/{id}", response_model=BaseOut, description="删除日志", summary="删除日志")
async def delete(
    id: UUID,
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除日志（仅管理员）
    """
    try:
        log = await UserLog.get_or_none(id=id)
        if not log:
            raise HTTPException(status_code=404, detail='日志不存在')
        
        await log.delete()
        return BaseOut(message='成功', count=1)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
