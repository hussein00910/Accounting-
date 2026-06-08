"""Single transaction row widget."""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from core.categorizer import get_category_meta
from utils.currency import format_amount
from utils.date_utils import format_date


class TransactionCard(MDCard):
    tx_id = NumericProperty(0)
    merchant = StringProperty('')
    amount = NumericProperty(0)
    currency = StringProperty('SAR')
    date = StringProperty('')
    category = StringProperty('other')
    tx_type = StringProperty('debit')

    def __init__(self, tx: dict, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self.tx_id = tx.get('id', 0)
        self.merchant = tx.get('merchant') or tx.get('bank_id', '')
        self.amount = tx.get('amount', 0)
        self.currency = tx.get('currency', 'SAR')
        self.date = tx.get('date', '')
        self.category = tx.get('category', 'other')
        self.tx_type = tx.get('type', 'debit')
        self._on_tap = on_tap

        self.orientation = 'horizontal'
        self.padding = '12dp'
        self.spacing = '10dp'
        self.size_hint_y = None
        self.height = '72dp'
        self.radius = [10]
        self.elevation = 1
        self.md_bg_color = (0.14, 0.14, 0.16, 1)

        meta = get_category_meta(self.category)

        # Category color dot
        from kivy.uix.widget import Widget
        from kivy.graphics import Color, Ellipse
        dot = Widget(size_hint=(None, None), size=('10dp', '10dp'))
        r, g, b = self._hex_to_rgb(meta['color'])
        with dot.canvas:
            Color(r, g, b, 1)
            dot.ellipse = Ellipse(pos=dot.pos, size=dot.size)
        dot.bind(pos=lambda w, v: setattr(w.ellipse, 'pos', v))

        # Left info
        info = MDBoxLayout(orientation='vertical', adaptive_height=True,
                           size_hint_x=1)
        name = self.merchant or meta['name']
        info.add_widget(MDLabel(
            text=name[:30],
            font_style='Body1',
            theme_text_color='Primary',
            size_hint_y=None, height='24dp',
        ))
        info.add_widget(MDLabel(
            text=format_date(self.date),
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_y=None, height='18dp',
        ))

        # Amount
        sign = '-' if self.tx_type == 'debit' else '+'
        color = (1, 0.35, 0.35, 1) if self.tx_type == 'debit' else (0.2, 0.8, 0.4, 1)
        amt_label = MDLabel(
            text=f'{sign}{format_amount(self.amount, self.currency)}',
            halign='right',
            theme_text_color='Custom',
            text_color=color,
            size_hint_x=None,
            width='120dp',
        )

        self.add_widget(dot)
        self.add_widget(info)
        self.add_widget(amt_label)

        if on_tap:
            self.bind(on_release=lambda *_: on_tap(tx))

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return r / 255, g / 255, b / 255
