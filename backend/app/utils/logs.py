import logging
import os
from logging import Logger
from concurrent_log_handler import ConcurrentRotatingFileHandler
import gzip
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path


def getLogger(name: str = 'root') -> Logger:
    """
    创建一个按文件大小滚动（200MB）、支持多进程安全、自动压缩日志的 Logger
    :param name: 日志器名称
    :return: 单例 Logger 对象
    """
    logger: Logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # 日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # 日志文件路径
        log_file = os.path.join(log_dir, f"{name}.log")

        # 文件处理器：按文件大小滚动，单个文件最大200MB，保留7天
        # 假设每天产生约1GB日志，7天约7GB，需要约35个200MB的文件
        file_handler = ConcurrentRotatingFileHandler(
            filename=log_file,
            mode='a',
            maxBytes=200 * 1024 * 1024,  # 200MB
            backupCount=50,               # 保留50个备份文件（约10GB，足够7天使用）
            encoding='utf-8',
            use_gzip=False  # 不使用内置压缩，我们自己处理
        )

        # 设置 Formatter - 简化格式，去掉路径信息
        formatter = logging.Formatter(
            fmt="【{name}】{levelname} {asctime} {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{"
        )
        console_formatter = logging.Formatter(
            fmt="{levelname} {asctime} {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(console_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # 注意：日志压缩由 main.py 中的启动任务和定时任务统一处理
        # 不在这里执行，避免每次创建 logger 都重复压缩

    return logger


def _compress_and_organize_logs(log_dir: str, name: str):
    """
    将旧日志压缩并按照 日志名称/年/月/日 的目录结构组织
    例如: logs/api/2026/02/22/api.log.1.gz
    """
    pattern = os.path.join(log_dir, f"{name}.log.*")
    for filepath in glob.glob(pattern):
        if filepath.endswith('.gz'):
            continue
        
        try:
            # 使用文件修改时间来组织目录结构
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            year = file_mtime.strftime('%Y')
            month = file_mtime.strftime('%m')
            day = file_mtime.strftime('%d')
            
            # 创建目标目录结构: logs/日志名称/年/月/日
            target_dir = os.path.join(log_dir, name, year, month, day)
            os.makedirs(target_dir, exist_ok=True)
            
            # 压缩文件
            filename = os.path.basename(filepath)
            gz_filename = filename + '.gz'
            target_path = os.path.join(target_dir, gz_filename)
            
            # 如果目标文件已存在，添加时间戳避免覆盖
            if os.path.exists(target_path):
                timestamp = file_mtime.strftime('%H%M%S')
                gz_filename = f"{filename}.{timestamp}.gz"
                target_path = os.path.join(target_dir, gz_filename)
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            os.remove(filepath)
            print(f"日志已压缩并移动: {filepath} -> {target_path}")
                
        except Exception as e:
            print(f"日志压缩失败: {filepath}, 原因: {e}")


def compress_old_logs(log_dir: str = None, name: str = "root"):
    """
    压缩旧的日志文件（公共接口）
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
        name: 日志器名称
    """
    if log_dir is None:
        log_dir = "logs"
    
    _compress_and_organize_logs(log_dir, name)


def compress_all_logs(log_dir: str = None):
    """
    压缩所有日志模块的旧日志文件，并按目录结构组织
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
    """
    if log_dir is None:
        log_dir = "logs"
    
    if not os.path.exists(log_dir):
        return
    
    # 获取所有日志模块名称
    logger_names = set()
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            # 提取模块名（去掉.log后缀）
            logger_name = filename[:-4]
            logger_names.add(logger_name)
    
    # 压缩每个模块的旧日志
    compressed_count = 0
    processed_files = set()  # 记录已处理的文件，避免重复
    
    for logger_name in logger_names:
        pattern = os.path.join(log_dir, f"{logger_name}.log.*")
        for filepath in glob.glob(pattern):
            # 跳过已压缩的文件
            if filepath.endswith('.gz'):
                continue
            
            # 跳过已处理的文件（避免重复）
            if filepath in processed_files:
                continue
            
            # 检查文件是否存在（避免并发问题）
            if not os.path.exists(filepath):
                continue
            
            processed_files.add(filepath)
            
            try:
                # 使用文件修改时间来组织目录结构
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                year = file_mtime.strftime('%Y')
                month = file_mtime.strftime('%m')
                day = file_mtime.strftime('%d')
                
                # 创建目标目录
                target_dir = os.path.join(log_dir, logger_name, year, month, day)
                os.makedirs(target_dir, exist_ok=True)
                
                # 压缩文件
                filename = os.path.basename(filepath)
                gz_filename = filename + '.gz'
                target_path = os.path.join(target_dir, gz_filename)
                
                # 如果目标文件已存在，添加时间戳避免覆盖
                if os.path.exists(target_path):
                    timestamp = file_mtime.strftime('%H%M%S')
                    gz_filename = f"{filename}.{timestamp}.gz"
                    target_path = os.path.join(target_dir, gz_filename)
                
                with open(filepath, 'rb') as f_in:
                    with gzip.open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                os.remove(filepath)
                compressed_count += 1
                print(f"日志已压缩并移动: {filepath} -> {target_path}")
                    
            except FileNotFoundError:
                # 文件已被其他进程处理，跳过
                continue
            except Exception as e:
                print(f"日志压缩失败: {filepath}, 原因: {e}")
    
    if compressed_count > 0:
        print(f"成功压缩并组织 {compressed_count} 个日志文件")
    
    # 同时清理超过7天的压缩日志
    delete_old_compressed_logs(log_dir, days=7)


def log_api_call(logger: Logger, user_id: str = None, endpoint: str = None, method: str = None, params: dict = None, response_status: int = None, client_ip: str = None):
    """
    记录API调用信息，包含用户ID、接口路径、请求方法、参数、响应状态和来源IP
    
    Args:
        logger: 日志器对象
        user_id: 用户ID
        endpoint: 接口路径
        method: 请求方法 (GET, POST, PUT, DELETE等)
        params: 请求参数
        response_status: 响应状态码
        client_ip: 客户端IP地址
    """
    try:
        # 构建日志信息
        log_parts = []
        
        if user_id:
            log_parts.append(f"用户={user_id}")
        
        if client_ip:
            log_parts.append(f"IP={client_ip}")
        
        if method and endpoint:
            log_parts.append(f"{method} {endpoint}")
        elif endpoint:
            log_parts.append(f"接口={endpoint}")
            
        if params:
            # 过滤敏感信息
            safe_params = {k: v for k, v in params.items() 
                          if k.lower() not in ['password', 'token', 'secret', 'key']}
            if safe_params:
                log_parts.append(f"参数={safe_params}")
        
        if response_status:
            log_parts.append(f"状态码={response_status}")
        
        if log_parts:
            log_message = " ".join(log_parts)
            logger.info(log_message)
            
    except Exception as e:
        logger.error(f"记录API调用日志失败: {e}")


def delete_old_compressed_logs(log_dir: str = None, days: int = 7):
    """
    删除超过指定天数的压缩日志文件（递归删除子目录）
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
        days: 保留天数，默认7天
    """
    try:
        if log_dir is None:
            log_dir = "logs"
        
        log_path = Path(log_dir)
        if not log_path.exists():
            return
        
        # 计算截止时间
        cutoff_time = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        
        # 递归遍历所有子目录
        for gz_file in log_path.rglob('*.log.gz'):
            if gz_file.is_file():
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(gz_file.stat().st_mtime)
                
                # 如果文件超过保留期限，删除它
                if file_mtime < cutoff_time:
                    gz_file.unlink()
                    print(f"删除旧压缩日志文件: {gz_file}")
                    deleted_count += 1
        
        # 删除空目录
        _remove_empty_dirs(log_path)
        
        if deleted_count > 0:
            print(f"总共删除了 {deleted_count} 个旧压缩日志文件（超过{days}天）")
        
    except Exception as e:
        print(f"删除旧压缩日志文件失败: {e}")


def _remove_empty_dirs(path: Path):
    """
    递归删除空目录
    """
    try:
        for item in path.iterdir():
            if item.is_dir():
                _remove_empty_dirs(item)
                # 如果目录为空，删除它
                try:
                    if not any(item.iterdir()):
                        item.rmdir()
                        print(f"删除空目录: {item}")
                except OSError:
                    pass
    except Exception as e:
        print(f"删除空目录失败: {e}")


def get_log_statistics(log_dir: str = None):
    """
    获取日志统计信息
    
    Args:
        log_dir: 日志目录
        
    Returns:
        dict: 统计信息
    """
    if log_dir is None:
        log_dir = "logs"
    
    log_path = Path(log_dir)
    if not log_path.exists():
        return {
            'total_files': 0,
            'total_size': 0,
            'compressed_files': 0,
            'compressed_size': 0,
            'by_logger': {}
        }
    
    stats = {
        'total_files': 0,
        'total_size': 0,
        'compressed_files': 0,
        'compressed_size': 0,
        'by_logger': {}
    }
    
    # 统计所有日志文件
    for log_file in log_path.rglob('*.log*'):
        if log_file.is_file():
            file_size = log_file.stat().st_size
            stats['total_files'] += 1
            stats['total_size'] += file_size
            
            if log_file.name.endswith('.gz'):
                stats['compressed_files'] += 1
                stats['compressed_size'] += file_size
            
            # 按日志器统计
            logger_name = log_file.name.split('.')[0]
            if logger_name not in stats['by_logger']:
                stats['by_logger'][logger_name] = {
                    'files': 0,
                    'size': 0
                }
            stats['by_logger'][logger_name]['files'] += 1
            stats['by_logger'][logger_name]['size'] += file_size
    
    return stats


if __name__ == '__main__':
    logger = getLogger('WebAPI')
    
    # 基础日志测试
    logger.info("系统启动")
    logger.debug("调试信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    
    # API调用日志测试
    log_api_call(
        logger=logger,
        user_id="user123",
        endpoint="/api/users/info",
        method="GET",
        params={"id": 123, "fields": ["name", "email"]},
        response_status=200,
        client_ip="192.168.1.100"
    )
    
    log_api_call(
        logger=logger,
        user_id="user456",
        endpoint="/api/users/login",
        method="POST",
        params={"username": "test", "password": "hidden"},  # password会被过滤
        response_status=401,
        client_ip="10.0.0.50"
    )
    
    # 单例验证
    logger2 = getLogger('WebAPI')
    print(f"Logger单例验证: {id(logger) == id(logger2)}")
    
    # 显示日志统计
    stats = get_log_statistics()
    print(f"\n日志统计信息:")
    print(f"总文件数: {stats['total_files']}")
    print(f"总大小: {stats['total_size'] / 1024 / 1024:.2f} MB")
    print(f"压缩文件数: {stats['compressed_files']}")
    print(f"压缩文件大小: {stats['compressed_size'] / 1024 / 1024:.2f} MB")
