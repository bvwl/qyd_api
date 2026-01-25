#!/usr/bin/env python3
"""
修复时间参数重复解析的问题

问题：API层已经调用parse_time()将字符串转换为datetime对象，
但CRUD层又再次调用parse_time()，导致对datetime对象调用strptime()失败。

解决方案：移除API层的parse_time()调用，让CRUD层统一处理时间参数解析。
"""

import os
import re
from pathlib import Path


def fix_api_file(file_path: str) -> bool:
    """
    修复API文件：移除parse_time()调用
    
    将：
        create_time_start=parse_time(create_time_start),
    改为：
        create_time_start=create_time_start,
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 移除 parse_time() 调用，保留参数名
    # 匹配模式：create_time_start=parse_time(create_time_start)
    # 或：create_time_start=parse_time(create_time_start, True)
    patterns = [
        (r'(\w+_time_start)=parse_time\(\1\)', r'\1=\1'),
        (r'(\w+_time_end)=parse_time\(\1,\s*True\)', r'\1=\1'),
        (r'(\w+_time_end)=parse_time\(\1,\s*is_end=True\)', r'\1=\1'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def find_and_fix_files():
    """查找并修复所有API文件"""
    backend_dir = Path(__file__).parent
    api_dir = backend_dir / 'app' / 'apis' / 'v1'
    
    if not api_dir.exists():
        print(f"❌ API目录不存在: {api_dir}")
        return
    
    fixed_files = []
    
    # 遍历所有API文件
    for api_file in api_dir.rglob('*.py'):
        if api_file.name == '__init__.py':
            continue
        
        try:
            if fix_api_file(str(api_file)):
                fixed_files.append(str(api_file.relative_to(backend_dir)))
                print(f"✅ 已修复: {api_file.relative_to(backend_dir)}")
        except Exception as e:
            print(f"❌ 修复失败 {api_file.relative_to(backend_dir)}: {e}")
    
    print(f"\n{'='*60}")
    print(f"修复完成！共修复 {len(fixed_files)} 个文件")
    print(f"{'='*60}")
    
    if fixed_files:
        print("\n修复的文件列表：")
        for file in fixed_files:
            print(f"  - {file}")


if __name__ == '__main__':
    find_and_fix_files()
