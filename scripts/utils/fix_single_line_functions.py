#!/usr/bin/env python3
"""修复单行函数定义"""

import re

files_to_fix = [
    'backend/app/apis/v1/server/country.py',
    'backend/app/apis/v1/server/group.py',
    'backend/app/apis/v1/server/info.py',
    'backend/app/apis/v1/project/account.py',
    'backend/app/apis/v1/project/balance.py',
]

for file_path in files_to_fix:
    print(f"\n处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 模式1: async def func(param):
    def replace_single_param(match):
        func_name = match.group(1)
        params = match.group(2)
        full_match = match.group(0)
        
        # 检查是否已经有认证
        if 'get_current_user' in full_match or 'get_admin_user' in full_match:
            return full_match
        
        # 添加认证参数
        return f'{func_name}(\n    {params},\n    current_user: dict = Depends(get_current_user)\n):'
    
    pattern1 = r'(async def \w+)\(([^)]+)\):'
    content = re.sub(pattern1, replace_single_param, content)
    
    # 模式2: async def func():
    def replace_no_param(match):
        func_name = match.group(1)
        full_match = match.group(0)
        
        # 检查是否已经有认证
        if 'get_current_user' in full_match or 'get_admin_user' in full_match:
            return full_match
        
        # 添加认证参数
        return f'{func_name}(\n    current_user: dict = Depends(get_current_user)\n):'
    
    pattern2 = r'(async def \w+)\(\):'
    content = re.sub(pattern2, replace_no_param, content)
    
    # 保存文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 文件已更新: {file_path}")
    else:
        print(f"⊘ 文件无需更新: {file_path}")

print("\n" + "=" * 80)
print("完成！")
print("=" * 80)
