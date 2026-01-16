from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, field_serializer

CN_TZ = timezone(timedelta(hours=8))


def now_cn() -> datetime:
    """
    获取中国时区的当前时间
    返回带有中国时区信息的 datetime 对象
    """
    return datetime.now(CN_TZ)


def parse_time(val: str | int | None, is_end: bool = False) -> datetime | None:
    """
    将传入的字符串或时间戳解析为中国时区的 datetime，用于数据库查询时间比较。
    支持格式:
    - "YYYY-MM-DD"
    - "YYYY-MM-DD HH:mm:ss"
    - 10 位时间戳（秒）
    - 13 位时间戳（毫秒）
    """
    if val is None:
        return None

    dt_cn: datetime

    if isinstance(val, int) or (isinstance(val, str) and val.isdigit()):
        ts = int(val)
        # 根据量级判断是秒还是毫秒
        if ts >= 10 ** 12:
            dt_cn = datetime.fromtimestamp(ts / 1000, CN_TZ)
        else:
            dt_cn = datetime.fromtimestamp(ts, CN_TZ)
    else:
        try:
            dt_cn = datetime.strptime(val, "%Y-%m-%d").replace(tzinfo=CN_TZ)
            if is_end:
                dt_cn = dt_cn.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            try:
                dt_cn = datetime.strptime(val, "%Y-%m-%d %H:%M:%S").replace(tzinfo=CN_TZ)
            except ValueError:
                raise ValueError("时间格式错误，支持 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:mm:ss' 或 10/13位时间戳")

    # 与 ORM 配置保持一致（use_tz=False），返回本地时区的“朴素”时间
    return dt_cn.replace(tzinfo=None)


# 自动把 datetime 序列化为 13位时间戳的基类
class TimestampModel(BaseModel):
    """自动把 datetime 序列化为 13位时间戳的基类"""

    model_config = {"arbitrary_types_allowed": True}

    @field_serializer("*", when_used="json", check_fields=False)  # "*" 表示作用于所有字段
    def serialize_datetime(self, value):
        if isinstance(value, datetime):
            return int(value.timestamp() * 1000)  # 转成 13 位 int 时间戳
        return value
