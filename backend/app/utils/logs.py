import logging
import os
import re
import reprlib
from logging import Logger
from concurrent_log_handler import ConcurrentRotatingFileHandler
import gzip
import shutil
import glob
import time
from datetime import datetime, timedelta
from pathlib import Path


_BACKEND_DIR = Path(__file__).resolve().parents[2]
_SENSITIVE_KEYS = frozenset({
    "password", "passwd", "token", "access_token", "refresh_token",
    "authorization", "secret", "key", "api_key",
})


def _default_log_dir() -> str:
    configured_log_dir = os.getenv("LOG_DIR")
    if configured_log_dir:
        return str(Path(configured_log_dir).expanduser())
    return str(_BACKEND_DIR / "logs")


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


def _log_level(name: str, fallback: str = "INFO") -> int:
    level_name = os.getenv(name, fallback).upper()
    return getattr(logging, level_name, getattr(logging, fallback, logging.INFO))


def safe_repr(value, max_length: int | None = None) -> str:
    """生成有界 repr，避免日志格式化复制完整的大对象。"""
    limit = max_length or _env_int("LOG_MAX_VALUE_LENGTH", 1024, minimum=64)
    formatter = reprlib.Repr()
    formatter.maxstring = limit
    formatter.maxother = limit
    formatter.maxlist = 20
    formatter.maxtuple = 20
    formatter.maxset = 20
    formatter.maxfrozenset = 20
    formatter.maxdict = 20
    result = formatter.repr(value)
    if len(result) > limit:
        suffix = "...<truncated>"
        return f"{result[:max(0, limit - len(suffix))]}{suffix}"[-limit:]
    return result


def sanitize_mapping(values: dict | None) -> dict:
    """过滤敏感字段，并限制单个日志字段的长度。"""
    if not values:
        return {}
    safe_values = {}
    max_value_length = _env_int("LOG_MAX_VALUE_LENGTH", 1024, minimum=64)
    for key, value in values.items():
        key_text = str(key)
        if key_text.lower() in _SENSITIVE_KEYS:
            safe_values[key_text] = "***"
        elif isinstance(value, str) and len(value) > max_value_length:
            safe_values[key_text] = f"{value[:max_value_length]}...<truncated>"
        else:
            safe_values[key_text] = value
    return safe_values


