#!/usr/bin/env python3
"""
快速为所有API文件添加JWT认证
"""
import os
import glob

# 排除auth.py（登录注册接口不需要认证）
EXCLUDE_FILES = ['auth.py']

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 跳过已处理的文件
    if 'from app.apis.deps import get_current_user' in content:
        return False
    
    # 跳过排除的文件
    if any(exclude in filepath for exclude in EXCLUDE_FILES):
        return False
    
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    for i, line in enumerate(lines):
        # 1. 添加Depends到fastapi导入
        if line.startswith('from fastapi import') and 'Depends' not in line:
            if line.endswith(')'):
                # 多行导入
                new_lines.append(line)
            else:
                # 单行导入
                new_lines.append(line.rstrip() + ', Depends')
                modified = True
                continue
        
        # 2. 在最后一个import后添加deps导入
        if i > 0 and (line.startswith('from ') or line.startswith('import ')):
            new_lines.append(line)
            # 检查下一行是否还是import
            if i + 1 < len(lines) and not (lines[i+1].startswith('from ') or lines[i+1].startswith('import ') or lines[i+1].strip() == ''):
                # 这是最后一个import，添加deps导入
                if 'from app.apis.deps import get_current_user' not in content:
                    new_lines.append('from app.apis.deps import get_current_user')
                    modified = True
            continue
        
        # 3. 为async def函数添加认证参数
        if line.strip().startswith('async def ') and '(' in line:
            # 检查是否已有current_user参数
            if 'current_user' not in line:
                # 找到函数定义的结束
                func_lines = [line]
                j = i + 1
                while j < len(lines) and ')' not in lines[j]:
                    func_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    func_lines.append(lines[j])
                
                # 重构函数定义
                full_func = '\n'.join(func_lines)
                if '):\n' in full_func or '),\n' in full_func:
                    # 在最后一个参数后添加认证参数
                    if 'item:' in full_func or 'id:' in full_func or any(param in full_func for param in ['email:', 'status:', 'name:', 'username:', 'host:', 'domain:', 'project_id:', 'user_id:', 'server_id:', 'email_type:', 'short_name:', 'from_status:', 'to_status:']):
                        # 有参数，添加逗号
                        full_func = full_func.replace('):\n', ',\n    current_user: dict = Depends(get_current_user)\n):\n')
                        full_func = full_func.replace('),\n', ',\n    current_user: dict = Depends(get_current_user)\n),\n')
                    else:
                        # 无参数
                        full_func = full_func.replace('():\n', '(current_user: dict = Depends(get_current_user)):\n')
                        full_func = full_func.replace('(),\n', '(current_user: dict = Depends(get_current_user)),\n')
                    
                    new_lines.extend(full_func.split('\n')[:-1])  # 不包括最后的空行
                    modified = True
                    # 跳过已处理的行
                    while i < j:
                        i += 1
                    continue
        
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def main():
    """主函数"""
    # 查找所有API文件
    api_files = glob.glob('backend/app/apis/v1/**/*.py', recursive=True)
    
    updated = []
    skipped = []
    
    for filepath in api_files:
        if '__init__' in filepath or '__pycache__' in filepath:
            continue
        
        try:
            if process_file(filepath):
                updated.append(filepath)
                print(f"✓ {filepath}")
            else:
                skipped.append(filepath)
                print(f"- {filepath} (已处理或跳过)")
        except Exception as e:
            print(f"✗ {filepath}: {e}")
    
    print(f"\n完成！")
    print(f"更新: {len(updated)} 个文件")
    print(f"跳过: {len(skipped)} 个文件")

if __name__ == '__main__':
    main()
