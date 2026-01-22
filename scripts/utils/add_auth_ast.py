#!/usr/bin/env python3
"""
使用AST正确添加认证参数
"""

import ast
import os
from pathlib import Path
from typing import List

# 白名单文件
WHITELIST_FILES = [
    'backend/app/apis/v1/user/auth.py',
]


def add_auth_to_file(file_path: Path) -> bool:
    """为文件中的所有路由函数添加认证参数"""
    if str(file_path) in WHITELIST_FILES:
        print(f"⊘ 跳过白名单文件: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_content = ''.join(lines)
        modified = False
        
        # 1. 添加必要的导入
        has_depends = False
        has_get_current_user = False
        fastapi_import_line = -1
        last_import_line = -1
        
        for i, line in enumerate(lines):
            if 'from fastapi import' in line:
                fastapi_import_line = i
                if 'Depends' in line:
                    has_depends = True
            if 'from app.core.verify import' in line and 'get_current_user' in line:
                has_get_current_user = True
            if line.startswith('from ') or line.startswith('import '):
                last_import_line = i
        
        # 添加 Depends 到 fastapi 导入
        if not has_depends and fastapi_import_line >= 0:
            line = lines[fastapi_import_line]
            if '(' not in line:  # 单行导入
                lines[fastapi_import_line] = line.rstrip() + ', Depends\n'
                modified = True
        
        # 添加 get_current_user 导入
        if not has_get_current_user and last_import_line >= 0:
            lines.insert(last_import_line + 1, 'from app.core.verify import get_current_user\n')
            modified = True
        
        # 2. 为每个路由函数添加认证参数
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 查找路由装饰器
            if line.strip().startswith('@app.') and any(method in line for method in ['.get(', '.post(', '.put(', '.delete(', '.patch(']):
                # 找到函数定义
                func_line_idx = i + 1
                while func_line_idx < len(lines) and 'async def' not in lines[func_line_idx]:
                    func_line_idx += 1
                
                if func_line_idx >= len(lines):
                    i += 1
                    continue
                
                # 找到函数参数的结束位置
                paren_count = 0
                start_idx = func_line_idx
                end_idx = func_line_idx
                found_open = False
                
                for j in range(func_line_idx, min(func_line_idx + 30, len(lines))):
                    for char in lines[j]:
                        if char == '(':
                            paren_count += 1
                            found_open = True
                        elif char == ')':
                            paren_count -= 1
                            if found_open and paren_count == 0:
                                end_idx = j
                                break
                    if end_idx > func_line_idx:
                        break
                
                if end_idx <= func_line_idx:
                    i += 1
                    continue
                
                # 检查是否已经有认证
                func_params = ''.join(lines[start_idx:end_idx+1])
                if 'get_current_user' in func_params or 'get_admin_user' in func_params or 'get_gm_user' in func_params:
                    i = end_idx + 1
                    continue
                
                # 添加认证参数
                # 找到 ) 的位置
                end_line = lines[end_idx]
                close_paren_pos = end_line.rfind(')')
                
                if close_paren_pos == -1:
                    i = end_idx + 1
                    continue
                
                # 检查是否有其他参数
                has_params = False
                for j in range(start_idx, end_idx + 1):
                    check_line = lines[j]
                    # 移除函数定义部分
                    if 'async def' in check_line:
                        check_line = check_line[check_line.index('(') + 1:]
                    # 检查是否有参数（不只是空格和括号）
                    clean_line = check_line.replace('(', '').replace(')', '').replace(':', '').strip()
                    if clean_line and not clean_line.startswith('#'):
                        has_params = True
                        break
                
                # 构建新的行
                if has_params:
                    # 有参数，添加逗号
                    new_line = end_line[:close_paren_pos] + ',\n    current_user: dict = Depends(get_current_user)\n' + end_line[close_paren_pos:]
                else:
                    # 没有参数
                    new_line = end_line[:close_paren_pos] + 'current_user: dict = Depends(get_current_user)' + end_line[close_paren_pos:]
                
                lines[end_idx] = new_line
                modified = True
                
                # 提取函数名用于日志
                func_name = lines[start_idx].split('def ')[1].split('(')[0].strip()
                print(f"  ✓ 添加认证到函数: {func_name}")
                
                i = end_idx + 1
                continue
            
            i += 1
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✓ 修改文件: {file_path}")
            return True
        
        return False
    
    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 80)
    print("使用AST方法添加API认证")
    print("=" * 80)
    print()
    
    # 查找所有API文件
    api_files = []
    for root, dirs, files in os.walk('backend/app/apis'):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                api_files.append(Path(root) / file)
    
    print(f"找到 {len(api_files)} 个API文件")
    print()
    
    modified_files = 0
    for file_path in sorted(api_files):
        if add_auth_to_file(file_path):
            modified_files += 1
        print()
    
    print("=" * 80)
    print(f"完成！修改了 {modified_files} 个文件")
    print("=" * 80)
    print()
    print("运行检测: python check_api_auth.py")


if __name__ == '__main__':
    main()
