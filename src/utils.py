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


def truncate(text: str, max_len: int = 200) -> str:
    """截断文本，超出部分以 ... 结尾"""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text
