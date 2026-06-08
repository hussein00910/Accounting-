"""
Lightweight pie chart and bar chart using Kivy Canvas.
No third-party charting library needed.
"""

import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import ListProperty


class PieChart(Widget):
    """Draws a pie/donut chart from a list of (value, (r,g,b)) tuples."""

    segments = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(segments=self._redraw, size=self._redraw, pos=self._redraw)

    def set_data(self, data: list[tuple[float, tuple]]):
        self.segments = data
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        if not self.segments:
            return
        total = sum(v for v, _ in self.segments)
        if total == 0:
            return

        cx, cy = self.center
        r = min(self.width, self.height) / 2 - 4
        inner_r = r * 0.5

        start_angle = 90.0
        with self.canvas:
            for value, color in self.segments:
                sweep = (value / total) * 360
                Color(*color, 1)
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2),
                        angle_start=start_angle, angle_end=start_angle + sweep)
                start_angle += sweep

            # Donut hole
            Color(0.13, 0.13, 0.15, 1)
            Ellipse(pos=(cx - inner_r, cy - inner_r),
                    size=(inner_r * 2, inner_r * 2))


class BarChart(Widget):
    """Simple vertical bar chart."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = []
        self.bind(size=self._redraw, pos=self._redraw)

    def set_data(self, data: list[dict]):
        """data: [{'label': '1', 'value': 300.0}]"""
        self._data = data
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        if not self._data:
            return
        values = [d['value'] for d in self._data]
        max_v = max(values) if values else 1
        if max_v == 0:
            max_v = 1

        n = len(self._data)
        pad = 8
        bar_w = max(4, (self.width - pad * (n + 1)) / n)
        chart_h = self.height - 20

        with self.canvas:
            for i, item in enumerate(self._data):
                x = self.x + pad + i * (bar_w + pad)
                h = (item['value'] / max_v) * chart_h
                Color(0.18, 0.75, 0.75, 1)
                Rectangle(pos=(x, self.y + 10), size=(bar_w, max(2, h)))
