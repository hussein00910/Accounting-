"""
Transactions list with search and category filter.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.chip import MDChip
from kivy.clock import Clock

from core.database import Database
from core.categorizer import all_categories
from utils.date_utils import current_month
from ui.widgets.transaction_card import TransactionCard


class TransactionsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='transactions', **kwargs)
        self._month = current_month()
        self._active_cat = None
        self._search_text = ''

        root = MDBoxLayout(orientation='vertical', padding='12dp', spacing='8dp')

        # Search bar
        self._search = MDTextField(
            hint_text='ابحث عن تاجر أو مبلغ…',
            on_text=self._on_search,
            size_hint_y=None, height='48dp',
        )
        root.add_widget(self._search)

        # Category filter chips
        chip_scroll = MDScrollView(
            size_hint_y=None, height='44dp',
            do_scroll_y=False,
        )
        self._chips_row = MDBoxLayout(
            orientation='horizontal',
            spacing='8dp', padding='4dp',
            adaptive_width=True, size_hint_y=None, height='44dp',
        )
        chip_scroll.add_widget(self._chips_row)
        root.add_widget(chip_scroll)

        # Transaction list
        list_scroll = MDScrollView()
        self._list = MDBoxLayout(
            orientation='vertical',
            spacing='6dp',
            adaptive_height=True,
        )
        list_scroll.add_widget(self._list)
        root.add_widget(list_scroll)
        self.add_widget(root)

    def on_enter(self):
        self._build_chips()
        self._load_transactions()

    def _build_chips(self):
        self._chips_row.clear_widgets()
        all_chip = MDChip(
            text='الكل',
            on_release=lambda *_: self._filter_cat(None),
        )
        self._chips_row.add_widget(all_chip)
        for cat in all_categories():
            if cat['id'] == 'other':
                continue
            c = MDChip(
                text=cat['name'],
                on_release=lambda *_, cid=cat['id']: self._filter_cat(cid),
            )
            self._chips_row.add_widget(c)

    def _filter_cat(self, cat_id):
        self._active_cat = cat_id
        self._load_transactions()

    def _on_search(self, instance, value):
        self._search_text = value.strip()
        Clock.unschedule(self._delayed_search)
        Clock.schedule_once(self._delayed_search, 0.3)

    def _delayed_search(self, *_):
        self._load_transactions()

    def _load_transactions(self):
        self._list.clear_widgets()
        db = Database.get()
        txs = db.get_transactions(
            month=self._month,
            category=self._active_cat,
            limit=300,
        )
        # Client-side search filter
        if self._search_text:
            q = self._search_text.lower()
            txs = [t for t in txs
                   if q in (t.get('merchant') or '').lower()
                   or q in str(t.get('amount', ''))]

        if not txs:
            self._list.add_widget(MDLabel(
                text='لا توجد معاملات',
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None, height='64dp',
            ))
            return

        for tx in txs:
            self._list.add_widget(TransactionCard(tx))
