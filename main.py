"""
المحاسب الذكي — Smart Accountant
Entry point: initialises KivyMD theme, builds ScreenManager, runs SMS sync.
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock

from ui.screens.splash_screen import SplashScreen
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.transactions_screen import TransactionsScreen
from ui.screens.analytics_screen import AnalyticsScreen
from ui.screens.budgets_screen import BudgetsScreen
from ui.screens.settings_screen import SettingsScreen
from core.sms_reader import sync_sms
from core.database import Database

try:
    from android.permissions import request_permissions, Permission  # type: ignore
    _ANDROID = True
except ImportError:
    _ANDROID = False


_NAV_ITEMS = [
    ('view-dashboard', 'الرئيسية', 'dashboard'),
    ('format-list-bulleted', 'المعاملات', 'transactions'),
    ('chart-bar', 'الإحصاءات', 'analytics'),
    ('wallet', 'الميزانية', 'budgets'),
    ('cog', 'الإعدادات', 'settings'),
]


class SmartAccountantApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'DeepOrange'
        self.title = 'المحاسب الذكي'

        root = MDBoxLayout(orientation='vertical')

        self.sm = MDScreenManager()

        # Add all screens
        self.sm.add_widget(SplashScreen())
        self.sm.add_widget(DashboardScreen())
        self.sm.add_widget(TransactionsScreen())
        self.sm.add_widget(AnalyticsScreen())
        self.sm.add_widget(BudgetsScreen())
        self.sm.add_widget(SettingsScreen())

        root.add_widget(self.sm)

        # Bottom navigation bar
        nav = MDNavigationBar(on_switch_tabs=self._on_tab)
        for icon, label, screen in _NAV_ITEMS:
            item = MDNavigationItem(
                MDNavigationItem.icon(icon) if hasattr(MDNavigationItem, 'icon') else None,
                text=label,
            )
            item._screen = screen
            nav.add_widget(item)
        root.add_widget(nav)

        return root

    def on_start(self):
        if _ANDROID:
            request_permissions([
                Permission.READ_SMS,
                Permission.RECEIVE_SMS,
            ], self._on_permissions)
        else:
            Clock.schedule_once(self._start_sync, 0.5)

    def _on_permissions(self, permissions, results):
        Clock.schedule_once(self._start_sync, 0.5)

    def _start_sync(self, *_):
        splash = self.sm.get_screen('splash')
        self.sm.current = 'splash'

        def progress(count):
            splash.update_status(f'تم استخراج {count} معاملة…')

        def done(total):
            splash.update_status(f'تم! {total} معاملة جديدة')
            Clock.schedule_once(lambda dt: self._go_dashboard(), 1.0)

        sync_sms(on_progress=progress, on_done=done)

    def _go_dashboard(self):
        self.sm.current = 'dashboard'

    def _on_tab(self, bar, item, item_name):
        screen = getattr(item, '_screen', None)
        if screen and screen in [s.name for s in self.sm.screens]:
            self.sm.current = screen

    def on_stop(self):
        Database.get().close()


if __name__ == '__main__':
    SmartAccountantApp().run()
