#!/usr/bin/env python3
"""
日志分析工具
分析日志文件，生成统计报告
"""

import os
import sys
import gzip
import glob
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta


def read_log_file(filepath):
    """读取日志文件（支持压缩文件）"""
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
            return f.readlines()
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()


def parse_log_line(line):
    """解析日志行"""
    # 日志格式: 【name】LEVEL YYYY-MM-DD HH:MM:SS message
    pattern = r'【(.+?)】(\w+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)'
    match = re.match(pattern, line)
    
    if match:
        return {
            'logger': match.group(1),
            'level': match.group(2),
            'timestamp': match.group(3),
            'message': match.group(4).strip()
        }
    return None


def analyze_log_levels(log_dir='logs', logger_name=None):
    """分析日志级别分布"""
    print("\n=== 日志级别分析 ===")
    
    level_counter = Counter()
    
    # 获取日志文件
    if logger_name:
        pattern = os.path.join(log_dir, f"{logger_name}.log*")
    else:
        pattern = os.path.join(log_dir, "*.log*")
    
    files = glob.glob(pattern)
    
    for filepath in files:
        try:
            lines = read_log_file(filepath)
            for line in lines:
                parsed = parse_log_line(line)
                if parsed:
                    level_counter[parsed['level']] += 1
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
    
    # 显示结果
    total = sum(level_counter.values())
    print(f"总日志条数: {total}")
    print("\n级别分布:")
    for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        count = level_counter.get(level, 0)
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {level:8s}: {count:6d} ({percentage:5.2f}%)")


def analyze_error_logs(log_dir='logs', logger_name=None, top_n=10):
    """分析错误日志"""
    print("\n=== 错误日志分析 ===")
    
    error_messages = []
    
    # 获取日志文件
    if logger_name:
        pattern = os.path.join(log_dir, f"{logger_name}.log*")
    else:
        pattern = os.path.join(log_dir, "*.log*")
    
    files = glob.glob(pattern)
    
    for filepath in files:
        try:
            lines = read_log_file(filepath)
            for line in lines:
                parsed = parse_log_line(line)
                if parsed and parsed['level'] in ['ERROR', 'CRITICAL']:
                    error_messages.append({
                        'timestamp': parsed['timestamp'],
                        'level': parsed['level'],
                        'message': parsed['message'][:100]  # 截取前100字符
                    })
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
    
    print(f"错误日志总数: {len(error_messages)}")
    
    if error_messages:
        print(f"\n最近 {min(top_n, len(error_messages))} 条错误:")
        for i, error in enumerate(sorted(error_messages, key=lambda x: x['timestamp'], reverse=True)[:top_n], 1):
            print(f"\n{i}. [{error['timestamp']}] {error['level']}")
            print(f"   {error['message']}")


def analyze_api_calls(log_dir='logs', logger_name='api', top_n=10):
    """分析 API 调用统计"""
    print("\n=== API 调用分析 ===")
    
    endpoint_counter = Counter()
    method_counter = Counter()
    status_counter = Counter()
    user_counter = Counter()
    
    pattern = os.path.join(log_dir, f"{logger_name}.log*")
    files = glob.glob(pattern)
    
    for filepath in files:
        try:
            lines = read_log_file(filepath)
            for line in lines:
                # 解析 API 日志: 用户=xxx IP=xxx GET /api/xxx 参数={} 状态码=200
                if 'GET ' in line or 'POST ' in line or 'PUT ' in line or 'DELETE ' in line:
                    # 提取方法
                    for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        if f' {method} ' in line:
                            method_counter[method] += 1
                            
                            # 提取端点
                            endpoint_match = re.search(rf'{method}\s+(/[^\s]+)', line)
                            if endpoint_match:
                                endpoint_counter[endpoint_match.group(1)] += 1
                            break
                    
                    # 提取状态码
                    status_match = re.search(r'状态码=(\d+)', line)
                    if status_match:
                        status_code = status_match.group(1)
                        status_counter[status_code] += 1
                    
                    # 提取用户
                    user_match = re.search(r'用户=([^\s]+)', line)
                    if user_match:
                        user_counter[user_match.group(1)] += 1
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
    
    total_calls = sum(method_counter.values())
    print(f"API 调用总数: {total_calls}")
    
    if method_counter:
        print("\n请求方法分布:")
        for method, count in method_counter.most_common():
            percentage = (count / total_calls * 100) if total_calls > 0 else 0
            print(f"  {method:6s}: {count:6d} ({percentage:5.2f}%)")
    
    if status_counter:
        print("\n状态码分布:")
        for status, count in sorted(status_counter.items()):
            percentage = (count / total_calls * 100) if total_calls > 0 else 0
            print(f"  {status}: {count:6d} ({percentage:5.2f}%)")
    
    if endpoint_counter:
        print(f"\nTop {top_n} 热门端点:")
        for endpoint, count in endpoint_counter.most_common(top_n):
            percentage = (count / total_calls * 100) if total_calls > 0 else 0
            print(f"  {count:6d} ({percentage:5.2f}%) {endpoint}")
    
    if user_counter:
        print(f"\nTop {top_n} 活跃用户:")
        for user, count in user_counter.most_common(top_n):
            print(f"  {user}: {count} 次调用")


