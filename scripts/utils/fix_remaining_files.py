#!/usr/bin/env python3
"""修复剩余文件的认证"""

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
    
    # 1. 添加 Depends 到导入
    if 'from fastapi import' in content and ', Depends' not in content:
        content = re.sub(
            r'(from fastapi import [^\n]+)',
            r'\1, Depends',
            content,
            count=1
        )
        print("  ✓ 添加了 Depends 导入")
    
    # 2. 添加 get_current_user 导入
    if 'from app.core.verify import get_current_user' not in content and 'from app.apis.deps import get_current_user' not in content:
        # 在 app = APIRouter() 之前添加
        if 'app = APIRouter()' in content:
            content = content.replace(
                'app = APIRouter()',
                'from app.core.verify import get_current_user\n\napp = APIRouter()'
            )
            print("  ✓ 添加了 get_current_user 导入")
    
    # 3. 为每个路由函数添加认证参数
    # 匹配模式：找到所有的 async def 函数定义
    
    # 模式1: 单行无参数函数
    pattern1 = r'(@app\.(get|post|put|delete|patch)\([^)]+\)\s*\nasync def \w+\(\s*\):)'
    matches1 = list(re.finditer(pattern1, content))
    for match in reversed(matches1):
        func_def = match.group(0)
        if 'get_current_user' not in func_def and 'get_admin_user' not in func_def:
            new_def = func_def[:-2] + '\n    current_user: dict = Depends(get_current_user)\n):'
            content = content[:match.start()] + new_def + content[match.end():]
            print(f"  ✓ 添加认证到无参数函数")
    
    # 模式2: 单行有参数函数
    pattern2 = r'(@app\.(get|post|put|delete|patch)\([^)]+\)\s*\nasync def \w+\([^)]+\):)'
    matches2 = list(re.finditer(pattern2, content))
    for match in reversed(matches2):
        func_def = match.group(0)
        if 'get_current_user' not in func_def and 'get_admin_user' not in func_def:
            # 检查是否是单行定义
            if '\n' not in func_def[func_def.index('async def'):]:
                new_def = func_def[:-2] + ',\n    current_user: dict = Depends(get_current_user)\n):'
                content = content[:match.start()] + new_def + content[match.end():]
                print(f"  ✓ 添加认证到单行函数")
    
    # 模式3: 多行参数函数 - 需要找到最后一个参数
    # 这个比较复杂，我们使用更简单的方法：查找 ): 模式并在前面添加认证参数
    lines = content.split('\n')
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 查找路由装饰器
        if re.match(r'@app\.(get|post|put|delete|patch)', line):
            # 找到函数定义
            func_start = i + 1
            while func_start < len(lines) and 'async def' not in lines[func_start]:
                func_start += 1
            
            if func_start >= len(lines):
                i += 1
                continue
            
            # 找到函数参数结束位置 ):
            func_end = func_start
            paren_count = 0
            found_open = False
            
            for j in range(func_start, min(func_start + 50, len(lines))):
                for char in lines[j]:
                    if char == '(':
                        paren_count += 1
                        found_open = True
                    elif char == ')':
                        paren_count -= 1
                        if found_open and paren_count == 0:
                            func_end = j
                            break
                if func_end > func_start:
                    break
            
            if func_end <= func_start:
                i += 1
                continue
            
            # 检查是否已经有认证
            func_lines = '\n'.join(lines[func_start:func_end+1])
            if 'get_current_user' in func_lines or 'get_admin_user' in func_lines:
                i = func_end + 1
                continue
            
            # 添加认证参数
            # 在 ): 之前添加
            end_line = lines[func_end]
            if end_line.strip() == '):':
                # 在这一行之前插入认证参数
                lines.insert(func_end, '    current_user: dict = Depends(get_current_user)')
                modified = True
                print(f"  ✓ 添加认证到多行函数（第{func_end+1}行）")
            elif '):' in end_line:
                # 在 ): 之前插入
                indent = len(end_line) - len(end_line.lstrip())
                lines[func_end] = end_line.replace('):', ',\n' + ' ' * indent + 'current_user: dict = Depends(get_current_user)\n' + ' ' * indent + '):')
                modified = True
                print(f"  ✓ 添加认证到函数（第{func_end+1}行）")
            
            i = func_end + 1
            continue
        
        i += 1
    
    if modified:
        content = '\n'.join(lines)
    
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
