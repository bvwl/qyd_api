from uuid import UUID
from fastapi import HTTPException

from app.models.project import ProjectWallet, ProjectInfo
from app.schemas.project.wallet import Create, Update, Out, OutList, BatchCreate, BatchCreateOut
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.clients.wallet import WalletClient
from app.core.tools import aes_encrypt_wallet


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        res = await ProjectWallet.create(**item.model_dump())
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('project')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('project')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        project_id: UUID | None = None,
                        chain: str | None = None,
                        public_key: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        user_project_ids: list[str] | None = None
                        ) -> OutList:
        query = ProjectWallet.all()
        
        # 数据权限过滤：如果指定了user_project_ids，只返回这些项目的钱包
        if user_project_ids is not None:
            if len(user_project_ids) == 0:
                # 用户没有关联任何项目，返回空列表
                return OutList(message='成功', count=0, num=0, items=[])
            query = query.filter(project_id__in=user_project_ids)
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        if chain:
            query = query.filter(chain__icontains=chain)
        
        if public_key:
            query = query.filter(public_key__icontains=public_key)
        
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(
                create_time_end, is_end=True))
        if update_time_start:
            query = query.filter(update_time__gte=parse_time(update_time_start))
        if update_time_end:
            query = query.filter(update_time__lte=parse_time(
                update_time_end, is_end=True))

        if order_by:
            query = query.order_by(order_by)

        if res_count:
            count = await query.count()
        else:
            count = -1

        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        
        # 预加载关联的项目信息
        res = await query.prefetch_related('project')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('project')
        
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新（根据公钥唯一性）
    async def upsert(self, item: Create) -> Out:
        record, created = await ProjectWallet.get_or_create(
            defaults=item.model_dump(),
            public_key=item.public_key
        )
        
        if not created:
            update_data = item.model_dump(exclude_unset=True)
            if update_data:
                await record.update_from_dict(update_data)
                await record.save()
        
        await record.fetch_related('project')
        return Out.model_validate(record)

    # 批量创建钱包
    async def batch_create(self, item: BatchCreate) -> BatchCreateOut:
        """
        批量创建钱包
        :param item: 批量创建参数
        :return: 创建的钱包列表
        """
        # 验证链类型并转换为大写
        chain_upper = item.chain.upper()
        if chain_upper not in ['ETH', 'SOL']:
            raise ValueError('链类型只支持 ETH 或 SOL')
        
        # 初始化钱包客户端
        wallet_client = WalletClient()
        
        # 批量创建钱包
        created_wallets = []
        for i in range(item.count):
            try:
                # 根据链类型创建钱包
                if chain_upper == 'ETH':
                    private_key, public_key, mnemonic = await wallet_client.eth_create()
                else:  # SOL
                    private_key, public_key, mnemonic = await wallet_client.solana_create()
                
                # 使用项目名称加密私钥和助记词
                encrypted_private_key = aes_encrypt_wallet(private_key, item.project_name)
                encrypted_mnemonic = aes_encrypt_wallet(mnemonic, item.project_name) if mnemonic else None
                
                # 创建钱包记录（使用大写链类型）
                wallet = await ProjectWallet.create(
                    private_key=encrypted_private_key,
                    public_key=public_key,
                    mnemonic=encrypted_mnemonic,
                    chain=chain_upper,
                    remark=item.remark
                )
                
                created_wallets.append(wallet)
                
            except Exception as e:
                # 如果某个钱包创建失败，记录错误但继续创建其他钱包
                print(f"创建第 {i+1} 个钱包失败: {str(e)}")
                continue
        
        if not created_wallets:
            raise HTTPException(status_code=500, detail='批量创建失败，没有成功创建任何钱包')
        
        # 手动构建输出数据（避免Pydantic验证关联字段）
        items = []
        for wallet in created_wallets:
            # 使用项目名称解密（因为前端需要明文显示）
            from app.core.tools import aes_decrypt_wallet
            
            # 构建字典，排除 project 字段
            wallet_dict = {
                'message': '成功',
                'id': wallet.id,
                'private_key': aes_decrypt_wallet(wallet.private_key, item.project_name),
                'public_key': wallet.public_key,
                'mnemonic': aes_decrypt_wallet(wallet.mnemonic, item.project_name) if wallet.mnemonic else None,
                'chain': wallet.chain,
                'remark': wallet.remark,
                'project_id': None,
                'create_time': wallet.create_time,
                'update_time': wallet.update_time,
            }
            items.append(Out(**wallet_dict))
        
        return BatchCreateOut(
            message=f'成功创建 {len(created_wallets)} 个钱包',
            count=len(created_wallets),
            items=items
        )


project_wallet_crud = CRUD()
