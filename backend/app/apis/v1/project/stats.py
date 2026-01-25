"""
项目统计API
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List

from app.schemas.project.stats import DashboardStatsOut, ProjectStatsTimeSeries
from app.crud.project.stats import project_stats_crud
from app.apis.deps import get_current_user
from app.core.database import db_read


app = APIRouter()


@app.get("/dashboard", response_model=DashboardStatsOut, description="获取仪表盘统计数据", summary="获取仪表盘统计数据")
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90, description="查询最近N天的数据"),
    project_ids: str | None = Query(None, description="项目ID列表，逗号分隔，不传则返回总和"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取仪表盘统计数据（项目账号更新数量曲线图）
    
    权限控制：
    - ADMIN/GM: 可以看到所有项目的统计数据
    - IT/MANUAL: 只能看到分配给自己的项目的统计数据
    
    参数说明：
    - days: 查询最近N天的数据
    - project_ids: 项目ID列表（逗号分隔），不传则返回所有项目的总和曲线
    
    返回数据格式：
    ```json
    {
        "code": 1,
        "message": "成功",
        "data": [
            {
                "project_id": "total",
                "project_name": "总计",
                "dates": ["2026-01-19", "2026-01-20", ..., "2026-01-25"],
                "counts": [10, 15, 20, 18, 25, 30, 28]
            }
        ]
    }
    ```
    
    如果传入project_ids，则返回指定项目的曲线：
    ```json
    {
        "code": 1,
        "message": "成功",
        "data": [
            {
                "project_id": "xxx",
                "project_name": "项目A",
                "dates": ["2026-01-19", ..., "2026-01-25"],
                "counts": [5, 8, 10, 9, 12, 15, 14]
            },
            {
                "project_id": "yyy",
                "project_name": "项目B",
                "dates": ["2026-01-19", ..., "2026-01-25"],
                "counts": [5, 7, 10, 9, 13, 15, 14]
            }
        ]
    }
    ```
    """
    try:
        from app.utils.data_permission import filter_by_user_projects
        
        # 获取用户ID
        user_id = current_user.get('user_id') or current_user.get('id')
        
        # 根据用户权限过滤项目
        user_project_ids = await filter_by_user_projects(user_id)
        
        # 解析请求的项目ID列表
        requested_project_ids = None
        if project_ids:
            requested_project_ids = [pid.strip() for pid in project_ids.split(',') if pid.strip()]
            
            # 权限检查：如果用户有项目限制，只能查看自己的项目
            if user_project_ids is not None:
                # 过滤掉用户没有权限的项目
                requested_project_ids = [
                    pid for pid in requested_project_ids 
                    if pid in user_project_ids
                ]
                if not requested_project_ids:
                    return DashboardStatsOut(
                        code=0,
                        message="没有权限访问指定的项目",
                        data=[]
                    )
        
        # 获取统计数据
        if requested_project_ids:
            # 用户指定了项目ID，返回这些项目的曲线
            stats_data = await project_stats_crud.get_project_stats_time_series(
                project_ids=requested_project_ids,
                days=days,
                use_cache=True
            )
        else:
            # 用户没有指定项目ID，返回总和曲线
            if user_project_ids is None:
                # ADMIN/GM：所有项目的总和
                stats_data = await project_stats_crud.get_total_stats_time_series(
                    project_ids=None,
                    days=days,
                    use_cache=True
                )
            elif len(user_project_ids) == 0:
                # 用户没有关联任何项目
                stats_data = []
            else:
                # IT/MANUAL：自己项目的总和
                stats_data = await project_stats_crud.get_total_stats_time_series(
                    project_ids=user_project_ids,
                    days=days,
                    use_cache=True
                )
        
        return DashboardStatsOut(
            code=1,
            message="成功",
            data=stats_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"获取统计数据失败: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@app.get("/project/{project_id}/today", description="获取项目今天的更新数量", summary="获取项目今天的更新数量")
async def get_project_today_count(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取项目今天的更新数量
    
    权限控制：
    - ADMIN/GM: 可以查看所有项目
    - IT/MANUAL: 只能查看分配给自己的项目
    """
    try:
        from app.utils.data_permission import filter_by_user_projects
        from uuid import UUID
        
        # 获取用户ID
        user_id = current_user.get('user_id') or current_user.get('id')
        
        # 根据用户权限过滤项目
        user_project_ids = await filter_by_user_projects(user_id)
        
        # 检查权限
        if user_project_ids is not None:
            if project_id not in user_project_ids:
                raise HTTPException(status_code=403, detail="没有权限访问该项目")
        
        # 获取今天的更新数量
        count = await project_stats_crud.get_today_update_count(UUID(project_id))
        
        return {
            "code": 1,
            "message": "成功",
            "data": {
                "project_id": project_id,
                "today_count": count
            }
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"项目ID格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@app.post("/cache/clear", description="清除统计缓存", summary="清除统计缓存")
async def clear_stats_cache(
    project_id: str | None = Query(None, description="项目ID，不传则清除所有缓存"),
    current_user: dict = Depends(get_current_user)
):
    """
    清除统计缓存（仅管理员可用）
    
    权限控制：
    - 仅 ADMIN 可以清除缓存
    """
    try:
        from app.utils.stats_cache import stats_cache
        
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        if 'ADMIN' not in user_roles:
            raise HTTPException(status_code=403, detail="只有管理员可以清除缓存")
        
        if project_id:
            # 清除指定项目的缓存
            success = await stats_cache.clear_project_cache(project_id)
            message = f"项目 {project_id} 的缓存已清除" if success else "清除缓存失败"
        else:
            # 清除所有统计缓存
            success = await stats_cache.clear_all_stats_cache()
            message = "所有统计缓存已清除" if success else "清除缓存失败"
        
        return {
            "code": 1 if success else 0,
            "message": message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")


@app.post("/sync", description="同步统计数据", summary="同步统计数据")
async def sync_stats(
    days: int = Query(1, ge=1, le=90, description="同步最近N天的数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    手动同步统计数据（仅管理员可用）
    
    权限控制：
    - 仅 ADMIN 可以同步数据
    
    说明：
    - 从 project_account 表统计更新数量，写入 project_daily_stats 表
    - 用于初始化或修复统计数据
    """
    try:
        from app.utils.stats_sync import sync_historical_stats
        
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        if 'ADMIN' not in user_roles:
            raise HTTPException(status_code=403, detail="只有管理员可以同步数据")
        
        # 同步数据
        synced_count = await sync_historical_stats(days=days)
        
        # 清除缓存
        from app.utils.stats_cache import stats_cache
        await stats_cache.clear_all_stats_cache()
        
        return {
            "code": 1,
            "message": f"同步完成，共同步 {synced_count} 条记录",
            "data": {
                "days": days,
                "synced_count": synced_count
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@app.get("/projects", description="获取可用项目列表", summary="获取可用项目列表")
async def get_available_projects(
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户可以查看统计数据的项目列表
    
    权限控制：
    - ADMIN/GM: 返回所有项目
    - IT/MANUAL: 返回分配给自己的项目
    
    返回数据格式：
    ```json
    {
        "code": 1,
        "message": "成功",
        "data": [
            {
                "id": "xxx",
                "name": "项目A"
            },
            {
                "id": "yyy",
                "name": "项目B"
            }
        ]
    }
    ```
    """
    try:
        from app.utils.data_permission import filter_by_user_projects
        from app.models.project import ProjectInfo
        
        # 获取用户ID
        user_id = current_user.get('user_id') or current_user.get('id')
        
        # 根据用户权限过滤项目
        user_project_ids = await filter_by_user_projects(user_id)
        
        # 获取项目列表
        if user_project_ids is None:
            # ADMIN/GM：所有项目
            projects = await db_read(ProjectInfo).all()
        elif len(user_project_ids) == 0:
            # 用户没有关联任何项目
            projects = []
        else:
            # IT/MANUAL：自己的项目
            projects = await db_read(ProjectInfo).filter(id__in=user_project_ids).all()
        
        # 构建返回数据
        project_list = [
            {
                'id': str(project.id),
                'name': project.name
            }
            for project in projects
        ]
        
        # 按项目名称排序
        project_list.sort(key=lambda x: x['name'])
        
        return {
            "code": 1,
            "message": "成功",
            "data": project_list
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")
