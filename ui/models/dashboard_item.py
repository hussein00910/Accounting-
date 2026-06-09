"""
DashboardItem — data model for Smart Accountant dashboard cards.
"""
from dataclasses import dataclass


@dataclass
class DashboardItem:
    item_id: str
    icon: str
    title: str
    balance: float = 0.0
    currency: str = 'YER'
    show_balance: bool = True
    route: str = ''


DASHBOARD_ITEMS: list = [
    DashboardItem('customers',    'account-group',   'العملاء',         currency='YER', route='customers'),
    DashboardItem('suppliers',    'truck-delivery',  'الموردين',        currency='YER', route='suppliers'),
    DashboardItem('employees',    'account-tie',     'الموظفين',        currency='YER', route='employees'),
    DashboardItem('debts',        'credit-card',     'الديون',          currency='YER', route='debts'),
    DashboardItem('expenses',     'cash-minus',      'الصرفيات',        currency='YER', route='expenses'),
    DashboardItem('other',        'dots-horizontal', 'أخرى',            currency='YER', route='other_accounts'),
    DashboardItem('measurements', 'ruler',           'تمتير ومقاسات',   show_balance=False, route='measurements'),
    DashboardItem('new_measure',  'plus-circle',     'مقاس جديد',       show_balance=False, route='new_measurement'),
]
