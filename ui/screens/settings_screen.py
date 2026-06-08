"""
App settings: language, currency, export, about.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.clock import Clock

from core.database import Database
from utils.export import export_to_csv
from utils.date_utils import current_month


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='settings', **kwargs)

        root = MDBoxLayout(orientation='vertical', padding='16dp', spacing='16dp')
        root.add_widget(MDLabel(
            text='الإعدادات',
            font_style='H5', bold=True,
            theme_text_color='Primary',
            size_hint_y=None, height='48dp',
        ))

        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', spacing='14dp', adaptive_height=True)

        # Export section
        content.add_widget(self._section_label('تصدير البيانات'))
        export_btn = MDRaisedButton(
            text='تصدير هذا الشهر كـ CSV',
            md_bg_color=(0.18, 0.65, 0.95, 1),
            on_release=self._export_csv,
        )
        content.add_widget(export_btn)

        # Sync section
        content.add_widget(self._section_label('مزامنة الرسائل'))
        sync_btn = MDRaisedButton(
            text='إعادة قراءة رسائل SMS',
            md_bg_color=(0.2, 0.55, 0.2, 1),
            on_release=self._resync,
        )
        content.add_widget(sync_btn)

        # About
        content.add_widget(self._section_label('حول التطبيق'))
        content.add_widget(MDLabel(
            text='مصروفاتي — تطبيق تتبع المصروفات البنكية عبر SMS\nالإصدار 1.0.0',
            font_style='Body2',
            theme_text_color='Secondary',
            size_hint_y=None, height='56dp',
        ))

        self._status = MDLabel(
            text='',
            font_style='Caption',
            theme_text_color='Secondary',
            size_hint_y=None, height='30dp',
            halign='center',
        )
        content.add_widget(self._status)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    @staticmethod
    def _section_label(text: str) -> MDLabel:
        return MDLabel(
            text=text,
            font_style='Subtitle1',
            bold=True,
            theme_text_color='Primary',
            size_hint_y=None, height='36dp',
        )

    def _export_csv(self, *_):
        db = Database.get()
        month = current_month()
        txs = db.get_transactions(month=month, limit=10000)
        try:
            path = export_to_csv(txs, month)
            self._status.text = f'تم التصدير: {path}'
        except Exception as e:
            self._status.text = f'خطأ: {e}'

    def _resync(self, *_):
        self._status.text = 'جاري المزامنة…'
        from core.sms_reader import sync_sms

        def done(total):
            Clock.schedule_once(
                lambda dt: setattr(self._status, 'text', f'تمت المزامنة: {total} معاملة جديدة')
            )

        sync_sms(on_done=done)
