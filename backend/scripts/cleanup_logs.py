#!/usr/bin/env python3
"""
日志清理脚本
可以通过 cron 定期执行，清理和压缩日志文件

使用方法:
    python scripts/cleanup_logs.py
    
或添加到 crontab (每天凌晨3点执行):
    0 3 * * * cd /path/to/backend && python scripts/cleanup_logs.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.logs import compress_old_logs, delete_old_compressed_logs
import glob
import os


def cleanup_all_logs(log_dir: str = "logs", retention_days: int = 30):
    """
    清理所有日志文件
    
    Args:
        log_dir: 日志目录
        retention_days: 保留天数
    """
    print(f"开始清理日志目录: {log_dir}")
    print(f"保留天数: {retention_days}")
    
    if not os.path.exists(log_dir):
        print(f"日志目录不存在: {log_dir}")
        return
    
    # 获取所有日志文件的基础名称
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    logger_names = set()
    
    for log_file in log_files:
        basename = os.path.basename(log_file)
        # 提取 logger 名称（去掉 .log 后缀）
        logger_name = basename.replace('.log', '')
        logger_names.add(logger_name)
    
    print(f"\n发现 {len(logger_names)} 个日志模块: {', '.join(logger_names)}")
    
    # 压缩每个模块的旧日志
    print("\n=== 压缩旧日志 ===")
    for logger_name in logger_names:
        print(f"压缩 {logger_name} 模块的日志...")
        compress_old_logs(log_dir=log_dir, name=logger_name)
    
    # 删除超期的压缩日志
    print(f"\n=== 删除超过 {retention_days} 天的压缩日志 ===")
    delete_old_compressed_logs(log_dir=log_dir, days=retention_days)
    
    print("\n日志清理完成！")


if __name__ == "__main__":
    # 可以通过命令行参数指定保留天数
    retention_days = 30
    if len(sys.argv) > 1:
        try:
            retention_days = int(sys.argv[1])
        except ValueError:
            print(f"无效的天数参数: {sys.argv[1]}, 使用默认值 30 天")
    
    cleanup_all_logs(retention_days=retention_days)
