#!/usr/bin/env python3
"""
修复CRUD文件中的空结果处理逻辑
将 404 错误改为返回空列表
"""

import os
import re

# 需要修复的文件列表
files_to_fix = [
    'app/crud/project/account.py',
    'app/crud/user/role.py',
    'app/crud/project/balance.py',
    'app/crud/server/account.py',
    'app/crud/project/info.py',
    'app/crud/user/log.py',
    'app/crud/server/info.py',
    'app/crud/project/wallet.py',
    'app/crud/server/country.py',
    'app/crud/user/token.py',
    'app/crud/user/route.py',
    'app/crud/mail/info.py',
    'app/crud/user/user.py',
    'app/crud/server/group.py',
]

def fix_file(filepath):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换模式
    # 原模式：
    # if not res:
    #     raise HTTPException(status_code=404, detail='未查询到数据')
    # 
    # num = len(res)
    
    # 新模式：
    # # 空结果不是错误，返回空列表
    # num = len(res) if res else 0
    
    pattern = r"if not res:\s+raise HTTPException\(status_code=404, detail='未查询到数据'\)\s+num = len\(res\)"
    replacement = "# 空结果不是错误，返回空列表\n        num = len(res) if res else 0"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ 已修复: {filepath}")
        return True
    else:
        print(f"✗ 未找到匹配模式: {filepath}")
        return False

def main():
    """主函数"""
    print("开始修复空结果处理逻辑...\n")
    
    fixed_count = 0
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"✗ 文件不存在: {filepath}")
    
    print(f"\n修复完成！共修复 {fixed_count}/{len(files_to_fix)} 个文件")

if __name__ == '__main__':
    main()
