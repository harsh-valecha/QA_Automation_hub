import pytest
from pytest_check import check
from playwright.sync_api import Page , expect

@pytest.mark.ui 
def test_login_logout_and_role_navigation(page:Page):
    # when navigate to books/ initially no actions should display
    page.goto('/')
    rows = page.locator(".actions").all_inner_texts()
    for i in rows:
        check.equal(i,"",msg="invalid action displayed")

    # user login then validate the books/ actions
    page.goto("login")
    page.get_by_label("Username ").fill("user")
    page.get_by_test_id("password-input").fill("user123")
    page.get_by_role('button').click()
    rows = page.locator(".actions").all_inner_texts()
    for i in rows:
        check.equal(i,"Edit",msg="action mismatch for user")

    # admin login then validate books/ actions
    page.goto('login')
    page.locator("input[name='username']").fill("admin")
    page.get_by_label("Password ").fill("admin123")
    page.get_by_test_id("login-submit").click()
    rows = page.locator(".actions").all_inner_texts()
    for i in rows:
        check.equal(i,"Edit\nDelete",msg="action mismatch for admin")
    
    
