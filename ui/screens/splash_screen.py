"""Splash / loading screen shown while SMS sync runs."""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivy.clock import Clock


class SplashScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name='splash', **kwargs)
        layout = MDBoxLayout(
            orientation='vertical',
            padding='40dp',
            spacing='24dp',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            adaptive_size=True,
        )
        layout.add_widget(MDLabel(
            text='مصروفاتي',
            font_style='H3',
            halign='center',
            theme_text_color='Primary',
            bold=True,
        ))
        layout.add_widget(MDLabel(
            text='تتبع مصروفاتك البنكية تلقائياً',
            font_style='Body1',
            halign='center',
            theme_text_color='Secondary',
        ))
        self._spinner = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=('48dp', '48dp'),
            pos_hint={'center_x': 0.5},
        )
        layout.add_widget(self._spinner)
        self.status_label = MDLabel(
            text='جاري قراءة الرسائل…',
            font_style='Caption',
            halign='center',
            theme_text_color='Secondary',
        )
        layout.add_widget(self.status_label)
        self.add_widget(layout)

    def update_status(self, text: str):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))
