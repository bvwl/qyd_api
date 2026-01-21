#!/usr/bin/env python3
"""
批量为后端 API 添加 JWT/API-TOKEN 认证
"""
import os
import re

# 需要添加认证的文件列表（排除 auth.py）
FILES_TO_UPDATE = [
    "app/apis/v1/mail/outlook.py",
    "app/apis/v1/project/account.py",
    "app/apis/v1/project/balance.py",
    "app/apis/v1/server/country.py",
    "app/apis/v1/server/group.py",
    "app/apis/v1/server/info.py",
    "app/apis/v1/user/log.py",
    "app/apis/v1/user/role.py",
    "app/apis/v1/user/route.py",
    "app/apis/v1/user/token.py",
]

def add_auth_to_file(file_path):
    """为单个文件添加认证"""
    if not os.path.exists(file_path):
        print(f"⚠️  文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入了 Depends
    if "from fastapi import" in content and "Depends" not in content:
        # 添加 Depends 到导入
        content = re.sub(
            r'from fastapi import ([^)]+)',
            lambda m: f'from fastapi import {m.group(1)}, Depends' if 'Depends' not in m.group(1) else m.group(0),
            content
        )
    
    # 检查是否已经导入了 get_current_user
    if "get_current_user" not in content:
        # 在 fastapi 导入后添加 deps 导入
        if "from fastapi import" in content:
            content = re.sub(
                r'(from fastapi import [^\n]+\n)',
                r'\1from app.apis.deps import get_current_user\n',
                content,
                count=1
            )
    
    # 为每个端点函数添加 current_user 参数
    # 匹配函数定义：async def function_name(
    def add_auth_param(match):
        func_def = match.group(0)
        # 如果已经有 current_user 参数，跳过
        if "current_user" in func_def:
            return func_def
        
        # 在最后一个参数后添加 current_user
        # 找到函数参数的结束位置
        if "):" in func_def:
            # 如果参数列表为空或只有一行
            func_def = func_def.replace(
                "):",
                ",\n    current_user: dict = Depends(get_current_user)\n):"
            )
        return func_def
    
    # 匹配所有 async def 函数
    content = re.sub(
        r'async def \w+\([^)]*\):',
        add_auth_param,
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新: {file_path}")
    return True

def main():
    """主函数"""
    print("开始批量添加认证...")
    print("=" * 60)
    
    success_count = 0
    for file_path in FILES_TO_UPDATE:
        if add_auth_to_file(file_path):
            success_count += 1
    
    print("=" * 60)
    print(f"完成！成功更新 {success_count}/{len(FILES_TO_UPDATE)} 个文件")
    print("\n注意：请手动检查以下内容：")
    print("1. 确认所有端点都添加了 current_user 参数")
    print("2. 确认导入语句正确")
    print("3. 运行测试确保功能正常")

if __name__ == "__main__":
    main()
