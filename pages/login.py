import os
from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

class BasePage:
    URL = ""
    def __init__(self, page:Page):
        self.page = page
        self.page_title_txt = page.get_by_test_id('page-title')
        self.books_btn = page.get_by_test_id('nav-books')
        self.playground_btn = page.get_by_test_id('nav-playground')
        self.login_btn = page.get_by_test_id('nav-login')
        self.home_btn = page.get_by_test_id('nav-home')
        self.current_user_txt = page.get_by_test_id('current-user')
        self.logout_btn = page.get_by_test_id('logout-button')
        self.add_book_btn = page.get_by_test_id('nav-add-book')

    def navigate(self):
        self.page.goto(self.URL)

class LoginPage(BasePage):
    URL = "login"

    def __init__(self, page):
        super().__init__(page)
        self.username_input = page.get_by_test_id('username-input')
        self.password_input = page.get_by_test_id('password-input')
        self.login_btn = page.get_by_test_id('login-submit')
        self.error_alert = page.get_by_test_id('flash')

    def login(self,username:str,password:str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()

    def admin_login(self):
        admin_username = self._get_env('ADMIN_USERNAME', 'admin_username')
        admin_password = self._get_env('ADMIN_PASSWORD', 'admin_password')
        self.login(username=admin_username, password=admin_password)

    def user_login(self):
        user_username = self._get_env('USER_USERNAME', 'user_username')
        user_password = self._get_env('USER_PASSWORD', 'user_password')
        self.login(username=user_username, password=user_password)

    @staticmethod
    def _get_env(*names: str) -> str:
        for name in names:
            value = os.getenv(name)
            if value:
                return value
        raise RuntimeError(
            f"Missing login credential environment variable: {names[0]}"
        )


        
