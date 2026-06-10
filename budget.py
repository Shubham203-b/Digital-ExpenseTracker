"""
Budget Management Screen
- Set daily / monthly / yearly budget
- Stored in SQLite via SQLAlchemy
- Check budget on every expense add
- Alert popup when limit exceeded or near (80%)
"""

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from sqlalchemy import Column, String, Float
from dtclasses import Base, session_scope

# ─── Model ────────────────────────────────────────────────────────────────────

class Budget(Base):
    __tablename__ = 'budget'
    period = Column(String, primary_key=True)   # 'day' | 'month' | 'year'
    amount = Column(Float, default=0.0)

    def __init__(self, **kwargs):
        self.period = kwargs['period']
        self.amount = kwargs['amount']

    def get_budget(period):
        with session_scope() as session:
            b = session.query(Budget).filter(Budget.period == period).first()
            return b.amount if b else 0.0

    def set_budget(period, amount):
        with session_scope() as session:
            b = session.query(Budget).filter(Budget.period == period).first()
            if b:
                b.amount = amount
            else:
                session.add(Budget(period=period, amount=amount))

    def ensure_table():
        from dtclasses import Session
        from sqlalchemy import inspect
        engine = Session.kw['bind']
        if not inspect(engine).has_table('budget'):
            Base.metadata.create_all(engine, tables=[Budget.__table__])


# ─── Alert Helpers ────────────────────────────────────────────────────────────

def check_budget_and_alert(period_label, spent, budget_amount, currency='₹'):
    """Call after adding an expense. Shows popup if over/near budget."""
    if budget_amount <= 0:
        return
    pct = spent / budget_amount * 100
    if pct >= 100:
        _show_alert(
            '🚨 Budget Exceeded!',
            '{} budget exceeded!\nSpent: {}{:.2f}  |  Limit: {}{:.2f}\n({:.1f}% used)'.format(
                period_label, currency, spent, currency, budget_amount, pct),
            (0.9, 0.2, 0.2, 1)
        )
    elif pct >= 80:
        _show_alert(
            '⚠️ Budget Warning',
            '{} budget almost full!\nSpent: {}{:.2f}  |  Limit: {}{:.2f}\n({:.1f}% used)'.format(
                period_label, currency, spent, currency, budget_amount, pct),
            (0.95, 0.6, 0.1, 1)
        )


def _show_alert(title, message, bar_color):
    box = BoxLayout(orientation='vertical', padding=20, spacing=12)
    lbl = Label(text=message, halign='center', valign='middle', color=(0.1, 0.1, 0.1, 1))
    lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))

    popup = Popup(
        title=title,
        title_color=bar_color,
        content=box,
        size_hint=(0.85, 0.45),
        separator_color=bar_color
    )
    from kivymd.button import MDRaisedButton
    btn = MDRaisedButton(text='OK', size_hint=(1, None), height=44)
    btn.bind(on_release=popup.dismiss)
    box.add_widget(lbl)
    box.add_widget(btn)
    popup.open()


# ─── KV ───────────────────────────────────────────────────────────────────────

budget_kv = """
#:import MDTextField kivymd.textfields.MDTextField
#:import MDRaisedButton kivymd.button.MDRaisedButton
#:import MDLabel kivymd.label.MDLabel
#:import MDSeparator kivymd.cards.MDSeparator

<BudgetRow@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(72)
    spacing: dp(10)
    padding: dp(8), dp(4)
    period_label: ''
    budget_input: budget_input
    canvas.before:
        Color:
            rgba: 0.97, 0.97, 0.97, 1
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [8]
    MDLabel:
        text: root.period_label
        size_hint_x: 0.28
        theme_text_color: 'Primary'
        font_style: 'Subtitle1'
        halign: 'left'
    MDTextField:
        id: budget_input
        hint_text: 'Amount'
        input_filter: 'float'
        size_hint_x: 0.45
    MDRaisedButton:
        text: 'Save'
        size_hint_x: 0.27
        on_release: app.screens.objects['Budget'].save_budget(root.period_label.lower(), budget_input.text)

<BudgetScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(12)
        padding: dp(12)

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
                text: 'Set Budget Limits'
                halign: 'center'
                theme_text_color: 'Primary'
                font_style: 'H6'

        MDLabel:
            text: 'Set 0 to disable a budget limit'
            halign: 'center'
            theme_text_color: 'Secondary'
            size_hint_y: None
            height: dp(28)

        BudgetRow:
            id: row_day
            period_label: 'Day'

        BudgetRow:
            id: row_month
            period_label: 'Month'

        BudgetRow:
            id: row_year
            period_label: 'Year'

        MDLabel:
            id: lbl_status
            halign: 'center'
            theme_text_color: 'Primary'
            size_hint_y: None
            height: dp(32)

        BoxLayout:
            orientation: 'vertical'
            padding: dp(8)
            spacing: dp(6)
            size_hint_y: None
            height: dp(130)
            canvas.before:
                Color:
                    rgba: 0.95, 0.95, 0.95, 1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [8]
            MDLabel:
                text: 'Current Budgets'
                halign: 'center'
                font_style: 'Subtitle1'
                theme_text_color: 'Primary'
                size_hint_y: None
                height: dp(28)
            MDLabel:
                id: lbl_day_budget
                halign: 'center'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: dp(24)
            MDLabel:
                id: lbl_month_budget
                halign: 'center'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: dp(24)
            MDLabel:
                id: lbl_year_budget
                halign: 'center'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: dp(24)

        Widget:
"""


# ─── Screen ───────────────────────────────────────────────────────────────────

class BudgetScreen(Screen):
    def __init__(self, **kwargs):
        global app_scr
        app_scr = kwargs.pop('app', App.get_running_app())
        kwargs.setdefault('name', 'Budget')
        super(BudgetScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        Budget.ensure_table()
        currency = self._currency()
        for period in ('day', 'month', 'year'):
            amt = Budget.get_budget(period)
            lbl = self.ids['lbl_{}_budget'.format(period)]
            lbl.text = '{} limit: {}{:.2f}'.format(
                period.capitalize(), currency, amt) if amt > 0 else '{} limit: Not set'.format(period.capitalize())

    def save_budget(self, period, text):
        try:
            amount = float(text) if text.strip() else 0.0
        except ValueError:
            self.ids.lbl_status.text = 'Invalid amount!'
            return
        Budget.ensure_table()
        Budget.set_budget(period, amount)
        self.ids.lbl_status.text = '{} budget saved ✓'.format(period.capitalize())
        self.on_enter()  # refresh display

    def _currency(self):
        try:
            return app_scr.config.get('CustSettings', 'Currency')
        except Exception:
            return '₹'