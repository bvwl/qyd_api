#!/usr/bin/env python3
"""
将所有删除接口的权限改为管理员权限
"""

import re
from pathlib import Path

# 需要修复的文件列表
files_to_fix = [
    'backend/app/apis/v1/mail/info.py',
    'backend/app/apis/v1/server/country.py',
    'backend/app/apis/v1/server/group.py',
    'backend/app/apis/v1/server/info.py',
    'backend/app/apis/v1/server/account.py',
    'backend/app/apis/v1/user/user.py',
    'backend/app/apis/v1/user/token.py',
    'backend/app/apis/v1/user/log.py',
    'backend/app/apis/v1/user/route.py',
    'backend/app/apis/v1/user/role.py',
    'backend/app/apis/v1/project/info.py',
    'backend/app/apis/v1/project/balance.py',
    'backend/app/apis/v1/project/account.py',
    'backend/app/apis/v1/project/wallet.py',
]

def fix_file(file_path: str) -> bool:
    """修复单个文件的删除接口权限"""
    print(f"\n处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 确保导入了 get_admin_user
    if 'get_admin_user' not in content:
        # 检查是否已经导入了 get_current_user
        if 'from app.core.verify import get_current_user' in content:
            content = content.replace(
                'from app.core.verify import get_current_user',
                'from app.core.verify import get_current_user, get_admin_user'
            )
            print("  ✓ 添加了 get_admin_user 导入")
        elif 'from app.apis.deps import get_current_user' in content:
            content = content.replace(
                'from app.apis.deps import get_current_user',
                'from app.apis.deps import get_current_user, get_admin_user'
            )
            print("  ✓ 添加了 get_admin_user 导入")
    
    # 2. 查找所有删除路由并修改权限
    lines = content.split('\n')
    modified_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 查找删除路由装饰器
        if '@app.delete' in line:
            # 找到函数定义
            func_start = i + 1
            while func_start < len(lines) and 'async def' not in lines[func_start]:
                func_start += 1
            
            if func_start >= len(lines):
                i += 1
                continue
            
            # 找到函数参数结束位置
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
            
            # 检查并修改权限
            func_lines = lines[func_start:func_end+1]
            func_text = '\n'.join(func_lines)
            
            # 如果使用的是 get_current_user，改为 get_admin_user
            if 'get_current_user' in func_text and 'get_admin_user' not in func_text:
                for j in range(func_start, func_end + 1):
                    if 'current_user: dict = Depends(get_current_user)' in lines[j]:
                        lines[j] = lines[j].replace(
                            'current_user: dict = Depends(get_current_user)',
                            'admin_user: dict = Depends(get_admin_user)'
                        )
                        modified_count += 1
                        print(f"  ✓ 修改删除接口权限（第{j+1}行）")
                        break
            
            i = func_end + 1
            continue
        
        i += 1
    
    content = '\n'.join(lines)
    
    # 保存文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 文件已更新: {file_path} (修改了 {modified_count} 个删除接口)")
        return True
    else:
        print(f"⊘ 文件无需更新: {file_path}")
        return False


def main():
    print("=" * 80)
    print("修复删除接口权限")
    print("=" * 80)
    print()
    print("将所有删除接口的权限从 get_current_user 改为 get_admin_user")
    print()
    
    modified_files = 0
    for file_path in files_to_fix:
        if fix_file(file_path):
            modified_files += 1
    
    print()
    print("=" * 80)
    print(f"完成！修改了 {modified_files} 个文件")
    print("=" * 80)
    print()
    print("建议:")
    print("1. 运行 python check_delete_permissions.py 验证修复结果")
    print("2. 重启后端服务")
    print("3. 测试删除功能，确保只有管理员可以删除")


if __name__ == '__main__':
    main()
