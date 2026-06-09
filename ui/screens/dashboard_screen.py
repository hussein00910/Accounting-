"""
المحاسب الذكي — Smart Accountant main dashboard.
Deep Blue / DeepOrange Light theme, RTL Arabic layout.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.chip import MDChip
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from core.database import Database
from ui.models.dashboard_item import DASHBOARD_ITEMS, DashboardItem


_BLUE   = (0.13, 0.59, 0.95, 1)
_ORANGE = (1.0,  0.34, 0.13, 1)
_GREY   = (0.90, 0.90, 0.90, 1)

_QUICK_ACTIONS = [
    ('البحث السريع',    False),
    ('صرف عملات',       False),
    ('فاتورة جديدة',    False),
    ('صناديق النقدية',  False),
    ('الحركة اليومية',  False),
    ('قيد بسيط',        False),
    ('كشف حساب',        True),
    ('حوالة جديدة',     True),
    ('سند جديد',        True),
]

_SOCIAL_ICONS = [
    ('telegram',  'telegram'),
    ('youtube',   'youtube'),
    ('facebook',  'facebook'),
    ('whatsapp',  'whatsapp'),
]

APP_VERSION = '135.1.2'


class DashboardCard(MDCard):
    def __init__(self, item: DashboardItem, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self._item = item
        self.orientation = 'vertical'
        self.padding = (dp(10), dp(12))
        self.spacing = dp(4)
        self.radius = [dp(12)]
        self.elevation = 1
        self.shadow_softness = 4
        self.md_bg_color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(115)

        with self.canvas.before:
            Color(0.13, 0.59, 0.95, 0.30)
            self._border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._sync_border, size=self._sync_border)

        icon_lbl = MDLabel(
            text='\U000f0004',   # placeholder — MDIcon via font
            font_style='H5',
            halign='center',
            theme_text_color='Custom',
            text_color=_BLUE,
            size_hint_y=None,
            height=dp(36),
        )
        # Use MDIconButton as icon display (simpler than MDIcon in pure Python)
        icon_btn = MDIconButton(
            icon=item.icon,
            theme_text_color='Custom',
            text_color=_BLUE,
            disabled=True,
            size_hint=(1, None),
            height=dp(36),
            pos_hint={'center_x': 0.5},
        )

        title_lbl = MDLabel(
            text=item.title,
            font_style='Subtitle2',
            halign='center',
            theme_text_color='Primary',
            size_hint_y=None,
            height=dp(24),
            bold=True,
        )

        self._balance_label = MDLabel(
            text='',
            font_style='Caption',
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(18),
        )

        self.add_widget(icon_btn)
        self.add_widget(title_lbl)
        if item.show_balance:
            self.add_widget(self._balance_label)

        if on_tap:
            self.bind(on_release=lambda *_: on_tap(item.item_id))

    def _sync_border(self, *_):
        self._border.pos = self.pos
        self._border.size = self.size


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='dashboard', **kwargs)
        self._balance_labels: dict = {}

        root_float = FloatLayout()

        vbox = MDBoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
        )
        vbox.add_widget(self._build_top_bar())

        scroll = MDScrollView(size_hint=(1, 1))
        content = MDBoxLayout(
            orientation='vertical',
            padding=(dp(12), dp(8), dp(12), dp(72)),
            spacing=dp(10),
            adaptive_height=True,
        )
        content.add_widget(self._build_quick_actions())
        content.add_widget(self._build_cards_grid())
        content.add_widget(self._build_footer())
        scroll.add_widget(content)
        vbox.add_widget(scroll)

        root_float.add_widget(vbox)

        fab = MDFloatingActionButton(
            icon='plus',
            md_bg_color=_ORANGE,
            pos_hint={'right': 0.95, 'y': 0.03},
        )
        root_float.add_widget(fab)

        self.add_widget(root_float)

    def on_enter(self):
        Clock.schedule_once(self._load_balances, 0)

    def _load_balances(self, *_):
        db = Database.get()
        balance_map = {
            'customers': db.get_customers_balance(),
            'suppliers': db.get_suppliers_balance(),
            'employees': db.get_employees_balance(),
            'debts':     db.get_debts_total(),
            'expenses':  db.get_expenses_total(),
            'other':     0.0,
        }
        for item_id, lbl in self._balance_labels.items():
            val = balance_map.get(item_id, 0.0)
            lbl.text = f'{val:,.0f} ري'

    def _build_top_bar(self):
        return MDTopAppBar(
            title='المحاسب الذكي',
            anchor_title='center',
            left_action_items=[['menu', lambda x: None]],
            right_action_items=[
                ['magnify', lambda x: None],
                ['bell',    lambda x: None],
                ['sync',    lambda x: None],
                ['plus',    lambda x: None],
            ],
            elevation=2,
        )

    def _build_quick_actions(self):
        chip_scroll = MDScrollView(
            size_hint_y=None,
            height=dp(52),
            do_scroll_y=False,
            bar_width=0,
        )
        row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(6),
            padding=(dp(4), dp(6)),
            adaptive_width=True,
            size_hint_y=None,
            height=dp(52),
        )
        for label, is_highlighted in _QUICK_ACTIONS:
            chip = MDChip(
                text=label,
                type='suggestion',
                md_bg_color=_BLUE if is_highlighted else _GREY,
            )
            if is_highlighted:
                for child in chip.children:
                    if hasattr(child, 'theme_text_color'):
                        child.theme_text_color = 'Custom'
                        child.text_color = (1, 1, 1, 1)
            row.add_widget(chip)
        chip_scroll.add_widget(row)
        return chip_scroll

    def _build_cards_grid(self):
        grid = MDGridLayout(
            cols=2,
            spacing=dp(10),
            padding=(0, dp(4)),
            adaptive_height=True,
        )
        for item in DASHBOARD_ITEMS:
            card = DashboardCard(item, on_tap=self._on_card_tap)
            if item.show_balance:
                self._balance_labels[item.item_id] = card._balance_label
            grid.add_widget(card)
        return grid

    def _build_footer(self):
        footer = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            spacing=dp(4),
            padding=(0, dp(8)),
        )
        footer.add_widget(MDLabel(
            text=f'الإصدار {APP_VERSION}',
            halign='center',
            theme_text_color='Secondary',
            font_style='Caption',
            size_hint_y=None,
            height=dp(20),
        ))
        icons_row = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(4),
            pos_hint={'center_x': 0.5},
        )
        for icon_name, _ in _SOCIAL_ICONS:
            icons_row.add_widget(MDIconButton(
                icon=icon_name,
                theme_text_color='Custom',
                text_color=_BLUE,
            ))
        footer.add_widget(icons_row)
        return footer

    def _on_card_tap(self, item_id: str):
        pass
