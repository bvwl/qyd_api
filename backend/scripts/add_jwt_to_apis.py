#!/usr/bin/env python3
"""
批量为API文件添加JWT认证
"""
import os
import re

# 需要添加JWT认证的文件列表（排除auth.py因为它是登录注册接口）
API_FILES = [
    "backend/app/apis/v1/server/account.py",
    "backend/app/apis/v1/server/country.py",
    "backend/app/apis/v1/server/group.py",
    "backend/app/apis/v1/server/info.py",
    "backend/app/apis/v1/project/wallet.py",
    "backend/app/apis/v1/project/account.py",
    "backend/app/apis/v1/project/balance.py",
    "backend/app/apis/v1/mail/info.py",
    "backend/app/apis/v1/mail/outlook.py",
    "backend/app/apis/v1/user/role.py",
    "backend/app/apis/v1/user/route.py",
    "backend/app/apis/v1/user/token.py",
    "backend/app/apis/v1/user/log.py",
]


def add_jwt_to_file(filepath):
    """为单个文件添加JWT认证"""
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入了Depends
    if 'from app.apis.deps import get_current_user' in content:
        print(f"已处理: {filepath}")
        return False
    
    # 1. 添加Depends导入（如果没有）
    if 'from fastapi import' in content and ', Depends' not in content:
        content = re.sub(
            r'from fastapi import ([^)]+)',
            r'from fastapi import \1, Depends',
            content
        )
    
    # 2. 添加deps导入
    if 'from app.apis.deps import get_current_user' not in content:
        # 找到最后一个import语句的位置
        import_lines = []
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                last_import_idx = i
        
        # 在最后一个import后插入
        lines.insert(last_import_idx + 1, 'from app.apis.deps import get_current_user')
        content = '\n'.join(lines)
    
    # 3. 为每个路由函数添加current_user参数
    # 匹配函数定义，添加认证参数
    def add_auth_param(match):
        func_def = match.group(0)
        # 如果已经有current_user参数，跳过
        if 'current_user' in func_def:
            return func_def
        
        # 找到函数参数的最后一个位置
        if '):\n' in func_def:
            # 简单函数定义
            return func_def.replace('):\n', ',\n    current_user: dict = Depends(get_current_user)\n):\n')
        elif '),\n' in func_def:
            # 多行参数
            return func_def.replace('),\n', ',\n    current_user: dict = Depends(get_current_user)\n),\n')
        else:
            return func_def
    
    # 匹配async def函数
    content = re.sub(
        r'async def (post|get|gets|put|delete|post_or_put|batch_update_status|send_mail|get_emails|check_email_status|get_auth_url|get_token)\([^)]*\):\n',
        add_auth_param,
        content,
        flags=re.MULTILINE
    )
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已更新: {filepath}")
    return True


def main():
    """主函数"""
    updated_count = 0
    for filepath in API_FILES:
        if add_jwt_to_file(filepath):
            updated_count += 1
    
    print(f"\n完成！共更新 {updated_count} 个文件")


if __name__ == '__main__':
    main()
