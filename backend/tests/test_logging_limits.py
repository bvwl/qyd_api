import logging
import logging.handlers
import importlib.util
import sys
import types
from pathlib import Path


UTILS_DIR = Path(__file__).resolve().parents[1] / "app" / "utils"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# 本组测试不落盘；本机未安装可选处理器时，用标准类完成模块加载。
if "concurrent_log_handler" not in sys.modules:
    try:
        import concurrent_log_handler  # noqa: F401
    except ModuleNotFoundError:
        fallback = types.ModuleType("concurrent_log_handler")
        fallback.ConcurrentRotatingFileHandler = logging.handlers.RotatingFileHandler
        sys.modules["concurrent_log_handler"] = fallback


logs_module = _load_module("qyd_logs_for_test", UTILS_DIR / "logs.py")
error_tracker_module = _load_module("qyd_error_tracker_for_test", UTILS_DIR / "error_tracker.py")

BoundedFormatter = logs_module.BoundedFormatter
getLogger = logs_module.getLogger
safe_repr = logs_module.safe_repr
sanitize_mapping = logs_module.sanitize_mapping
ErrorTracker = error_tracker_module.ErrorTracker


def test_logger_respects_configured_level_and_stops_propagation(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("LOG_ENABLE_CONSOLE", "0")
    monkeypatch.setenv("LOG_ENABLE_FILE", "0")

    logger = getLogger("test_logging_limits_level")

    assert logger.level == logging.WARNING
    assert not logger.isEnabledFor(logging.INFO)
    assert logger.propagate is False


def test_formatter_and_values_have_hard_size_limits(monkeypatch):
    monkeypatch.setenv("LOG_MAX_VALUE_LENGTH", "128")
    formatter = BoundedFormatter("%(message)s", max_length=128)
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="x" * 10_000,
        args=(),
        exc_info=None,
    )

    assert len(formatter.format(record)) <= 128
    assert len(safe_repr(["x" * 10_000] * 1_000)) <= 128


def test_sensitive_values_are_redacted(monkeypatch):
    monkeypatch.setenv("LOG_MAX_VALUE_LENGTH", "64")

    values = sanitize_mapping({"password": "secret", "token": "abc", "query": "x" * 200})

    assert values["password"] == "***"
    assert values["token"] == "***"
    assert len(values["query"]) < 200


def test_error_tracker_is_bounded_and_deduplicates():
    tracker = ErrorTracker(window_seconds=300, max_entries=3)

    assert tracker.should_log("same-error") == (True, 1)
    assert tracker.should_log("same-error") == (False, 2)
    for index in range(10):
        tracker.should_log(f"dynamic-error-{index}")

    stats = tracker.get_stats()
    assert len(stats) == 3
    assert "dynamic-error-9" in stats


def test_error_key_length_is_bounded():
    tracker = ErrorTracker(window_seconds=300, max_entries=3)
    tracker.should_log("x" * 10_000)

    assert max(map(len, tracker.get_stats())) == 256
