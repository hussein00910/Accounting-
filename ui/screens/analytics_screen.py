"""
Analytics screen: bar chart (daily spending) + category table.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp

from core.database import Database
from core.categorizer import get_category_meta
from utils.currency import format_amount
from utils.date_utils import current_month, month_label, prev_month, next_month
from ui.widgets.chart_widget import BarChart


class AnalyticsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='analytics', **kwargs)
        self._month = current_month()

        scroll = MDScrollView()
        self._layout = MDBoxLayout(
            orientation='vertical',
            padding='16dp',
            spacing='14dp',
            adaptive_height=True,
        )
        scroll.add_widget(self._layout)
        self.add_widget(scroll)

    def on_enter(self):
        self._rebuild()

    def _rebuild(self):
        self._layout.clear_widgets()
        db = Database.get()

        # Month nav
        nav = MDBoxLayout(orientation='horizontal', size_hint_y=None, height='48dp')
        nav.add_widget(MDIconButton(icon='chevron-right',
                                    on_release=lambda *_: self._change_month(-1)))
        nav.add_widget(MDLabel(text=month_label(self._month), halign='center',
                               font_style='H6', theme_text_color='Primary'))
        nav.add_widget(MDIconButton(icon='chevron-left',
                                    on_release=lambda *_: self._change_month(1)))
        self._layout.add_widget(nav)

        # Daily spending bar chart
        self._layout.add_widget(MDLabel(
            text='الإنفاق اليومي',
            font_style='Subtitle1', bold=True,
            theme_text_color='Primary',
            size_hint_y=None, height='30dp',
        ))
        daily = db.get_daily_spending(self._month)
        bar = BarChart(size_hint_y=None, height='150dp')
        bar.set_data([{'label': d['day'], 'value': d['total']} for d in daily])
        self._layout.add_widget(bar)

        # Category breakdown table
        self._layout.add_widget(MDLabel(
            text='تفصيل حسب الفئة',
            font_style='Subtitle1', bold=True,
            theme_text_color='Primary',
            size_hint_y=None, height='30dp',
        ))
        breakdown = db.get_category_breakdown(self._month)
        summary = db.get_monthly_summary(self._month)
        total = summary['total_debit'] or 1

        if not breakdown:
            self._layout.add_widget(MDLabel(
                text='لا توجد بيانات', halign='center',
                theme_text_color='Secondary', size_hint_y=None, height='48dp',
            ))
            return

        for item in breakdown:
            meta = get_category_meta(item['category'])
            pct = item['total'] / total * 100
            row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None, height='36dp',
                spacing='8dp', padding=('4dp', 0),
            )
            row.add_widget(MDLabel(
                text=meta['name'], font_style='Body2', theme_text_color='Primary',
                size_hint_x=0.45,
            ))
            row.add_widget(MDLabel(
                text=format_amount(item['total']),
                halign='right', font_style='Body2', theme_text_color='Secondary',
                size_hint_x=0.35,
            ))
            row.add_widget(MDLabel(
                text=f"{pct:.1f}%",
                halign='right', font_style='Caption', theme_text_color='Secondary',
                size_hint_x=0.2,
            ))
            self._layout.add_widget(row)

    def _change_month(self, direction: int):
        self._month = prev_month(self._month) if direction < 0 else next_month(self._month)
        self._rebuild()
