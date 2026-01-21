#!/usr/bin/env python3
"""
修复API文件中的异常处理顺序
将 except Exception 和 except HTTPException 的顺序调整为正确顺序
"""

import os
import re

files_to_fix = [
    'app/apis/v1/mail/outlook.py',
    'app/apis/v1/mail/info.py',
    'app/apis/v1/server/country.py',
    'app/apis/v1/server/group.py',
    'app/apis/v1/server/info.py',
    'app/apis/v1/server/account.py',
    'app/apis/v1/user/auth.py',
    'app/apis/v1/user/user.py',
    'app/apis/v1/user/user_role.py',
    'app/apis/v1/user/token.py',
    'app/apis/v1/user/log.py',
    'app/apis/v1/user/role.py',
    'app/apis/v1/project/info.py',
    'app/apis/v1/project/balance.py',
    'app/apis/v1/project/account.py',
    'app/apis/v1/project/wallet.py',
]

def fix_file(filepath):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 查找 except Exception
        if 'except Exception as e:' in line:
            # 检查后面几行是否有 except HTTPException
            j = i + 1
            exception_block_end = i + 1
            
            # 找到这个except块的结束位置
            while j < len(lines) and j < i + 10:
                if lines[j].strip().startswith('except '):
                    # 找到了下一个except
                    if 'except HTTPException:' in lines[j]:
                        # 需要交换顺序
                        # 提取Exception块
                        exception_lines = lines[i:j]
                        # 提取HTTPException块（通常是2行）
                        http_exception_lines = [lines[j], lines[j+1]]
                        
                        # 交换顺序：先HTTPException，再Exception
                        lines[i:j+2] = http_exception_lines + exception_lines
                        modified = True
                        break
                    else:
                        break
                j += 1
        
        i += 1
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    
    return False

def main():
    """主函数"""
    print("开始修复异常处理顺序...\n")
    
    fixed_count = 0
    for filepath in files_to_fix:
        if not os.path.exists(filepath):
            print(f"⚠️  文件不存在: {filepath}")
            continue
        
        if fix_file(filepath):
            print(f"✅ 已修复: {filepath}")
            fixed_count += 1
        else:
            print(f"⏭️  无需修复: {filepath}")
    
    print(f"\n修复完成！共修复 {fixed_count} 个文件")

if __name__ == '__main__':
    main()
