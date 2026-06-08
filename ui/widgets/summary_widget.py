"""Summary card: shows a single stat (label + value)."""

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout


class SummaryCard(MDCard):
    def __init__(self, title: str, value: str, subtitle: str = '',
                 value_color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '16dp'
        self.spacing = '4dp'
        self.radius = [14]
        self.elevation = 2
        self.md_bg_color = (0.14, 0.14, 0.16, 1)
        self.size_hint_y = None
        self.height = '100dp'

        self.add_widget(MDLabel(
            text=title,
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_y=None, height='18dp',
        ))
        val_label = MDLabel(
            text=value,
            font_style='H6',
            bold=True,
            theme_text_color='Custom' if value_color else 'Primary',
            size_hint_y=None, height='34dp',
        )
        if value_color:
            val_label.text_color = value_color
        self.add_widget(val_label)

        if subtitle:
            self.add_widget(MDLabel(
                text=subtitle,
                font_style='Caption',
                theme_text_color='Secondary',
                size_hint_y=None, height='18dp',
            ))
