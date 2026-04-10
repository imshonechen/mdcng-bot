from datetime import datetime


def format_date(date_str: str) -> str:
    """将 '2025-03-15' 格式化为 '2025年3月15日'"""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except ValueError:
        return date_str


def format_datetime(dt_str: str) -> str:
    """将 ISO 时间戳格式化为 '2025年3月15日 14:30:00'"""
    if not dt_str:
        return ""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            return f"{dt.year}年{dt.month}月{dt.day}日 {dt.strftime('%H:%M:%S')}"
        except ValueError:
            continue
    return dt_str


def truncate(text: str, max_len: int = 200) -> str:
    """截断文本，超出部分以 ... 结尾"""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text
