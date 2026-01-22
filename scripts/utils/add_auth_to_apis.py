#!/usr/bin/env python3
"""
自动为所有API接口添加JWT认证
除了注册和登录接口外，其他接口都添加 current_user 依赖
"""

import os
import re
from pathlib import Path

# 不需要认证的接口文件和函数
WHITELIST = {
    'backend/app/apis/v1/user/auth.py': ['register', 'login'],
}

def should_skip_file(file_path: str) -> bool:
    """检查文件是否应该跳过"""
    return file_path in WHITELIST


def should_skip_function(file_path: str, func_name: str) -> bool:
    """检查函数是否应该跳过"""
    if file_path in WHITELIST:
        return func_name in WHITELIST[file_path]
    return False


def add_auth_import(content: str) -> tuple[str, bool]:
    """添加认证相关的导入"""
    lines = content.split('\n')
    
    # 检查是否已经有导入
    has_depends = any('from fastapi import' in line and 'Depends' in line for line in lines)
    has_get_current_user = any('from app.core.verify import' in line and 'get_current_user' in line for line in lines)
    
    if has_depends and has_get_current_user:
        return content, False
    
    # 找到合适的位置插入导入
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('from fastapi import'):
            # 在现有的 fastapi 导入中添加 Depends
            if not has_depends and 'Depends' not in line:
                # 添加 Depends 到导入列表
                if '(' in line:
                    # 多行导入
                    lines[i] = line.replace(')', ', Depends)')
                else:
                    # 单行导入
                    lines[i] = line.rstrip() + ', Depends'
                has_depends = True
            insert_pos = i + 1
        elif line.startswith('from app.'):
            insert_pos = i + 1
    
    # 添加 get_current_user 导入
    if not has_get_current_user:
        import_line = 'from app.core.verify import get_current_user'
        lines.insert(insert_pos, import_line)
    
    return '\n'.join(lines), True


def add_auth_to_function(content: str, file_path: str) -> tuple[str, int]:
    """为函数添加认证参数"""
    lines = content.split('\n')
    modified_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 查找路由装饰器
        if re.match(r'@app\.(get|post|put|delete|patch)', line):
            # 找到对应的函数定义
            func_start = i + 1
            while func_start < len(lines) and 'async def' not in lines[func_start]:
                func_start += 1
            
            if func_start >= len(lines):
                i += 1
                continue
            
            # 提取函数名
            func_match = re.search(r'async def (\w+)', lines[func_start])
            if not func_match:
                i += 1
                continue
            
            func_name = func_match.group(1)
            
            # 检查是否应该跳过
            if should_skip_function(file_path, func_name):
                i = func_start + 1
                continue
            
            # 找到函数参数的结束位置
            param_end = func_start
            paren_count = 0
            found_open = False
            
            for j in range(func_start, min(func_start + 30, len(lines))):
                for char in lines[j]:
                    if char == '(':
                        paren_count += 1
                        found_open = True
                    elif char == ')':
                        paren_count -= 1
                        if found_open and paren_count == 0:
                            param_end = j
                            break
                if param_end > func_start:
                    break
            
            if param_end <= func_start:
                i += 1
                continue
            
            # 检查函数是否已经有认证
            func_params = '\n'.join(lines[func_start:param_end+1])
            if 'get_current_user' in func_params or 'get_admin_user' in func_params or 'get_gm_user' in func_params:
                # 已经有认证，跳过
                i = param_end + 1
                continue
            
            # 需要添加认证
            # 在参数列表末尾添加认证参数
            line_content = lines[param_end]
            
            # 找到 ) 的位置
            close_paren_pos = line_content.rfind(')')
            if close_paren_pos == -1:
                i = param_end + 1
                continue
            
            # 检查括号前是否有参数
            has_params = False
            for j in range(func_start, param_end + 1):
                # 检查是否有参数（排除空格和括号）
                check_line = lines[j].replace('async def ' + func_name, '').strip()
                if check_line and check_line not in ['(', ')', '()', ':']:
                    # 检查是否有实际参数（不只是括号）
                    if any(c.isalnum() or c == '_' for c in check_line):
                        has_params = True
                        break
            
            # 构建插入文本
            if has_params:
                # 有参数，添加逗号
                insert_text = ',\n    current_user: dict = Depends(get_current_user)'
            else:
                # 没有参数，不添加逗号
                insert_text = '\n    current_user: dict = Depends(get_current_user)'
            
            # 插入认证参数
            lines[param_end] = line_content[:close_paren_pos] + insert_text + '\n' + line_content[close_paren_pos:]
            
            modified_count += 1
            print(f"  ✓ 添加认证到函数: {func_name}")
            
            i = param_end + 1
            continue
        
        i += 1
    
    return '\n'.join(lines), modified_count


def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    if should_skip_file(str(file_path)):
        print(f"⊘ 跳过白名单文件: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 添加导入
        content, import_modified = add_auth_import(content)
        
        # 添加认证到函数
        content, func_count = add_auth_to_function(content, str(file_path))
        
        if content != original_content:
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 修改文件: {file_path}")
            if import_modified:
                print(f"  - 添加了导入")
            if func_count > 0:
                print(f"  - 修改了 {func_count} 个函数")
            return True
        
        return False
    
    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        return False


def main():
    print("=" * 80)
    print("自动添加API认证")
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
    for file_path in api_files:
        if process_file(file_path):
            modified_files += 1
        print()
    
    print("=" * 80)
    print(f"完成！修改了 {modified_files} 个文件")
    print("=" * 80)
    print()
    print("建议:")
    print("1. 运行 python check_api_auth.py 检查修复结果")
    print("2. 测试所有API接口确保正常工作")
    print("3. 检查是否有需要特殊权限的接口（如管理员权限）")


if __name__ == '__main__':
    main()