class BoundedFormatter(logging.Formatter):
    """限制单条日志长度，防止异常或请求参数生成超大日志。"""

    def __init__(self, *args, max_length: int = 8192, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = max_length

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if len(message) <= self.max_length:
            return message
        suffix = f"...<truncated {len(message) - self.max_length} chars>"
        prefix_length = max(0, self.max_length - len(suffix))
        return f"{message[:prefix_length]}{suffix}"[-self.max_length:]


def getLogger(name: str = 'root') -> Logger:
    """
    创建支持多进程滚动的 Logger。

    日志直接同步写入有界滚动文件，不使用无界内存队列。所有级别、文件
    大小和保留数量均可通过环境变量配置。
    :param name: 日志器名称
    :return: 单例 Logger 对象
    """
    normalized_name = name or "root"
    logger: Logger = logging.getLogger(normalized_name)
    logger_level = _log_level("LOG_LEVEL", "INFO")
    logger.setLevel(logger_level)
    # 自定义 handler 已经负责输出；禁止继续传播到 root，避免控制台重复日志。
    logger.propagate = False

    managed_handlers = [
        handler for handler in logger.handlers
        if getattr(handler, "_qyd_managed_handler", False)
    ]
    if not managed_handlers:
        # 控制台输出
        console_handler = None
        if _env_bool("LOG_ENABLE_CONSOLE", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(_log_level("LOG_CONSOLE_LEVEL", logging.getLevelName(logger_level)))
            console_handler._qyd_managed_handler = True

        # 日志目录
        configured_log_dir = os.getenv("LOG_DIR")
        log_dir = Path(configured_log_dir).expanduser() if configured_log_dir else _BACKEND_DIR / "logs"
        file_handler = None
        if _env_bool("LOG_ENABLE_FILE", True):
            log_dir.mkdir(parents=True, exist_ok=True)

            # logger 名称不能影响日志目录结构。
            safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", normalized_name)
            log_file = log_dir / f"{safe_name}.log"

            # 默认每类日志最多约 200MB（20MB * 当前文件及 9 个备份）。
            file_handler = ConcurrentRotatingFileHandler(
                filename=str(log_file),
                mode="a",
                maxBytes=_env_int("LOG_MAX_BYTES", 20 * 1024 * 1024),
                backupCount=_env_int("LOG_BACKUP_COUNT", 9),
                encoding="utf-8",
                delay=True,
                use_gzip=False,
            )
            file_handler.setLevel(_log_level("LOG_FILE_LEVEL", logging.getLevelName(logger_level)))
            file_handler._qyd_managed_handler = True

        # 设置 Formatter - 简化格式，去掉路径信息
        max_message_length = _env_int("LOG_MAX_MESSAGE_LENGTH", 8192, minimum=256)
        formatter = BoundedFormatter(
            fmt="【{name}】{levelname} {asctime} {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
            max_length=max_message_length,
        )
        console_formatter = BoundedFormatter(
            fmt="{levelname} {asctime} {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
            max_length=max_message_length,
        )

        if file_handler:
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        if console_handler:
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    else:
        # 配置热加载/测试修改环境变量后，再次获取 logger 时同步级别。
        for handler in managed_handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(
                handler, ConcurrentRotatingFileHandler
            ):
                handler.setLevel(_log_level("LOG_CONSOLE_LEVEL", logging.getLevelName(logger_level)))
            else:
                handler.setLevel(_log_level("LOG_FILE_LEVEL", logging.getLevelName(logger_level)))

    return logger


def _compress_and_organize_logs(
    log_dir: str,
    name: str,
    min_age_seconds: int = 0,
    compress_level: int = 3,
) -> int:
    """
    将旧日志压缩并按照 日志名称/年/月/日 的目录结构组织
    例如: logs/api/2026/02/22/api.log.1.gz
    """
    pattern = os.path.join(log_dir, f"{name}.log.*")
    compressed_count = 0
    now = time.time()
    for filepath in glob.glob(pattern):
        if filepath.endswith((".gz", ".tmp")):
            continue
        
        claimed_path = None
        try:
            source_stat = os.stat(filepath)
            # 刚轮转的文件仍可能被多进程 handler 重命名，等待其稳定后再压缩。
            if now - source_stat.st_mtime < min_age_seconds:
                continue

            # 先原子改名认领文件，避免多压缩进程重复处理，也避免滚动过程中
            # 删除一个刚刚复用同名的新文件。上次异常遗留的认领文件可直接续压。
            if ".compressing-" in filepath:
                claimed_path = filepath
            else:
                claimed_path = f"{filepath}.compressing-{os.getpid()}-{time.time_ns()}"
                os.rename(filepath, claimed_path)
                source_stat = os.stat(claimed_path)

            # 使用文件修改时间来组织目录结构
            file_mtime = datetime.fromtimestamp(source_stat.st_mtime)
            year = file_mtime.strftime('%Y')
            month = file_mtime.strftime('%m')
            day = file_mtime.strftime('%d')
            
            # 创建目标目录结构: logs/日志名称/年/月/日
            target_dir = os.path.join(log_dir, name, year, month, day)
            os.makedirs(target_dir, exist_ok=True)
            
            # 压缩文件
            filename = os.path.basename(filepath).split(".compressing-", 1)[0]
            gz_filename = filename + '.gz'
            target_path = os.path.join(target_dir, gz_filename)
            
            # 如果目标文件已存在，添加时间戳避免覆盖
            if os.path.exists(target_path):
                timestamp = time.time_ns()
                gz_filename = f"{filename}.{timestamp}.gz"
                target_path = os.path.join(target_dir, gz_filename)

            # 先写临时文件，完整成功后再原子发布，失败时不会留下损坏的 .gz。
            temp_path = f"{target_path}.{os.getpid()}.tmp"
            try:
                with open(claimed_path, "rb") as f_in, open(temp_path, "wb") as raw_out:
                    with gzip.GzipFile(
                        filename="",
                        mode="wb",
                        compresslevel=min(9, max(1, compress_level)),
                        fileobj=raw_out,
                        mtime=int(source_stat.st_mtime),
                    ) as f_out:
                        shutil.copyfileobj(f_in, f_out, length=1024 * 1024)

                os.replace(temp_path, target_path)
                os.utime(target_path, (source_stat.st_atime, source_stat.st_mtime))
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise

            # 删除原文件
            os.remove(claimed_path)
            compressed_count += 1
                
        except Exception as e:
            # 如果本轮已认领但尚未产生同名新滚动文件，尽量恢复原名。
            if claimed_path and claimed_path != filepath and os.path.exists(claimed_path):
                try:
                    if not os.path.exists(filepath):
                        os.rename(claimed_path, filepath)
                except OSError:
                    pass
            print(f"日志压缩失败: {filepath}, 原因: {e}")

    return compressed_count


def compress_old_logs(
    log_dir: str = None,
    name: str = "root",
    min_age_seconds: int = 0,
    compress_level: int = 3,
) -> int:
    """
    压缩旧的日志文件（公共接口）
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
        name: 日志器名称
    """
    if log_dir is None:
        log_dir = _default_log_dir()
    
    return _compress_and_organize_logs(log_dir, name, min_age_seconds, compress_level)


def compress_all_logs(
    log_dir: str = None,
    min_age_seconds: int | None = None,
) -> int:
    """
    压缩所有日志模块的旧日志文件，并按目录结构组织
    
    Args:
        log_dir: 日志目录，如果不指定则使用默认目录
    """
    if log_dir is None:
        log_dir = _default_log_dir()
    if min_age_seconds is None:
        min_age_seconds = _env_int("LOG_COMPRESS_MIN_AGE_SECONDS", 300, minimum=0)
    compress_level = _env_int("LOG_COMPRESS_LEVEL", 3)
    
    if not os.path.exists(log_dir):
        return 0
    
    # 同时从当前日志和滚动日志识别模块，避免当前文件暂时不存在时漏压缩。
    logger_names = set()
    for filename in os.listdir(log_dir):
        if ".log" in filename and not filename.endswith((".gz", ".tmp")):
            logger_names.add(filename.split(".log", 1)[0])
    
    # 压缩每个模块的旧日志
    compressed_count = 0
    for logger_name in logger_names:
        compressed_count += _compress_and_organize_logs(
            log_dir,
            logger_name,
            min_age_seconds=min_age_seconds,
            compress_level=compress_level,
        )
    
    # 压缩与删除解耦：这里不自动批量删除归档文件。
    return compressed_count


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
            safe_params = sanitize_mapping(params)
            if safe_params:
                log_parts.append(f"参数={safe_repr(safe_params)}")
        
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
            log_dir = _default_log_dir()
        
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
        log_dir = _default_log_dir()
    
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
