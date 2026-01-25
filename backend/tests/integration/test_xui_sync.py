"""
测试 XUI 入站同步功能（包含端口过滤）
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, close_db
from app.crud.xui.operation import xui_operation_crud


async def test_sync_inbounds():
    """测试同步入站配置"""
    print("=" * 60)
    print("测试 XUI 入站同步功能（端口过滤）")
    print("=" * 60)
    
    # 初始化数据库
    await init_db()
    
    try:
        # 获取第一个 XUI 服务器
        from app.models.xui import XuiServer
        server = await XuiServer.first()
        
        if not server:
            print("❌ 未找到 XUI 服务器，请先创建服务器")
            return
        
        print(f"\n📡 服务器信息:")
        print(f"   ID: {server.id}")
        print(f"   名称: {server.name}")
        print(f"   地址: {server.domain or server.host}:{server.port}")
        
        # 同步入站配置
        print(f"\n🔄 开始同步入站配置...")
        print(f"   端口过滤规则:")
        print(f"   - 跳过 20000-21999 范围")
        print(f"   - 跳过 30000-31999 范围")
        
        result = await xui_operation_crud.sync_inbounds_from_panel(server.id)
        
        print(f"\n📊 同步结果:")
        print(f"   成功: {result.success}")
        print(f"   消息: {result.message}")
        
        if result.data:
            print(f"\n📈 详细统计:")
            print(f"   入站 - 创建: {result.data.get('inbound_created', 0)} 个")
            print(f"   入站 - 更新: {result.data.get('inbound_updated', 0)} 个")
            print(f"   入站 - 跳过: {result.data.get('inbound_skipped', 0)} 个")
            print(f"   服务器信息 - 创建: {result.data.get('server_info_created', 0)} 个")
            print(f"   服务器信息 - 更新: {result.data.get('server_info_updated', 0)} 个")
            
            errors = result.data.get('errors', [])
            if errors:
                print(f"\n⚠️  错误列表:")
                for error in errors:
                    print(f"   - {error}")
        
        # 查询同步后的入站列表
        from app.models.xui import XuiInbound
        inbounds = await XuiInbound.filter(server_id=server.id).all()
        
        print(f"\n📋 数据库中的入站列表 (共 {len(inbounds)} 个):")
        for inbound in inbounds:
            protocol_name = "HTTP" if inbound.protocol == 1 else "SOCKS"
            status_name = "正常" if inbound.status == 1 else "停用"
            print(f"   - {inbound.listen_host}:{inbound.listen_port} "
                  f"[{protocol_name}] [{status_name}] {inbound.remark or ''}")
        
        # 验证端口过滤
        print(f"\n✅ 端口过滤验证:")
        filtered_ports = [i.listen_port for i in inbounds 
                         if (20000 <= i.listen_port <= 21999) or (30000 <= i.listen_port <= 31999)]
        
        if filtered_ports:
            print(f"   ❌ 发现被过滤范围内的端口: {filtered_ports}")
        else:
            print(f"   ✅ 所有端口都不在过滤范围内")
        
        # 查询同步后的 ServerInfo 列表
        from app.models.server import ServerInfo, ServerGroup
        server_infos = await ServerInfo.all().prefetch_related('group')
        
        print(f"\n📋 ServerInfo 列表 (共 {len(server_infos)} 个):")
        for info in server_infos:
            group_name = info.group.name if info.group else '无分组'
            status_name = "正常" if info.status == 1 else "异常"
            print(f"   - {info.host}:{info.port} "
                  f"[分组: {group_name}] [{status_name}]")
        
        # 查询分组列表
        groups = await ServerGroup.all().prefetch_related('country')
        print(f"\n📋 ServerGroup 列表 (共 {len(groups)} 个):")
        for group in groups:
            country_name = group.country.name if group.country else '无国家'
            print(f"   - {group.name} (国家: {country_name})")
        
        print(f"\n✅ 测试完成！")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


async def test_port_filter_logic():
    """测试端口过滤逻辑"""
    print("\n" + "=" * 60)
    print("测试端口过滤逻辑")
    print("=" * 60)
    
    test_ports = [
        19999,  # 不过滤
        20000,  # 过滤
        20500,  # 过滤
        21999,  # 过滤
        22000,  # 不过滤
        29999,  # 不过滤
        30000,  # 过滤
        30500,  # 过滤
        31999,  # 过滤
        32000,  # 不过滤
    ]
    
    print("\n端口过滤测试:")
    for port in test_ports:
        should_skip = (20000 <= port <= 21999) or (30000 <= port <= 31999)
        status = "❌ 跳过" if should_skip else "✅ 导入"
        print(f"   端口 {port}: {status}")


if __name__ == '__main__':
    # 测试端口过滤逻辑
    asyncio.run(test_port_filter_logic())
    
    # 测试同步功能
    asyncio.run(test_sync_inbounds())
