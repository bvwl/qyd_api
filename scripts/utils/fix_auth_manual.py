#!/usr/bin/env python3
"""
手动修复API认证 - 使用更可靠的方法
"""

import os
import re
from pathlib import Path

# 不需要认证的接口文件
WHITELIST_FILES = [
    'backend/app/apis/v1/user/auth.py',
]


def fix_file(file_path: Path) -> bool:
    """修复单个文件"""
    if str(file_path) in WHITELIST_FILES:
        print(f"⊘ 跳过白名单文件: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 确保有必要的导入
        if 'from fastapi import' in content and 'Depends' not in content:
            # 找到 fastapi 导入行并添加 Depends
            content = re.sub(
                r'(from fastapi import [^(\n]+)',
                r'\1, Depends',
                content,
                count=1
            )
        
        if 'from app.core.verify import' not in content or 'get_current_user' not in content:
            # 在导入区域添加 get_current_user
            # 找到最后一个 from app. 导入
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('from app.'):
                    insert_pos = i + 1
            
            if insert_pos > 0:
                lines.insert(insert_pos, 'from app.core.verify import get_current_user')
                content = '\n'.join(lines)
        
        # 2. 为每个路由函数添加认证参数
        # 匹配模式: @app.METHOD -> async def FUNC_NAME(params):
        pattern = r'(@app\.(get|post|put|delete|patch)\([^)]+\)\s*\n\s*async def \w+\([^)]*)\):'
        
        def add_auth_param(match):
            func_def = match.group(1)
            # 检查是否已经有认证参数
            if 'get_current_user' in func_def or 'get_admin_user' in func_def or 'get_gm_user' in func_def:
                return match.group(0)  # 已经有认证，不修改
            
            # 检查是否有其他参数
            if '(' in func_def and func_def.strip().endswith('('):
                # 没有参数
                return func_def + '\n    current_user: dict = Depends(get_current_user)\n):'
            else:
                # 有参数，添加逗号
                return func_def + ',\n    current_user: dict = Depends(get_current_user)\n):'
        
        content = re.sub(pattern, add_auth_param, content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 修改文件: {file_path}")
            return True
        
        return False
    
    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        return False


def main():
    print("=" * 80)
    print("手动修复API认证")
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
        if fix_file(file_path):
            modified_files += 1
    
    print()
    print("=" * 80)
    print(f"完成！修改了 {modified_files} 个文件")
    print("=" * 80)


if __name__ == '__main__':
    main()
