"""
错误追踪工具
用于避免重复记录相同的错误日志
"""
import time
import os
from collections import OrderedDict
from typing import Dict, Tuple
from threading import Lock


class ErrorTracker:
    """错误追踪器 - 避免重复记录相同错误"""
    
    def __init__(self, window_seconds: int = 300, max_entries: int = 2048):
        """
        初始化错误追踪器
        
        Args:
            window_seconds: 时间窗口（秒），在此时间内相同错误只记录一次
        """
        self.window_seconds = max(1, window_seconds)
        self.max_entries = max(1, max_entries)
        # 有序且有容量上限，避免不同错误文本持续产生时无限占用内存。
        self._errors: OrderedDict[str, Tuple[int, int]] = OrderedDict()
        self._lock = Lock()

    def _cleanup_expired(self, current_time: int) -> None:
        """锁内清理；记录按时间排序，因此只需从最旧项开始处理。"""
        while self._errors:
            oldest_key = next(iter(self._errors))
            first_time, _ = self._errors[oldest_key]
            if current_time - first_time < self.window_seconds:
                break
            self._errors.popitem(last=False)
    
    def should_log(self, error_key: str) -> Tuple[bool, int]:
        """
        检查是否应该记录此错误
        
        Args:
            error_key: 错误的唯一标识（通常是错误消息的关键部分）
            
        Returns:
            Tuple[bool, int]: (是否应该记录, 累计次数)
        """
        current_time = int(time.time())
        # 错误消息可能包含动态数据；限制 key 长度也限制字符串本身的内存。
        error_key = str(error_key)[:256]
        
        with self._lock:
            self._cleanup_expired(current_time)
            if error_key in self._errors:
                first_time, count = self._errors[error_key]
                self._errors[error_key] = (first_time, count + 1)
                return False, count + 1
            else:
                # 首次出现，记录
                self._errors[error_key] = (current_time, 1)
                if len(self._errors) > self.max_entries:
                    self._errors.popitem(last=False)
                return True, 1
    
    def cleanup(self):
        """清理过期的错误记录"""
        current_time = int(time.time())
        
        with self._lock:
            self._cleanup_expired(current_time)
    
    def get_stats(self) -> Dict[str, int]:
        """获取错误统计信息"""
        with self._lock:
            return {key: count for key, (_, count) in self._errors.items()}


# 全局错误追踪器实例
try:
    _max_entries = int(os.getenv("ERROR_TRACKER_MAX_ENTRIES", "2048"))
except ValueError:
    _max_entries = 2048

_global_tracker = ErrorTracker(window_seconds=300, max_entries=_max_entries)  # 5分钟窗口


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
