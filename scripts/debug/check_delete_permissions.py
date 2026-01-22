#!/usr/bin/env python3
"""
检查所有删除接口的权限设置
确保只有管理员才能删除数据
"""

import os
import re
from pathlib import Path

# 管理员权限依赖
ADMIN_DEPENDENCIES = [
    'get_admin_user',
    'Depends(get_admin_user)',
]

# 普通用户权限依赖
USER_DEPENDENCIES = [
    'get_current_user',
    'Depends(get_current_user)',
]

def check_delete_routes():
    """检查所有删除路由的权限"""
    """检查所有删除路由的权限"""
    print("=" * 80)
    print("检查删除接口权限")
    print("=" * 80)
    print()
    
    api_files = []
    for root, dirs, files in os.walk('backend/app/apis'):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                api_files.append(Path(root) / file)
    
    print(f"找到 {len(api_files)} 个API文件")
    print()
    
    delete_routes = []
    
    for file_path in api_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找删除路由
        for i, line in enumerate(lines):
            if '@app.delete' in line:
                # 提取路径和描述
                path_match = re.search(r'["\']([^"\']*)["\']', line)
                path = path_match.group(1) if path_match else ''
                
                desc_match = re.search(r'summary\s*=\s*["\']([^"\']+)["\']', line)
                description = desc_match.group(1) if desc_match else ''
                
                # 读取函数定义
                func_lines = []
                found_func_def = False
                paren_count = 0
                
                for j in range(i+1, min(i+50, len(lines))):
                    func_lines.append(lines[j])
                    if 'async def' in lines[j]:
                        found_func_def = True
                        for char in lines[j]:
                            if char == '(':
                                paren_count += 1
                            elif char == ')':
                                paren_count -= 1
                    
                    if found_func_def:
                        for char in lines[j]:
                            if char == '(':
                                paren_count += 1
                            elif char == ')':
                                paren_count -= 1
                        
                        if paren_count == 0 and ')' in lines[j]:
                            if ':' in lines[j]:
                                break
                            if j + 1 < len(lines):
                                func_lines.append(lines[j+1])
                            break
                
                func_def = ''.join(func_lines)
                
                # 检查权限
                has_admin = any(dep in func_def for dep in ADMIN_DEPENDENCIES)
                has_user = any(dep in func_def for dep in USER_DEPENDENCIES)
                
                delete_routes.append({
                    'file': str(file_path),
                    'line': i + 1,
                    'path': path,
                    'description': description,
                    'has_admin': has_admin,
                    'has_user': has_user,
                    'func_def': func_def[:200]  # 只保留前200字符用于调试
                })
    
    print(f"找到 {len(delete_routes)} 个删除接口")
    print()
    
    # 分类
    admin_only = []
    user_access = []
    no_auth = []
    
    for route in delete_routes:
        if route['has_admin']:
            admin_only.append(route)
        elif route['has_user']:
            user_access.append(route)
        else:
            no_auth.append(route)
    
    # 打印结果
    print("-" * 80)
    print("统计结果:")
    print(f"  ✅ 仅管理员可删除: {len(admin_only)} 个")
    print(f"  ⚠️  普通用户可删除: {len(user_access)} 个")
    print(f"  ❌ 无认证保护: {len(no_auth)} 个")
    print("-" * 80)
    print()
    
    if admin_only:
        print("✅ 仅管理员可删除的接口:")
        print("-" * 80)
        for route in admin_only:
            print(f"  DELETE {route['path']:40} {route['description']}")
            print(f"         文件: {route['file']}:{route['line']}")
        print()
    
    if user_access:
        print("⚠️  普通用户可删除的接口（建议改为管理员权限）:")
        print("-" * 80)
        for route in user_access:
            print(f"  DELETE {route['path']:40} {route['description']}")
            print(f"         文件: {route['file']}:{route['line']}")
            print(f"         当前权限: get_current_user")
        print()
    
    if no_auth:
        print("❌ 无认证保护的删除接口（严重安全问题）:")
        print("-" * 80)
        for route in no_auth:
            print(f"  DELETE {route['path']:40} {route['description']}")
            print(f"         文件: {route['file']}:{route['line']}")
        print()
    
    # 总结
    print("=" * 80)
    if user_access or no_auth:
        print("⚠️  发现安全问题！")
        print()
        print("建议修复:")
        print("1. 将所有删除接口的权限改为 get_admin_user")
        print("2. 确保只有管理员才能删除数据")
        print()
        print("修改方法:")
        print("   将: current_user: dict = Depends(get_current_user)")
        print("   改为: admin_user: dict = Depends(get_admin_user)")
        return False
    else:
        print("✅ 所有删除接口都已正确配置管理员权限！")
        return True


if __name__ == '__main__':
    success = check_delete_routes()
    exit(0 if success else 1)
