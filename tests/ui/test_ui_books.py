import pytest
from playwright.sync_api import Page

@pytest.mark.ui 
def test_login_logout_and_role_navigation(page:Page):
    page.goto('login/')
