#!/usr/bin/env python3
"""
修复API文件中的异常处理顺序
将 except HTTPException 移到 except Exception 之前
"""

import os
import re

# 需要修复的文件列表
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
    'app/apis/v1/user/route.py',
    'app/apis/v1/user/role.py',
    'app/apis/v1/project/info.py',
    'app/apis/v1/project/balance.py',
    'app/apis/v1/project/account.py',
    'app/apis/v1/project/wallet.py',
]

def fix_file(filepath):
    """修复单个文件的异常处理顺序"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # 模式1: except ValueError ... except Exception ... except HTTPException
    # 改为: except HTTPException ... except ValueError ... except Exception
    pattern1 = r'(except ValueError as e:.*?raise HTTPException\(status_code=400, detail=str\(e\)\))\s+(except Exception as e:.*?raise HTTPException\(status_code=500, detail=str\(e\)\))\s+(except HTTPException:\s+raise)'
    
    def replace1(match):
        nonlocal changes
        changes += 1
        return f"{match.group(3)}\n    {match.group(1)}\n    {match.group(2)}"
    
    content = re.sub(pattern1, replace1, content, flags=re.DOTALL)
    
    # 模式2: except Exception ... except HTTPException (没有ValueError)
    # 改为: except HTTPException ... except Exception
    pattern2 = r'(except Exception as e:.*?raise HTTPException\(status_code=500, detail=str\(e\)\))\s+(except HTTPException:\s+raise)'
    
    def replace2(match):
        nonlocal changes
        changes += 1
        return f"{match.group(2)}\n    {match.group(1)}"
    
    content = re.sub(pattern2, replace2, content, flags=re.DOTALL)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, 0

def main():
    """主函数"""
    print("开始修复异常处理顺序...\n")
    print("=" * 80)
    
    total_fixed = 0
    total_changes = 0
    
    for filepath in files_to_fix:
        if not os.path.exists(filepath):
            print(f"⚠️  文件不存在: {filepath}")
            continue
        
        fixed, changes = fix_file(filepath)
        if fixed:
            print(f"✅ {filepath} - 修复了 {changes} 处")
            total_fixed += 1
            total_changes += changes
        else:
            print(f"⏭️  {filepath} - 无需修复")
    
    print("\n" + "=" * 80)
    print(f"\n修复完成！共修复 {total_fixed} 个文件，{total_changes} 处异常处理")

if __name__ == '__main__':
    main()
