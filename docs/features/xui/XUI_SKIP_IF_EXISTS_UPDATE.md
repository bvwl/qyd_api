# XUI 添加账号逻辑优化 - 支持跳过已存在

## 问题描述

在"添加到所有入站"功能中,如果某个账号已经添加到某个入站,会抛出 400 错误,导致批量添加失败。

## 优化方案

### 1. 添加 `skip_if_exists` 参数

在 `add_account_to_inbound` 方法中添加可选参数 `skip_if_exists`:
- `True`: 如果账号已存在,跳过并返回成功
- `False`: 如果账号已存在,抛出 400 异常(默认行为)

### 2. 实现逻辑

#### 数据库层面
```python
# 检查是否已经关联
existing = await inbound.accounts.filter(id=account_id).exists()
if existing:
    if skip_if_exists:
        # 跳过已存在的关联,直接返回成功
        logger.info(f'账号已关联到入站,跳过: account={account.username}')
        return XuiInboundAccountOut(...)
    else:
        # 抛出异常
        raise HTTPException(status_code=400, detail='该账号已添加到此入站')
```

#### XUI 面板层面
XUI 客户端的 `add_user_to_inbound` 方法已经处理了用户已存在的情况:
```python
if user_account not in accounts:
    accounts.append(user_account)
else:
    logger.warning(f'用户已存在: {username}@{host}:{port}')
    return True  # 直接返回成功
```

### 3. 使用场景

#### 单个添加(不跳过)
```python
# 直接调用,不传 skip_if_exists 参数
await add_account_to_inbound(inbound_id, account_id)
# 如果已存在,抛出 400 异常
```

#### 批量添加(跳过已存在)
```python
# 传入 skip_if_exists=True
await add_account_to_inbound(inbound_id, account_id, skip_if_exists=True)
# 如果已存在,跳过并返回成功
```

## 更新的代码

### backend/app/crud/xui/user.py

#### 方法签名更新
```python
async def add_account_to_inbound(
    self, 
    inbound_id: UUID, 
    account_id: UUID, 
    skip_if_exists: bool = False  # 新增参数
) -> XuiInboundAccountOut:
```

#### 添加到所有入站
```python
async def add_account_to_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
    for inbound in inbounds:
        try:
            # 使用 skip_if_exists=True,跳过已存在的关联
            await self.add_account_to_inbound(
                inbound.id, 
                account_id, 
                skip_if_exists=True  # 关键参数
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
```

#### 从所有入站删除
```python
async def remove_account_from_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
    for inbound in inbounds:
        try:
            # 检查是否已经关联
            existing = await inbound.accounts.filter(id=account_id).exists()
            if not existing:
                # 如果未关联,视为成功(已经是删除状态)
                success_count += 1
                continue
            
            # 从入站删除
            await self.remove_account_from_inbound(inbound.id, account_id)
            success_count += 1
        except Exception as e:
            failed_count += 1
```

## 优化效果

### 优化前
```
添加账号到入站 A: 成功
添加账号到入站 B: 成功
添加账号到入站 C: 失败(已存在) ❌
添加账号到入站 D: 未执行(因为 C 失败)
添加账号到入站 E: 未执行(因为 C 失败)

结果: 失败,只添加了 2 个入站
```

### 优化后
```
添加账号到入站 A: 成功
添加账号到入站 B: 成功
添加账号到入站 C: 跳过(已存在) ✓
添加账号到入站 D: 成功
添加账号到入站 E: 成功

结果: 成功,添加了 5 个入站(其中 1 个跳过)
```

## 行为对比

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 单个添加(已存在) | 抛出 400 异常 | 抛出 400 异常(默认) |
| 单个添加(已存在,skip=True) | N/A | 跳过,返回成功 |
| 批量添加(部分已存在) | 失败,中断流程 | 跳过已存在,继续添加 |
| XUI 面板中已存在 | 返回成功 | 返回成功(不变) |

## 日志输出

### 跳过已存在的关联
```
INFO - 账号已关联到入站,跳过: account=user123, inbound=192.168.1.1:1080
```

### 正常添加
```
INFO - 添加用户到入站: user123@192.168.1.1:1080
```

## 兼容性

- ✅ 向后兼容: `skip_if_exists` 默认为 `False`,保持原有行为
- ✅ 单个添加: 不传参数,行为不变
- ✅ 批量添加: 传入 `skip_if_exists=True`,实现幂等性

## 测试建议

1. ✅ 测试单个添加(已存在,不跳过) - 应该抛出 400 异常
2. ✅ 测试单个添加(已存在,跳过) - 应该返回成功
3. ✅ 测试批量添加(部分已存在) - 应该跳过已存在,继续添加其他
4. ✅ 测试批量添加(全部已存在) - 应该全部跳过,返回成功
5. ✅ 测试 XUI 面板中已存在 - 应该返回成功

## 总结

通过添加 `skip_if_exists` 参数,实现了:
- ✅ 幂等性: 多次执行"添加到所有入站"不会报错
- ✅ 容错性: 部分入站已存在不影响其他入站的添加
- ✅ 兼容性: 保持原有 API 行为不变
- ✅ 灵活性: 可以根据场景选择是否跳过已存在

这样用户可以放心地多次点击"添加到所有入站"按钮,系统会自动跳过已存在的关联,只添加未关联的入站。
