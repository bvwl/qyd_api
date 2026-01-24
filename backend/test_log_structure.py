#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试日志目录结构

验证日志系统是否按照 名称/年/月/日 的四层结构组织
"""

import os
from pathlib import Path


def test_log_structure():
    """测试日志目录结构"""
    print("=" * 60)
    print("测试日志目录结构")
    print("=" * 60)
    
    log_dir = Path("logs")
    
    if not log_dir.exists():
        print("❌ 日志目录不存在")
        return False
    
    print("✅ 日志目录存在")
    
    # 检查当前日志文件
    current_logs = ['api.log', 'app.log', 'database.log', 'scheduler.log']
    for log_name in current_logs:
        log_file = log_dir / log_name
        if log_file.exists():
            print(f"✅ 当前日志存在: {log_name}")
        else:
            print(f"⚠️  当前日志不存在: {log_name}")
    
    # 检查归档目录结构
    print("\n检查归档目录结构...")
    logger_names = ['api', 'app', 'database', 'scheduler']
    
    structure_correct = True
    
    for logger_name in logger_names:
        logger_dir = log_dir / logger_name
        
        if not logger_dir.exists():
            print(f"⚠️  归档目录不存在: {logger_name}/")
            continue
        
        print(f"\n📁 {logger_name}/")
        
        # 检查年份目录
        year_dirs = [d for d in logger_dir.iterdir() if d.is_dir()]
        
        if not year_dirs:
            print(f"  ⚠️  没有年份目录")
            continue
        
        for year_dir in sorted(year_dirs):
            year = year_dir.name
            
            # 验证年份格式（应该是4位数字）
            if not year.isdigit() or len(year) != 4:
                print(f"  ❌ 年份目录格式错误: {year}")
                structure_correct = False
                continue
            
            print(f"  📅 {year}/")
            
            # 检查月份目录
            month_dirs = [d for d in year_dir.iterdir() if d.is_dir()]
            
            if not month_dirs:
                print(f"    ⚠️  没有月份目录")
                continue
            
            for month_dir in sorted(month_dirs):
                month = month_dir.name
                
                # 验证月份格式（应该是2位数字）
                if not month.isdigit() or len(month) != 2:
                    print(f"    ❌ 月份目录格式错误: {month}")
                    structure_correct = False
                    continue
                
                # 检查日期目录
                day_dirs = [d for d in month_dir.iterdir() if d.is_dir()]
                
                if not day_dirs:
                    print(f"    📆 {month}/ (没有日期目录)")
                    continue
                
                # 只显示前3个日期目录
                display_days = sorted(day_dirs)[:3]
                day_count = len(day_dirs)
                
                for day_dir in display_days:
                    day = day_dir.name
                    
                    # 验证日期格式（应该是2位数字）
                    if not day.isdigit() or len(day) != 2:
                        print(f"      ❌ 日期目录格式错误: {day}")
                        structure_correct = False
                        continue
                    
                    # 检查压缩日志文件
                    gz_files = list(day_dir.glob('*.log.*.gz'))
                    
                    if gz_files:
                        print(f"      📄 {month}/{day}/ ({len(gz_files)} 个压缩日志)")
                    else:
                        print(f"      ⚠️  {month}/{day}/ (没有压缩日志)")
                
                if day_count > 3:
                    print(f"      ... (还有 {day_count - 3} 个日期目录)")
    
    print("\n" + "=" * 60)
    
    if structure_correct:
        print("✅ 目录结构验证通过！")
        print("   格式: 名称/年/月/日 (四层结构)")
        return True
    else:
        print("❌ 目录结构验证失败！")
        print("   请运行: python scripts/organize_logs.py")
        return False


def show_example_structure():
    """显示示例目录结构"""
    print("\n" + "=" * 60)
    print("正确的目录结构示例")
    print("=" * 60)
    print("""
logs/
├── api.log                    # 当前日志
├── api/                       # 归档（第0层）
│   └── 2026/                 # 年（第1层）
│       └── 01/               # 月（第2层）
│           └── 25/           # 日（第3层）
│               ├── api.log.2026-01-25_00.gz
│               ├── api.log.2026-01-25_02.gz
│               └── ...
├── app.log
├── app/
│   └── 2026/01/25/...
├── database.log
├── database/
│   └── 2026/01/25/...
└── scheduler.log
    └── scheduler/
        └── 2026/01/25/...
    """)


def show_statistics():
    """显示日志统计信息"""
    print("\n" + "=" * 60)
    print("日志统计信息")
    print("=" * 60)
    
    log_dir = Path("logs")
    
    if not log_dir.exists():
        print("日志目录不存在")
        return
    
    # 统计文件数量和大小
    total_files = 0
    total_size = 0
    compressed_files = 0
    compressed_size = 0
    
    for log_file in log_dir.rglob('*.log*'):
        if log_file.is_file():
            file_size = log_file.stat().st_size
            total_files += 1
            total_size += file_size
            
            if log_file.name.endswith('.gz'):
                compressed_files += 1
                compressed_size += file_size
    
    print(f"总文件数: {total_files}")
    print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
    print(f"压缩文件数: {compressed_files}")
    print(f"压缩文件大小: {compressed_size / 1024 / 1024:.2f} MB")
    
    if compressed_files > 0:
        compression_ratio = (1 - compressed_size / total_size) * 100
        print(f"压缩率: {compression_ratio:.1f}%")


if __name__ == '__main__':
    # 测试目录结构
    success = test_log_structure()
    
    # 显示示例结构
    show_example_structure()
    
    # 显示统计信息
    show_statistics()
    
    # 退出码
    exit(0 if success else 1)
