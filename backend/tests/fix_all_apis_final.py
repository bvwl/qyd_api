#!/usr/bin/env python3
"""
最终版本：修复所有API文件的异常处理
确保顺序为: except HTTPException -> except ValueError -> except Exception
"""

import os
import re

files_to_fix = [
    'app/apis/v1/mail/info.py',
    'app/apis/v1/server/country.py',
    'app/apis/v1/server/group.py',
    'app/apis/v1/server/info.py',
    'app/apis/v1/server/account.py',
    'app/apis/v1/user/auth.py',
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
        content = f.read()
    
    original = content
    
    # 模式：except ValueError ... except Exception (缺少HTTPException)
    # 在ValueError和Exception之间插入HTTPException
    pattern = r'(    except ValueError as e:\n        raise HTTPException\(status_code=400, detail=str\(e\)\)\n)(    except Exception as e:)'
    replacement = r'\1    except HTTPException:\n        raise\n\2'
    content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("开始修复API文件...\n")
    fixed = 0
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            if fix_file(filepath):
                print(f"✅ {filepath}")
                fixed += 1
            else:
                print(f"⏭️  {filepath}")
    print(f"\n修复完成！共修复 {fixed} 个文件")

if __name__ == '__main__':
    main()
