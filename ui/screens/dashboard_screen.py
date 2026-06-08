"""
Main dashboard: monthly summary, spending pie chart, recent transactions.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
from kivy.metrics import dp

from core.database import Database
from core.categorizer import get_category_meta, all_categories
from utils.currency import format_amount
from utils.date_utils import current_month, month_label, prev_month, next_month
from ui.widgets.chart_widget import PieChart
from ui.widgets.transaction_card import TransactionCard
from ui.widgets.summary_widget import SummaryCard


_CATEGORY_COLORS = {
    'food':          (1.0, 0.42, 0.42),
    'shopping':      (0.31, 0.80, 0.78),
    'fuel':          (0.27, 0.72, 0.82),
    'health':        (0.59, 0.81, 0.71),
    'subscriptions': (1.0, 0.92, 0.42),
    'bills':         (0.87, 0.63, 0.87),
    'transfer':      (0.45, 0.72, 1.0),
    'entertainment': (0.99, 0.47, 0.66),
    'other':         (0.70, 0.74, 0.76),
}


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='dashboard', **kwargs)
        self._month = current_month()

        scroll = MDScrollView()
        self._layout = MDBoxLayout(
            orientation='vertical',
            padding='16dp',
            spacing='12dp',
            adaptive_height=True,
        )
        scroll.add_widget(self._layout)
        self.add_widget(scroll)

    def on_enter(self):
        self._rebuild()

    def _rebuild(self):
        self._layout.clear_widgets()
        db = Database.get()

        # ── Month navigation ────────────────────────────────────────────────
        nav = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None, height='48dp',
            spacing='8dp',
        )
        nav.add_widget(MDIconButton(
            icon='chevron-right',
            on_release=lambda *_: self._change_month(-1),
        ))
        nav.add_widget(MDLabel(
            text=month_label(self._month),
            halign='center',
            font_style='H6',
            theme_text_color='Primary',
        ))
        nav.add_widget(MDIconButton(
            icon='chevron-left',
            on_release=lambda *_: self._change_month(1),
        ))
        self._layout.add_widget(nav)

        # ── Summary cards ───────────────────────────────────────────────────
        summary = db.get_monthly_summary(self._month)
        total_debit = summary['total_debit'] or 0
        total_credit = summary['total_credit'] or 0

        grid = MDGridLayout(
            cols=2, spacing='10dp',
            size_hint_y=None, height='110dp',
        )
        grid.add_widget(SummaryCard(
            title='إجمالي المصروفات',
            value=format_amount(total_debit),
            value_color=(1, 0.35, 0.35, 1),
        ))
        grid.add_widget(SummaryCard(
            title='إجمالي الإيرادات',
            value=format_amount(total_credit),
            value_color=(0.2, 0.8, 0.4, 1),
        ))
        self._layout.add_widget(grid)

        # ── Pie chart + category breakdown ─────────────────────────────────
        breakdown = db.get_category_breakdown(self._month)

        self._layout.add_widget(MDLabel(
            text='توزيع المصروفات',
            font_style='Subtitle1',
            theme_text_color='Primary',
            size_hint_y=None, height='32dp',
            bold=True,
        ))

        chart_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None, height='180dp',
            spacing='12dp',
        )

        pie = PieChart(size_hint_x=0.45)
        segments = [
            (item['total'], _CATEGORY_COLORS.get(item['category'], (0.7, 0.7, 0.7)))
            for item in breakdown
        ]
        pie.set_data(segments)
        chart_row.add_widget(pie)

        legend = MDBoxLayout(orientation='vertical', spacing='4dp', size_hint_x=0.55)
        for item in breakdown[:6]:
            meta = get_category_meta(item['category'])
            pct = (item['total'] / total_debit * 100) if total_debit else 0
            row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height='26dp')
            row.add_widget(MDLabel(
                text=f"● {meta['name']}",
                theme_text_color='Primary', font_style='Caption',
            ))
            row.add_widget(MDLabel(
                text=f"{pct:.0f}%",
                halign='right', theme_text_color='Secondary', font_style='Caption',
            ))
            legend.add_widget(row)
        chart_row.add_widget(legend)
        self._layout.add_widget(chart_row)

        # ── Budget progress bars ───────────────────────────────────────────────
        budgets = db.get_budgets()
        if budgets:
            self._layout.add_widget(MDLabel(
                text='الميزانية الشهرية',
                font_style='Subtitle1',
                theme_text_color='Primary',
                size_hint_y=None, height='32dp',
                bold=True,
            ))
            spend_map = {r['category']: r['total'] for r in breakdown}
            for b in budgets:
                cat = b['category']
                limit = b['monthly_limit']
                spent = spend_map.get(cat, 0)
                pct = min(spent / limit, 1.0) if limit else 0
                meta = get_category_meta(cat)

                brow = MDBoxLayout(
                    orientation='vertical',
                    size_hint_y=None, height='52dp',
                    spacing='4dp',
                )
                lbl_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height='20dp')
                lbl_row.add_widget(MDLabel(text=meta['name'], font_style='Caption',
                                           theme_text_color='Primary'))
                lbl_row.add_widget(MDLabel(
                    text=f"{format_amount(spent)} / {format_amount(limit)}",
                    halign='right', font_style='Caption', theme_text_color='Secondary',
                ))
                brow.add_widget(lbl_row)
                bar = MDProgressBar(value=pct * 100, max=100, size_hint_y=None, height='8dp')
                if pct >= 0.9:
                    bar.color = (1, 0.3, 0.3, 1)
                elif pct >= 0.7:
                    bar.color = (1, 0.7, 0.2, 1)
                else:
                    bar.color = (0.2, 0.8, 0.4, 1)
                brow.add_widget(bar)
                self._layout.add_widget(brow)

        # ── Recent transactions ───────────────────────────────────────────────
        self._layout.add_widget(MDLabel(
            text='آخر المعاملات',
            font_style='Subtitle1',
            theme_text_color='Primary',
            size_hint_y=None, height='32dp',
            bold=True,
        ))

        recent = db.get_transactions(month=self._month, limit=10)
        if not recent:
            self._layout.add_widget(MDLabel(
                text='لا توجد معاملات هذا الشهر',
                theme_text_color='Secondary',
                halign='center',
                size_hint_y=None, height='48dp',
            ))
        for tx in recent:
            card = TransactionCard(tx, on_tap=self._open_tx)
            self._layout.add_widget(card)

        # See all
        see_all = MDFlatButton(
            text='عرض الكل',
            theme_text_color='Custom',
            text_color=(0.3, 0.7, 1, 1),
            pos_hint={'center_x': 0.5},
            on_release=lambda *_: self._go_transactions(),
        )
        self._layout.add_widget(see_all)

    def _change_month(self, direction: int):
        if direction < 0:
            self._month = prev_month(self._month)
        else:
            self._month = next_month(self._month)
        self._rebuild()

    def _open_tx(self, tx: dict):
        pass  # TODO: open transaction detail sheet

    def _go_transactions(self):
        self.manager.current = 'transactions'
