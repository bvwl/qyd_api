import logging
import os
from logging import Logger
from concurrent_log_handler import ConcurrentRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import gzip
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path


def getLogger(name: str = 'root') -> Logger:
    """
    创建一个按2小时滚动、支持多进程安全、自动压缩日志的 Logger
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

        # 文件处理器：每2小时滚动一次，保留7天，共84个文件，支持多进程写入
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='H',
            interval=2,             # 每2小时切一次
            backupCount=84,         # 保留7天 = 7 * 24 / 2 = 84个文件
            encoding='utf-8',
            delay=False,
            utc=False  # 你也可以改成 True 表示按 UTC 时间切
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

        # 添加压缩功能（在第一次创建 logger 时执行一次）
        _compress_old_logs(log_dir, name)

    return logger


def _compress_old_logs(log_dir: str, name: str):
    """
    将旧日志压缩成 .gz 格式
    """
    pattern = os.path.join(log_dir, f"{name}.log.*")
    for filepath in glob.glob(pattern):
        if filepath.endswith('.gz'):
            continue
        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(filepath + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filepath)
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
    
    _compress_old_logs(log_dir, name)


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
    删除超过指定天数的压缩日志文件
    
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
        
        # 获取所有压缩日志文件
        gz_files = [f for f in log_path.iterdir() 
                   if f.is_file() and f.name.endswith('.log.gz')]
        
        deleted_count = 0
        for gz_file in gz_files:
            # 获取文件修改时间
            file_mtime = datetime.fromtimestamp(gz_file.stat().st_mtime)
            
            # 如果文件超过保留期限，删除它
            if file_mtime < cutoff_time:
                gz_file.unlink()
                print(f"删除旧压缩日志文件: {gz_file}")
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"总共删除了 {deleted_count} 个旧压缩日志文件")
        
    except Exception as e:
        print(f"删除旧压缩日志文件失败: {e}")

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
