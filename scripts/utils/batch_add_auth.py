#!/usr/bin/env python3
"""
批量为所有API添加认证 - 最终版本
使用简单的字符串替换方法
"""

import os
import re
from pathlib import Path

# 白名单文件
WHITELIST_FILES = [
    'backend/app/apis/v1/user/auth.py',
]


def process_file(file_path: Path) -> int:
    """处理单个文件，返回修改的函数数量"""
    if str(file_path) in WHITELIST_FILES:
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified_count = 0
        
        # 1. 添加导入
        if 'from fastapi import' in content and ', Depends' not in content:
            content = content.replace(
                'from fastapi import',
                'from fastapi import Depends,'
            )
        
        if 'from app.core.verify import get_current_user' not in content:
            # 在第一个 app = APIRouter() 之前添加导入
            if 'app = APIRouter()' in content:
                content = content.replace(
                    'app = APIRouter()',
                    'from app.core.verify import get_current_user\n\napp = APIRouter()'
                )
        
        # 2. 为每个路由函数添加认证
        # 匹配单行函数定义
        patterns = [
            # 无参数的函数
            (r'(@app\.(get|post|put|delete|patch)\([^)]+\)\s*\nasync def (\w+)\(\s*\):)',
             r'\1\n    current_user: dict = Depends(get_current_user)\n):'),
            
            # 有参数的函数（单行）
            (r'(@app\.(get|post|put|delete|patch)\([^)]+\)\s*\nasync def (\w+)\(([^)]+)\):)',
             lambda m: m.group(1)[:-2] + ',\n    current_user: dict = Depends(get_current_user)\n):'),
        ]
        
        for pattern, replacement in patterns:
            matches = list(re.finditer(pattern, content))
            for match in reversed(matches):  # 从后往前替换，避免位置偏移
                func_def = match.group(0)
                # 检查是否已经有认证
                if 'get_current_user' in func_def or 'get_admin_user' in func_def:
                    continue
                
                if callable(replacement):
                    new_def = replacement(match)
                else:
                    new_def = re.sub(pattern, replacement, func_def)
                
                content = content[:match.start()] + new_def + content[match.end():]
                modified_count += 1
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return modified_count
        
        return 0
    
    except Exception as e:
        print(f"✗ 处理文件失败 {file_path}: {e}")
        return 0


def main():
    print("=" * 80)
    print("批量添加API认证")
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
    
    total_modified = 0
    modified_files = 0
    
    for file_path in sorted(api_files):
        count = process_file(file_path)
        if count > 0:
            print(f"✓ {file_path}: 修改了 {count} 个函数")
            total_modified += count
            modified_files += 1
    
    print()
    print("=" * 80)
    print(f"完成！修改了 {modified_files} 个文件，共 {total_modified} 个函数")
    print("=" * 80)


if __name__ == '__main__':
    main()
