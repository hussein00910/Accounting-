"""Date helpers — Arabic month names + formatting."""

from datetime import datetime, timedelta

_AR_MONTHS = [
    '', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
]


def current_month() -> str:
    """Return YYYY-MM string for today."""
    return datetime.now().strftime('%Y-%m')


def month_label(month_str: str, arabic: bool = True) -> str:
    """Convert '2024-03' → 'مارس 2024' or 'March 2024'."""
    try:
        dt = datetime.strptime(month_str, '%Y-%m')
        if arabic:
            return f'{_AR_MONTHS[dt.month]} {dt.year}'
        return dt.strftime('%B %Y')
    except ValueError:
        return month_str


def prev_month(month_str: str) -> str:
    dt = datetime.strptime(month_str + '-01', '%Y-%m-%d')
    first = (dt.replace(day=1) - timedelta(days=1)).replace(day=1)
    return first.strftime('%Y-%m')


def next_month(month_str: str) -> str:
    dt = datetime.strptime(month_str + '-01', '%Y-%m-%d')
    nxt = (dt.replace(day=28) + timedelta(days=4)).replace(day=1)
    return nxt.strftime('%Y-%m')


def format_date(date_str: str, arabic: bool = True) -> str:
    try:
        dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
        if arabic:
            return f'{dt.day} {_AR_MONTHS[dt.month]}'
        return dt.strftime('%d %b')
    except (ValueError, IndexError):
        return date_str[:10]


def days_in_month(month_str: str) -> int:
    dt = datetime.strptime(month_str + '-01', '%Y-%m-%d')
    nxt = (dt.replace(day=28) + timedelta(days=4)).replace(day=1)
    return (nxt - dt).days
