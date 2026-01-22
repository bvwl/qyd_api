#!/usr/bin/env python3
"""调试account.py检测"""

import re

file_path = 'backend/app/apis/v1/project/account.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找gets函数
for i, line in enumerate(lines):
    if '@app.get("", response_model=OutList' in line:
        print(f"找到路由在第 {i+1} 行: {line.strip()}")
        
        # 读取函数定义
        func_lines = []
        found_func_def = False
        paren_count = 0
        
        for j in range(i+1, min(i+50, len(lines))):
            func_lines.append(lines[j])
            if 'async def' in lines[j]:
                found_func_def = True
                # 计算括号
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
        
        func_def = ''.join(func_lines)
        print(f"\n函数定义:\n{func_def}\n")
        
        # 检查认证
        AUTH_DEPENDENCIES = [
            'get_current_user',
            'get_admin_user',
            'get_gm_user',
        ]
        
        has_auth = any(dep in func_def for dep in AUTH_DEPENDENCIES)
        print(f"有认证: {has_auth}")
        
        break
