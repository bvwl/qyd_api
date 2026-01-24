#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志整理脚本

功能：
1. 压缩所有未压缩的日志文件
2. 按照 日志名称/年/月/日 的目录结构组织日志
3. 删除超过90天（3个月）的旧日志
4. 删除空目录

使用方法：
python scripts/organize_logs.py
"""

import os
import sys
import gzip
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path


def organize_logs(log_dir: str = "logs", days_to_keep: int = 90):
    """
    整理日志文件
    
    Args:
        log_dir: 日志目录
        days_to_keep: 保留天数
    """
    print("=" * 60)
    print("开始整理日志文件")
    print("=" * 60)
    
    log_path = Path(log_dir)
    if not log_path.exists():
        print(f"日志目录不存在: {log_dir}")
        return
    
    # 统计信息
    stats = {
        'compressed': 0,
        'moved': 0,
        'deleted': 0,
        'errors': 0
    }
    
    # 1. 压缩并组织日志文件
    print("\n步骤 1: 压缩并组织日志文件...")
    pattern = os.path.join(log_dir, "*.log.*")
    log_files = glob.glob(pattern)
    
    for filepath in log_files:
        # 跳过已压缩的文件
        if filepath.endswith('.gz'):
            continue
        
        # 跳过子目录中的文件
        if os.path.dirname(filepath) != log_dir:
            continue
        
        try:
            filename = os.path.basename(filepath)
            parts = filename.split('.')
            
            if len(parts) >= 3:
                # 提取日志名称和日期时间
                logger_name = parts[0]  # api, app, database, scheduler
                datetime_str = parts[-1]  # 2026-01-25_14
                
                # 解析日期
                if '_' in datetime_str:
                    date_part = datetime_str.split('_')[0]  # 2026-01-25
                    year = date_part[:4]  # 2026
                    month = date_part[5:7]  # 01
                    day = date_part[8:10]  # 25
                else:
                    # 使用文件修改时间
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    year = file_mtime.strftime('%Y')
                    month = file_mtime.strftime('%m')
                    day = file_mtime.strftime('%d')
                
                # 创建目标目录: logs/日志名称/年/月/日
                target_dir = os.path.join(log_dir, logger_name, year, month, day)
                os.makedirs(target_dir, exist_ok=True)
                
                # 压缩文件
                gz_filename = filename + '.gz'
                target_path = os.path.join(target_dir, gz_filename)
                
                print(f"  压缩: {filename} -> {logger_name}/{year}/{month}/{day}/{gz_filename}")
                
                with open(filepath, 'rb') as f_in:
                    with gzip.open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原文件
                os.remove(filepath)
                stats['compressed'] += 1
                stats['moved'] += 1
            else:
                print(f"  跳过格式不正确的文件: {filename}")
                
        except Exception as e:
            print(f"  错误: 处理文件 {filepath} 失败: {e}")
            stats['errors'] += 1
    
    # 2. 整理已压缩但未分类的日志
    print("\n步骤 2: 整理已压缩但未分类的日志...")
    gz_pattern = os.path.join(log_dir, "*.log.*.gz")
    gz_files = glob.glob(gz_pattern)
    
    for filepath in gz_files:
        # 跳过子目录中的文件
        if os.path.dirname(filepath) != log_dir:
            continue
        
        try:
            filename = os.path.basename(filepath)
            # 去掉 .gz 后缀
            base_filename = filename[:-3]
            parts = base_filename.split('.')
            
            if len(parts) >= 3:
                logger_name = parts[0]
                datetime_str = parts[-1]
                
                # 解析日期
                if '_' in datetime_str:
                    date_part = datetime_str.split('_')[0]
                    year = date_part[:4]
                    month = date_part[5:7]
                    day = date_part[8:10]
                else:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    year = file_mtime.strftime('%Y')
                    month = file_mtime.strftime('%m')
                    day = file_mtime.strftime('%d')
                
                # 创建目标目录
                target_dir = os.path.join(log_dir, logger_name, year, month, day)
                os.makedirs(target_dir, exist_ok=True)
                
                # 移动文件
                target_path = os.path.join(target_dir, filename)
                
                if not os.path.exists(target_path):
                    print(f"  移动: {filename} -> {logger_name}/{year}/{month}/{day}/{filename}")
                    shutil.move(filepath, target_path)
                    stats['moved'] += 1
                else:
                    print(f"  跳过: {filename} (目标文件已存在)")
                    os.remove(filepath)
                    
        except Exception as e:
            print(f"  错误: 处理文件 {filepath} 失败: {e}")
            stats['errors'] += 1
    
    # 2.5. 迁移旧的三层结构（年月合并）到新的四层结构
    print("\n步骤 2.5: 迁移旧的三层结构到新的四层结构...")
    logger_names = ['api', 'app', 'database', 'scheduler']
    
    for logger_name in logger_names:
        logger_dir = os.path.join(log_dir, logger_name)
        
        if not os.path.exists(logger_dir):
            continue
        
        # 查找旧格式的目录（例如 2026-01）
        for item in os.listdir(logger_dir):
            item_path = os.path.join(logger_dir, item)
            
            if not os.path.isdir(item_path):
                continue
            
            # 检查是否是旧格式（YYYY-MM）
            if '-' in item and len(item) == 7:
                year_month = item
                year = year_month[:4]
                month = year_month[5:7]
                
                print(f"  发现旧格式目录: {logger_name}/{year_month}")
                
                # 遍历日期目录
                for day in os.listdir(item_path):
                    day_path = os.path.join(item_path, day)
                    
                    if not os.path.isdir(day_path):
                        continue
                    
                    # 创建新的目标目录
                    target_dir = os.path.join(log_dir, logger_name, year, month, day)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 移动所有文件
                    for filename in os.listdir(day_path):
                        src_file = os.path.join(day_path, filename)
                        target_file = os.path.join(target_dir, filename)
                        
                        if os.path.isfile(src_file):
                            if not os.path.exists(target_file):
                                print(f"    移动: {logger_name}/{year_month}/{day}/{filename} -> {logger_name}/{year}/{month}/{day}/{filename}")
                                shutil.move(src_file, target_file)
                                stats['moved'] += 1
                            else:
                                print(f"    跳过: {filename} (目标文件已存在)")
                                os.remove(src_file)
                
                # 删除旧的空目录
                try:
                    for day in os.listdir(item_path):
                        day_path = os.path.join(item_path, day)
                        if os.path.isdir(day_path) and not os.listdir(day_path):
                            os.rmdir(day_path)
                            print(f"    删除空目录: {logger_name}/{year_month}/{day}")
                    
                    if not os.listdir(item_path):
                        os.rmdir(item_path)
                        print(f"  删除空目录: {logger_name}/{year_month}")
                except Exception as e:
                    print(f"    错误: 删除目录失败: {e}")
    
    # 3. 删除超过指定天数的旧日志
    print(f"\n步骤 3: 删除超过 {days_to_keep} 天的旧日志...")
    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    
    for gz_file in log_path.rglob('*.log.gz'):
        if gz_file.is_file():
            try:
                file_mtime = datetime.fromtimestamp(gz_file.stat().st_mtime)
                
                if file_mtime < cutoff_time:
                    print(f"  删除: {gz_file.relative_to(log_path)}")
                    gz_file.unlink()
                    stats['deleted'] += 1
            except Exception as e:
                print(f"  错误: 删除文件 {gz_file} 失败: {e}")
                stats['errors'] += 1
    
    # 4. 删除空目录
    print("\n步骤 4: 删除空目录...")
    remove_empty_dirs(log_path)
    
    # 5. 显示统计信息
    print("\n" + "=" * 60)
    print("整理完成！")
    print("=" * 60)
    print(f"压缩文件数: {stats['compressed']}")
    print(f"移动文件数: {stats['moved']}")
    print(f"删除文件数: {stats['deleted']}")
    print(f"错误数: {stats['errors']}")
    
    # 6. 显示目录结构
    print("\n当前日志目录结构:")
    print_directory_tree(log_path, max_depth=4)  # 改为4层
    
    # 7. 显示存储统计
    print("\n存储统计:")
    show_storage_stats(log_path)


def remove_empty_dirs(path: Path, level: int = 0):
    """
    递归删除空目录
    """
    try:
        for item in path.iterdir():
            if item.is_dir():
                remove_empty_dirs(item, level + 1)
                # 如果目录为空，删除它
                try:
                    if not any(item.iterdir()):
                        print(f"  删除空目录: {item.relative_to(path.parent)}")
                        item.rmdir()
                except OSError:
                    pass
    except Exception as e:
        if level == 0:
            print(f"  错误: 删除空目录失败: {e}")


def print_directory_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """
    打印目录树结构
    """
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                extension = "    " if is_last else "│   "
                print_directory_tree(item, prefix + extension, max_depth, current_depth + 1)
    except Exception as e:
        print(f"{prefix}[错误: {e}]")


def show_storage_stats(path: Path):
    """
    显示存储统计信息
    """
    total_size = 0
    file_count = 0
    by_logger = {}
    
    for log_file in path.rglob('*.log*'):
        if log_file.is_file():
            file_size = log_file.stat().st_size
            total_size += file_size
            file_count += 1
            
            # 按日志器统计
            logger_name = log_file.name.split('.')[0]
            if logger_name not in by_logger:
                by_logger[logger_name] = {'count': 0, 'size': 0}
            by_logger[logger_name]['count'] += 1
            by_logger[logger_name]['size'] += file_size
    
    print(f"总文件数: {file_count}")
    print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
    
    if by_logger:
        print("\n按日志器统计:")
        for logger_name, stats in sorted(by_logger.items()):
            print(f"  {logger_name}: {stats['count']} 个文件, {stats['size'] / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    # 获取日志目录
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
    else:
        log_dir = "logs"
    
    # 获取保留天数
    if len(sys.argv) > 2:
        days_to_keep = int(sys.argv[2])
    else:
        days_to_keep = 90  # 默认保留3个月
    
    # 执行整理
    organize_logs(log_dir, days_to_keep)
