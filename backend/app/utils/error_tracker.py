"""
错误追踪工具
用于避免重复记录相同的错误日志
"""
import time
from typing import Dict, Tuple
from threading import Lock


class ErrorTracker:
    """错误追踪器 - 避免重复记录相同错误"""
    
    def __init__(self, window_seconds: int = 300):
        """
        初始化错误追踪器
        
        Args:
            window_seconds: 时间窗口（秒），在此时间内相同错误只记录一次
        """
        self.window_seconds = window_seconds
        self._errors: Dict[str, Tuple[int, int]] = {}  # {error_key: (first_time, count)}
        self._lock = Lock()
    
    def should_log(self, error_key: str) -> Tuple[bool, int]:
        """
        检查是否应该记录此错误
        
        Args:
            error_key: 错误的唯一标识（通常是错误消息的关键部分）
            
        Returns:
            Tuple[bool, int]: (是否应该记录, 累计次数)
        """
        current_time = int(time.time())
        
        with self._lock:
            if error_key in self._errors:
                first_time, count = self._errors[error_key]
                
                # 检查是否在时间窗口内
                if current_time - first_time < self.window_seconds:
                    # 在时间窗口内，增加计数但不记录
                    self._errors[error_key] = (first_time, count + 1)
                    return False, count + 1
                else:
                    # 超出时间窗口，重置计数并记录
                    self._errors[error_key] = (current_time, 1)
                    return True, 1
            else:
                # 首次出现，记录
                self._errors[error_key] = (current_time, 1)
                return True, 1
    
    def cleanup(self):
        """清理过期的错误记录"""
        current_time = int(time.time())
        
        with self._lock:
            expired_keys = [
                key for key, (first_time, _) in self._errors.items()
                if current_time - first_time >= self.window_seconds
            ]
            
            for key in expired_keys:
                del self._errors[key]
    
    def get_stats(self) -> Dict[str, int]:
        """获取错误统计信息"""
        with self._lock:
            return {key: count for key, (_, count) in self._errors.items()}


# 全局错误追踪器实例
_global_tracker = ErrorTracker(window_seconds=300)  # 5分钟窗口


def should_log_error(error_key: str) -> Tuple[bool, int]:
    """
    检查是否应该记录此错误（全局函数）
    
    Args:
        error_key: 错误的唯一标识
        
    Returns:
        Tuple[bool, int]: (是否应该记录, 累计次数)
    """
    return _global_tracker.should_log(error_key)


def cleanup_error_tracker():
    """清理过期的错误记录（全局函数）"""
    _global_tracker.cleanup()


def get_error_stats() -> Dict[str, int]:
    """获取错误统计信息（全局函数）"""
    return _global_tracker.get_stats()
