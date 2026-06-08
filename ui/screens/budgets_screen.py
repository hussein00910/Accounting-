"""
Budget management: set monthly spending limits per category.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivy.clock import Clock

from core.database import Database
from core.categorizer import all_categories
from utils.currency import format_amount


class BudgetsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='budgets', **kwargs)
        self._inputs: dict[str, MDTextField] = {}

        root = MDBoxLayout(orientation='vertical', padding='16dp', spacing='12dp')
        root.add_widget(MDLabel(
            text='تحديد الميزانية الشهرية',
            font_style='H6', bold=True,
            theme_text_color='Primary',
            size_hint_y=None, height='40dp',
        ))
        root.add_widget(MDLabel(
            text='حدد الحد الأقصى للإنفاق لكل فئة شهرياً',
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_y=None, height='24dp',
        ))

        scroll = MDScrollView()
        self._form = MDBoxLayout(
            orientation='vertical',
            spacing='10dp',
            adaptive_height=True,
        )
        scroll.add_widget(self._form)
        root.add_widget(scroll)

        save_btn = MDRaisedButton(
            text='حفظ الميزانيات',
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.18, 0.65, 0.95, 1),
            on_release=self._save,
            size_hint_y=None, height='48dp',
        )
        root.add_widget(save_btn)
        self.add_widget(root)

    def on_enter(self):
        self._build_form()

    def _build_form(self):
        self._form.clear_widgets()
        self._inputs.clear()
        db = Database.get()
        budgets = {b['category']: b['monthly_limit'] for b in db.get_budgets()}

        for cat in all_categories():
            if cat['id'] == 'other':
                continue
            card = MDCard(
                orientation='vertical',
                padding='12dp', spacing='6dp',
                radius=[10], elevation=1,
                md_bg_color=(0.14, 0.14, 0.16, 1),
                size_hint_y=None, height='90dp',
            )
            card.add_widget(MDLabel(
                text=cat['name'],
                font_style='Subtitle2',
                theme_text_color='Primary',
                size_hint_y=None, height='22dp',
            ))
            field = MDTextField(
                hint_text='الحد الأقصى (ريال)',
                input_filter='float',
                text=str(int(budgets.get(cat['id'], 0))) if budgets.get(cat['id']) else '',
                size_hint_y=None, height='48dp',
            )
            self._inputs[cat['id']] = field
            card.add_widget(field)
            self._form.add_widget(card)

    def _save(self, *_):
        db = Database.get()
        for cat_id, field in self._inputs.items():
            try:
                limit = float(field.text.strip() or '0')
                if limit > 0:
                    db.set_budget(cat_id, limit)
            except ValueError:
                pass
        from kivymd.uix.snackbar import MDSnackbar
        MDSnackbar(text='تم حفظ الميزانيات').open()
