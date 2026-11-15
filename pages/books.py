from playwright.sync_api import Page
from login import BasePage

class BooksPage(BasePage):
    URL = 'books'

    def __init__(self, page):
        super().__init__(page)
        self.total_stats_txt = self.page.get_by_test_id('stats-total')
        self.stock_stats_txt = self.page.get_by_test_id('stats-stock')
        self.filter_input = self.page.get_by_placeholder('Search title or author')
        self.category_dropdown = self.page.get_by_test_id('category-filter')
        self.sort_dropdown = self.page.get_by_test_id('sort-select')
        self.order_dropdown = self.page.locator("[name='order']")
        self.apply_btn = self.page.get_by_role('button',description='Apply')
        self.reset_btn = self.page.locator("//a[text()='Reset']")

    def filter(self):
        pass
