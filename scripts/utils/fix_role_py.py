#!/usr/bin/env python3
"""修复role.py文件的认证"""

file_path = 'backend/app/apis/v1/user/role.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 添加导入
content = content.replace(
    'from fastapi import APIRouter, Query, Body, HTTPException, Path',
    'from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends'
)

content = content.replace(
    'from app.schemas.base import BaseOut',
    'from app.schemas.base import BaseOut\nfrom app.core.verify import get_current_user'
)

# 修改函数定义
replacements = [
    # post
    ('async def post(item: Create = Body(..., description="创建数据")):',
     'async def post(\n    item: Create = Body(..., description="创建数据"),\n    current_user: dict = Depends(get_current_user)\n):'),
    
    # get
    ('async def get(id: UUID = Path(..., description="ID")):',
     'async def get(\n    id: UUID = Path(..., description="ID"),\n    current_user: dict = Depends(get_current_user)\n):'),
    
    # put
    ('async def put(\n    id: UUID = Path(..., description="主键ID"),\n    item: Update = Body(..., description="更新数据"),\n):',
     'async def put(\n    id: UUID = Path(..., description="主键ID"),\n    item: Update = Body(..., description="更新数据"),\n    current_user: dict = Depends(get_current_user)\n):'),
    
    # delete
    ('async def delete(id: UUID = Path(..., description="主键ID")):',
     'async def delete(\n    id: UUID = Path(..., description="主键ID"),\n    current_user: dict = Depends(get_current_user)\n):'),
    
    # post_or_put
    ('async def post_or_put(item: Create = Body(..., description="创建或更新数据")):',
     'async def post_or_put(\n    item: Create = Body(..., description="创建或更新数据"),\n    current_user: dict = Depends(get_current_user)\n):'),
]

for old, new in replacements:
    content = content.replace(old, new)

# gets函数需要特殊处理（多行参数）
old_gets = '''@app.get("", response_model=OutList, description="获取角色列表", summary="获取角色列表")
async def gets(
    name: str | None = Query(None, description="角色名称"),
    code: str | None = Query(None, description="角色标识"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|code|create_time|update_time)$",
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
    update_time_start: str | int | None = Query(
        None,
        description="更新时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    update_time_end: str | int | None = Query(
        None,
        description="更新时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
):'''

new_gets = '''@app.get("", response_model=OutList, description="获取角色列表", summary="获取角色列表")
async def gets(
    name: str | None = Query(None, description="角色名称"),
    code: str | None = Query(None, description="角色标识"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|code|create_time|update_time)$",
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
    update_time_start: str | int | None = Query(
        None,
        description="更新时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    update_time_end: str | int | None = Query(
        None,
        description="更新时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):'''

content = content.replace(old_gets, new_gets)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ 修改完成: {file_path}")