def analyze_time_distribution(log_dir='logs', logger_name=None):
    """分析时间分布"""
    print("\n=== 时间分布分析 ===")
    
    hour_counter = Counter()
    date_counter = Counter()
    
    # 获取日志文件
    if logger_name:
        pattern = os.path.join(log_dir, f"{logger_name}.log*")
    else:
        pattern = os.path.join(log_dir, "*.log*")
    
    files = glob.glob(pattern)
    
    for filepath in files:
        try:
            lines = read_log_file(filepath)
            for line in lines:
                parsed = parse_log_line(line)
                if parsed:
                    try:
                        dt = datetime.strptime(parsed['timestamp'], '%Y-%m-%d %H:%M:%S')
                        hour_counter[dt.hour] += 1
                        date_counter[dt.date()] += 1
                    except:
                        pass
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
    
    if hour_counter:
        print("\n小时分布:")
        max_count = max(hour_counter.values())
        for hour in range(24):
            count = hour_counter.get(hour, 0)
            bar_length = int(count / max_count * 50) if max_count > 0 else 0
            bar = '█' * bar_length
            print(f"  {hour:02d}:00 {count:6d} {bar}")
    
    if date_counter:
        print("\n日期分布（最近7天）:")
        sorted_dates = sorted(date_counter.keys(), reverse=True)[:7]
        for date in sorted_dates:
            count = date_counter[date]
            print(f"  {date}: {count:6d}")


def analyze_file_sizes(log_dir='logs'):
    """分析日志文件大小"""
    print("\n=== 文件大小分析 ===")
    
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    compressed_files = glob.glob(os.path.join(log_dir, "*.log.*.gz"))
    uncompressed_rotated = [f for f in glob.glob(os.path.join(log_dir, "*.log.*")) 
                           if not f.endswith('.gz')]
    
    total_size = 0
    compressed_size = 0
    
    print(f"当前日志文件: {len(log_files)} 个")
    for f in log_files:
        size = os.path.getsize(f)
        total_size += size
        print(f"  {os.path.basename(f):30s} {size/1024:8.2f} KB")
    
    print(f"\n压缩日志文件: {len(compressed_files)} 个")
    for f in compressed_files[:10]:  # 只显示前10个
        size = os.path.getsize(f)
        compressed_size += size
        total_size += size
    
    if len(compressed_files) > 10:
        for f in compressed_files[10:]:
            size = os.path.getsize(f)
            compressed_size += size
            total_size += size
        print(f"  ... 还有 {len(compressed_files) - 10} 个文件")
    
    print(f"\n未压缩滚动日志: {len(uncompressed_rotated)} 个")
    if uncompressed_rotated:
        print("  ⚠️  建议运行压缩: python scripts/cleanup_logs.py")
    
    print(f"\n总大小: {total_size/1024/1024:.2f} MB")
    if compressed_size > 0:
        print(f"压缩文件大小: {compressed_size/1024/1024:.2f} MB")


def main():
    """主函数"""
    log_dir = "logs"
    
    if not os.path.exists(log_dir):
        print(f"日志目录不存在: {log_dir}")
        return 1
    
    print("="*60)
    print("日志分析报告")
    print("="*60)
    print(f"分析目录: {log_dir}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 文件大小分析
    analyze_file_sizes(log_dir)
    
    # 日志级别分析
    analyze_log_levels(log_dir)
    
    # 错误日志分析
    analyze_error_logs(log_dir, top_n=5)
    
    # API 调用分析
    if os.path.exists(os.path.join(log_dir, "api.log")):
        analyze_api_calls(log_dir, logger_name='api', top_n=10)
    
    # 时间分布分析
    analyze_time_distribution(log_dir)
    
    print("\n" + "="*60)
    print("分析完成")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
