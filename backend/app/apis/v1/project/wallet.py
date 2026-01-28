from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.wallet import Create, Update, Out, OutList, BatchCreate, BatchCreateOut
from app.crud.project.wallet import project_wallet_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user
from app.core.tools import aes_decrypt_wallet
from app.models.project import ProjectInfo


app = APIRouter()


@app.post("", response_model=Out, description="创建项目钱包", summary="创建项目钱包")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建项目钱包记录
    """
    try:
        return await project_wallet_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目钱包", summary="获取项目钱包")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个项目钱包记录
    
    注意：
    - 只有ADMIN角色可以查看解密后的私钥和助记词
    - 其他角色只能看到加密后的数据
    """
    try:
        obj = await project_wallet_crud.get(id)
        
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        
        # 如果是管理员，自动解密私钥和助记词
        if is_admin:
            try:
                # 使用公钥解密（每个钱包都有唯一的公钥）
                decrypted_private_key = aes_decrypt_wallet(obj.private_key, obj.public_key)
                obj.private_key = decrypted_private_key
                
                # 解密助记词（如果存在）
                if obj.mnemonic:
                    decrypted_mnemonic = aes_decrypt_wallet(obj.mnemonic, obj.public_key)
                    obj.mnemonic = decrypted_mnemonic
            except Exception as e:
                # 解密失败，返回加密数据
                print(f"解密失败: {str(e)}")
        
        return obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("", response_model=OutList, description="获取项目钱包列表", summary="获取项目钱包列表")
async def gets(
    project_id: UUID | None = Query(None, description="所属项目ID"),
    chain: str | None = Query(None, description="链名称"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|create_time|update_time)$",
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
):
    """
    分页查询项目钱包列表
    根据用户角色返回不同的数据：
    - ADMIN: 返回所有项目的钱包，并自动解密私钥和助记词
    - GM: 返回所有项目的钱包（加密状态）
    - IT/MANUAL: 只返回分配给该用户的项目的钱包（加密状态）
    """
    try:
        from app.utils.data_permission import filter_by_user_projects
        
        # 获取用户ID和角色
        user_id = current_user.get('user_id') or current_user.get('id')
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        
        # 根据用户权限过滤项目
        user_project_ids = await filter_by_user_projects(user_id)
        
        # 如果指定了project_id，需要检查用户是否有权限访问该项目
        if project_id and user_project_ids is not None:
            if str(project_id) not in user_project_ids:
                # 用户没有权限访问该项目
                return OutList(message='成功', count=0, num=0, items=[])
        
        result = await project_wallet_crud.get_multi(
            project_id=project_id,
            chain=chain,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
            user_project_ids=user_project_ids,
        )
        
        # 如果是管理员，自动解密所有钱包的私钥和助记词
        if is_admin:
            decrypted_items = []
            for item in result.items:
                try:
                    # 使用公钥解密（每个钱包都有唯一的公钥）
                    decrypted_private_key = aes_decrypt_wallet(item.private_key, item.public_key)
                    decrypted_mnemonic = None
                    if item.mnemonic:
                        decrypted_mnemonic = aes_decrypt_wallet(item.mnemonic, item.public_key)
                    
                    # 创建新的对象，包含解密后的数据
                    item_dict = item.model_dump()
                    item_dict['private_key'] = decrypted_private_key
                    if decrypted_mnemonic:
                        item_dict['mnemonic'] = decrypted_mnemonic
                    decrypted_items.append(Out(**item_dict))
                except Exception as e:
                    # 解密失败，保持加密状态
                    print(f"解密钱包 {item.id} 失败: {str(e)}")
                    decrypted_items.append(item)
            
            result.items = decrypted_items
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目钱包", summary="更新项目钱包")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目钱包，只更新传入的非空字段
    """
    try:
        return await project_wallet_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目钱包", summary="删除项目钱包")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除项目钱包（仅管理员）
    """
    try:
        return await project_wallet_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新项目钱包", summary="创建或更新项目钱包")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目钱包（根据公钥唯一性）
    
    如果公钥已存在，则更新该钱包信息；否则创建新钱包
    """
    try:
        return await project_wallet_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch", response_model=BatchCreateOut, description="批量创建钱包", summary="批量创建钱包")
async def batch_create(
    item: BatchCreate = Body(..., description="批量创建参数"),
    current_user: dict = Depends(get_current_user)
):
    """
    批量创建钱包（所有用户可用）
    
    功能说明：
    - 根据项目名称和链类型批量创建钱包
    - 私钥和助记词使用AES加密存储
    - 加密密钥：MD5(项目名称 + "9527")
    - 加密IV：MD5("9527" + 项目名称) 取前16位
    - 支持的链类型：ETH（以太坊）、SOL（Solana）
    - 创建数量限制：1-100个
    
    参数说明：
    - project_name: 项目名称（用于加密，不关联项目表）
    - chain: 链类型（ETH/SOL，大小写不敏感）
    - count: 创建数量（1-100）
    - remark: 备注信息（可选）
    
    返回说明：
    - 返回创建成功的钱包列表
    - 私钥和助记词已加密存储
    - 管理员查询时会自动解密
    """
    try:
        return await project_wallet_crud.batch_create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

