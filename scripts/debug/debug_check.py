#!/usr/bin/env python3
"""调试检测脚本"""

import re

file_path = 'backend/app/apis/v1/mail/outlook.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找第一个路由
route_pattern = r'@app\.(get|post|put|delete|patch)\s*\('

for i, line in enumerate(lines):
    match = re.search(route_pattern, line)
    if match:
        print(f"找到路由在第 {i+1} 行: {line.strip()}")
        
        # 读取函数定义
        func_lines = []
        for j in range(i+1, min(i+30, len(lines))):
            func_lines.append(lines[j])
            if 'async def' in lines[j]:
                # 继续读取直到找到函数体开始
                for k in range(j+1, min(j+20, len(lines))):
                    func_lines.append(lines[k])
                    if ':' in lines[k] and not lines[k].strip().startswith('#'):
                        break
                break
        
        func_def = ''.join(func_lines)
        print(f"\n函数定义:\n{func_def}\n")
        
        # 检查认证
        AUTH_DEPENDENCIES = [
            'get_current_user',
            'get_admin_user',
            'get_gm_user',
            'Depends(get_current_user)',
            'Depends(get_admin_user)',
            'Depends(get_gm_user)',
        ]
        
        has_auth = any(dep in func_def for dep in AUTH_DEPENDENCIES)
        print(f"有认证: {has_auth}")
        
        # 只检查第一个
        break
