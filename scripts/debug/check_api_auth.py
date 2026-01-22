#!/usr/bin/env python3
"""
检测后端所有API接口的认证状态
确保除了注册登录外，其他接口都需要JWT或Token认证
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# 不需要认证的接口（白名单）
WHITELIST_PATHS = [
    '/v1/user/auth/login',
    '/v1/user/auth/register',
]

# 认证依赖
AUTH_DEPENDENCIES = [
    'get_current_user',
    'get_admin_user',
    'get_gm_user',
    'Depends(get_current_user)',
    'Depends(get_admin_user)',
    'Depends(get_gm_user)',
]


def find_api_files(base_path: str = 'backend/app/apis') -> List[Path]:
    """查找所有API文件"""
    api_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                api_files.append(Path(root) / file)
    return api_files


def extract_routes(file_path: Path) -> List[Dict]:
    """从文件中提取所有路由定义"""
    routes = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 查找路由装饰器
    route_pattern = r'@app\.(get|post|put|delete|patch)\s*\('
    
    for i, line in enumerate(lines):
        match = re.search(route_pattern, line)
        if match:
            method = match.group(1).upper()
            
            # 提取路径
            path_match = re.search(r'["\']([^"\']+)["\']', line)
            path = path_match.group(1) if path_match else ''
            
            # 提取描述
            desc_match = re.search(r'summary\s*=\s*["\']([^"\']+)["\']', line)
            description = desc_match.group(1) if desc_match else ''
            
            # 检查函数定义（下一行或几行内，扩展到30行以覆盖多行参数）
            func_lines = []
            found_func_def = False
            paren_count = 0
            
            for j in range(i+1, min(i+30, len(lines))):
                func_lines.append(lines[j])
                if 'async def' in lines[j]:
                    found_func_def = True
                    # 计算括号，找到函数定义结束
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
                    
                    # 当括号平衡且遇到冒号时，函数定义结束
                    if paren_count == 0 and ')' in lines[j]:
                        # 继续读取直到找到冒号
                        if ':' in lines[j]:
                            break
                        # 或者读取下一行
                        if j + 1 < len(lines):
                            func_lines.append(lines[j+1])
                        break
            
            func_def = '\n'.join(func_lines)
            
            # 检查是否有认证依赖
            has_auth = any(dep in func_def for dep in AUTH_DEPENDENCIES)
            
            # 构建完整路径
            relative_path = str(file_path).replace('backend/app/apis', '')
            relative_path = relative_path.replace('.py', '').replace('\\', '/').replace('//', '/')
            
            # 构建API路径
            if relative_path.startswith('/v1/'):
                api_path = relative_path.replace('/v1/', '/v1/')
            else:
                api_path = relative_path
            
            # 如果path不为空，添加到api_path
            if path and path != '':
                if not path.startswith('/'):
                    api_path = api_path.rstrip('/') + '/' + path
                else:
                    api_path = api_path.rstrip('/') + path
            
            routes.append({
                'file': str(file_path),
                'method': method,
                'path': path,
                'api_path': api_path,
                'description': description,
                'has_auth': has_auth,
                'line': i + 1,
            })
    
    return routes


def check_auth_status():
    """检查所有API的认证状态"""
    print("=" * 80)
    print("后端API认证状态检测")
    print("=" * 80)
    print()
    
    api_files = find_api_files()
    print(f"找到 {len(api_files)} 个API文件")
    print()
    
    all_routes = []
    for file_path in api_files:
        routes = extract_routes(file_path)
        all_routes.extend(routes)
    
    print(f"找到 {len(all_routes)} 个API接口")
    print()
    
    # 分类统计
    with_auth = []
    without_auth = []
    whitelist = []
    
    for route in all_routes:
        # 检查是否在白名单中
        is_whitelist = False
        for wl_path in WHITELIST_PATHS:
            if wl_path in route['api_path'] or wl_path in route['path']:
                is_whitelist = True
                break
        
        if is_whitelist:
            whitelist.append(route)
        elif route['has_auth']:
            with_auth.append(route)
        else:
            without_auth.append(route)
    
    # 打印统计
    print("-" * 80)
    print(f"统计结果:")
    print(f"  ✅ 有认证保护: {len(with_auth)} 个")
    print(f"  ⚠️  无认证保护: {len(without_auth)} 个")
    print(f"  ℹ️  白名单接口: {len(whitelist)} 个")
    print("-" * 80)
    print()
    
    # 打印白名单接口
    if whitelist:
        print("白名单接口（不需要认证）:")
        print("-" * 80)
        for route in whitelist:
            print(f"  {route['method']:6} {route['api_path']:50} {route['description']}")
        print()
    
    # 打印无认证保护的接口（需要修复）
    if without_auth:
        print("⚠️  需要添加认证的接口:")
        print("-" * 80)
        for route in without_auth:
            print(f"  {route['method']:6} {route['api_path']:50}")
            print(f"         文件: {route['file']}:{route['line']}")
            print(f"         描述: {route['description']}")
            print()
        
        print("=" * 80)
        print(f"⚠️  发现 {len(without_auth)} 个接口没有认证保护！")
        print("=" * 80)
        print()
        print("建议修复方法:")
        print("1. 在函数参数中添加: current_user: dict = Depends(get_current_user)")
        print("2. 或使用管理员认证: admin_user: dict = Depends(get_admin_user)")
        print("3. 或使用GM认证: gm_user: dict = Depends(get_gm_user)")
        print()
        
        return False
    else:
        print("=" * 80)
        print("✅ 所有接口都已正确配置认证！")
        print("=" * 80)
        return True


if __name__ == '__main__':
    success = check_auth_status()
    exit(0 if success else 1)
