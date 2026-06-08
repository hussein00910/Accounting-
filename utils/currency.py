"""Currency formatting utilities."""

_SYMBOLS = {
    'SAR': 'ر.س',
    'AED': 'د.إ',
    'KWD': 'د.ك',
    'BHD': 'د.ب',
    'OMR': 'ر.ع',
    'QAR': 'ر.ق',
    'EGP': 'ج.م',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
}


def format_amount(amount: float, currency: str = 'SAR', arabic: bool = True) -> str:
    symbol = _SYMBOLS.get(currency, currency)
    formatted = f'{amount:,.2f}'
    if arabic:
        return f'{formatted} {symbol}'
    return f'{symbol} {formatted}'


def short_amount(amount: float) -> str:
    if amount >= 1_000_000:
        return f'{amount/1_000_000:.1f}M'
    if amount >= 1_000:
        return f'{amount/1_000:.1f}K'
    return f'{amount:.0f}'
