#!/usr/bin/env python3
"""
回滚空结果处理逻辑修改
将返回空列表改回抛出404错误
"""

import os
import re

# 需要回滚的文件列表
files_to_revert = [
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

def revert_file(filepath):
    """回滚单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换模式
    # 当前模式：
    # # 空结果不是错误，返回空列表
    # num = len(res) if res else 0
    
    # 回滚为：
    # if not res:
    #     raise HTTPException(status_code=404, detail='未查询到数据')
    # 
    # num = len(res)
    
    pattern = r"# 空结果不是错误，返回空列表\s+num = len\(res\) if res else 0"
    replacement = "if not res:\n            raise HTTPException(status_code=404, detail='未查询到数据')\n        \n        num = len(res)"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ 已回滚: {filepath}")
        return True
    else:
        print(f"✗ 未找到匹配模式: {filepath}")
        return False

def main():
    """主函数"""
    print("开始回滚空结果处理逻辑...\n")
    
    reverted_count = 0
    for filepath in files_to_revert:
        if os.path.exists(filepath):
            if revert_file(filepath):
                reverted_count += 1
        else:
            print(f"✗ 文件不存在: {filepath}")
    
    print(f"\n回滚完成！共回滚 {reverted_count}/{len(files_to_revert)} 个文件")

if __name__ == '__main__':
    main()
