from kivy.lang import Builder
from kivy.app import App


class Screens:
    primary_widget = None
    current_tab = 'day'
    item_refresh_rqd = True
    item_type = 'main'
    app = ''
    current_screen = 'None'

    objects = {
        'Dashboard':   None,
        'Expenses':    None,
        'Add Expense': None,
        'Items':       None,
        'Insights':    None,
        'Analysis':    None,
        'Budget':      None,
        'AddItem':     None,
    }

    sm_name = {
        'Dashboard':   'Dashboard',
        'Expenses':    'Dashboard2',
        'Add Expense': 'Add Expense',
        'Items':       'Items',
        'Insights':    'Insights',
        'Analysis':    'Analysis',
        'Budget':      'Budget',
        'AddItem':     'AddItem',
    }

    kv_loaded = set()

    def _make_screen(self, name_screen):
        app = self.app

        if name_screen == 'Dashboard':
            from dashboard import Dashboard, dashboard
            if 'Dashboard' not in self.kv_loaded:
                Builder.load_string(dashboard)
                self.kv_loaded.add('Dashboard')
            return Dashboard()

        elif name_screen == 'Expenses':
            from expdetail import Dashboard2, dashboard2
            if 'Expenses' not in self.kv_loaded:
                Builder.load_string(dashboard2)
                self.kv_loaded.add('Expenses')
            return Dashboard2(app=app)

        elif name_screen == 'Add Expense':
            from addexpense import AddExpense, add_expense
            if 'Add Expense' not in self.kv_loaded:
                Builder.load_string(add_expense)
                self.kv_loaded.add('Add Expense')
            return AddExpense()

        elif name_screen == 'Items':
            from itemmaint import ItemsMaint, itemsmaint
            if 'Items' not in self.kv_loaded:
                Builder.load_string(itemsmaint)
                self.kv_loaded.add('Items')
            return ItemsMaint(app=app)

        elif name_screen == 'Insights':
            from insights import Insights, insights_kv
            if 'Insights' not in self.kv_loaded:
                Builder.load_string(insights_kv)
                self.kv_loaded.add('Insights')
            return Insights(app=app)

        elif name_screen == 'Analysis':
            from analysis import Analysis, analysis_kv
            if 'Analysis' not in self.kv_loaded:
                Builder.load_string(analysis_kv)
                self.kv_loaded.add('Analysis')
            return Analysis(app=app)

        elif name_screen == 'AddItem':
            from additem import AddItem, additem
            if 'AddItem' not in self.kv_loaded:
                Builder.load_string(additem)
                self.kv_loaded.add('AddItem')
            return AddItem(app=app)

        elif name_screen == 'Budget':
            from budget import BudgetScreen, budget_kv
            if 'Budget' not in self.kv_loaded:
                Builder.load_string(budget_kv)
                self.kv_loaded.add('Budget')
            return BudgetScreen(app=app)

    def show_screen(self, name_screen):
        self.app = App.get_running_app()

        if self.objects[name_screen] is None:
            screen_obj = self._make_screen(name_screen)
            self.objects[name_screen] = screen_obj
            self.primary_widget.ids.scrn_mgr.add_widget(screen_obj)

        self.primary_widget.ids.scrn_mgr.current = self.sm_name[name_screen]
        self.current_screen = name_screen