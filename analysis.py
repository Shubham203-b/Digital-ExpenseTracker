from datetime import datetime, date
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
import math

from dtclasses import Expenses, Items, session_scope

analysis_kv = """
#:import MDLabel kivymd.label.MDLabel
#:import MDFlatButton kivymd.button.MDFlatButton

<PieChart>:
    canvas.before:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            size: self.size
            pos: self.pos

<Analysis>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(8)

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            canvas.before:
                Color:
                    rgba: app.theme_cls.primary_light
                Rectangle:
                    size: self.size
                    pos: self.pos
            MDLabel:
                text: 'Expense Analysis'
                halign: 'center'
                theme_text_color: 'Primary'
                font_style: 'H6'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(48)
            spacing: dp(6)
            padding: dp(6)
            MDFlatButton:
                text: 'This Month'
                on_release: root.load_data('month')
            MDFlatButton:
                text: 'This Year'
                on_release: root.load_data('year')
            MDFlatButton:
                text: 'All Time'
                on_release: root.load_data('all')

        MDLabel:
            id: lbl_period
            size_hint_y: None
            height: dp(30)
            halign: 'center'
            theme_text_color: 'Secondary'

        PieChart:
            id: pie_chart
            size_hint_y: 0.5

        ScrollView:
            size_hint_y: 0.4
            BoxLayout:
                id: legend_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(4)
"""

COLORS = [
    (0.23, 0.51, 0.89, 1),  # Blue
    (0.96, 0.49, 0.18, 1),  # Orange
    (0.20, 0.73, 0.47, 1),  # Green
    (0.90, 0.22, 0.33, 1),  # Red
    (0.58, 0.33, 0.82, 1),  # Purple
    (0.10, 0.74, 0.81, 1),  # Cyan
    (0.95, 0.76, 0.06, 1),  # Yellow
    (0.93, 0.33, 0.62, 1),  # Pink
    (0.40, 0.69, 0.22, 1),  # Light Green
    (0.60, 0.40, 0.25, 1),  # Brown
]


class PieChart(Widget):
    slices = ListProperty([])

    def on_slices(self, *args):
        self.draw()

    def on_size(self, *args):
        self.draw()

    def on_pos(self, *args):
        self.draw()

    def draw(self):
        self.canvas.clear()
        if not self.slices:
            return

        total = sum(v for _, v, _ in self.slices)
        if total == 0:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        r = min(self.width, self.height) / 2 * 0.85

        angle_start = 0
        with self.canvas:
            for label, value, color in self.slices:
                sweep = 360 * value / total
                Color(*color)
                Ellipse(
                    pos=(cx - r, cy - r),
                    size=(r * 2, r * 2),
                    angle_start=angle_start,
                    angle_end=angle_start + sweep
                )
                # white separator line
                Color(1, 1, 1, 1)
                mid_angle = math.radians(angle_start + sweep / 2)
                Line(
                    points=[cx, cy,
                            cx + r * math.cos(mid_angle),
                            cy + r * math.sin(mid_angle)],
                    width=1.2
                )
                angle_start += sweep


class Analysis(Screen):
    def __init__(self, **kwargs):
        global app_scr
        app_scr = kwargs.pop('app', App.get_running_app())
        kwargs.setdefault('name', 'Analysis')
        super(Analysis, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.load_data('month')

    def load_data(self, period):
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout

        today = date.today()
        data = {}

        try:
            with session_scope() as session:
                from sqlalchemy import func
                from dtclasses import Expenses as Exp, Items as It, Base

                if period == 'month':
                    month = today.strftime('%m')
                    year = today.strftime('%Y')
                    rows = session.query(It.item_name, func.sum(Exp.value))\
                        .filter(It.item_id == Exp.item_id)\
                        .filter(Exp.date.like('{}-{}-%%'.format(year, month)))\
                        .group_by(It.item_name).all()
                    self.ids.lbl_period.text = today.strftime('Month: %B %Y')

                elif period == 'year':
                    year = today.strftime('%Y')
                    rows = session.query(It.item_name, func.sum(Exp.value))\
                        .filter(It.item_id == Exp.item_id)\
                        .filter(Exp.date.like('{}-%'.format(year)))\
                        .group_by(It.item_name).all()
                    self.ids.lbl_period.text = 'Year: {}'.format(year)

                else:  # all time
                    rows = session.query(It.item_name, func.sum(Exp.value))\
                        .filter(It.item_id == Exp.item_id)\
                        .group_by(It.item_name).all()
                    self.ids.lbl_period.text = 'All Time'

                data = {row[0]: row[1] for row in rows if row[1] and row[1] > 0}

        except Exception as e:
            self.ids.lbl_period.text = 'Error loading data'
            return

        if not data:
            self.ids.lbl_period.text = self.ids.lbl_period.text + ' — No data'
            self.ids.pie_chart.slices = []
            self.ids.legend_box.clear_widgets()
            return

        total = sum(data.values())
        slices = []
        for i, (name, value) in enumerate(sorted(data.items(), key=lambda x: -x[1])):
            color = COLORS[i % len(COLORS)]
            slices.append((name, value, color))

        self.ids.pie_chart.slices = slices

        # Build legend
        self.ids.legend_box.clear_widgets()
        currency = app_scr.config.get('CustSettings', 'Currency') if hasattr(app_scr, 'config') else '₹'
        for name, value, color in slices:
            pct = value / total * 100
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=8)
            dot = Widget(size_hint=(None, None), size=(16, 16))
            with dot.canvas:
                Color(*color)
                Ellipse(pos=dot.pos, size=dot.size)
            dot.bind(pos=lambda w, p, c=color: _redraw_dot(w, c))
            from kivy.uix.label import Label
            lbl = Label(
                text='[b]{}[/b]  {}{:.2f}  ({:.1f}%)'.format(name, currency, value, pct),
                markup=True,
                color=(0.2, 0.2, 0.2, 1),
                halign='left',
                valign='middle'
            )
            lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
            row.add_widget(dot)
            row.add_widget(lbl)
            self.ids.legend_box.add_widget(row)


def _redraw_dot(widget, color):
    widget.canvas.clear()
    with widget.canvas:
        Color(*color)
        Ellipse(pos=widget.pos, size=widget.size)