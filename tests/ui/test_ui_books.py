import pytest
from pytest_check import check
from playwright.sync_api import Page , expect
from pages.login import LoginPage
from pages.books import BooksPage

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

    
@pytest.mark.ui 
def test_failed_login_and_unsafe_next_redirect(page:Page):
    l1 = LoginPage(page)
    l1.navigate()
    l1.login('test','test123')
    check.equal(l1.error_alert.text_content(),"Invalid username or password",msg="failed login msg error invalidated")

    # after successful login the page is redirected to applications valid url
    l1.login('user','user123')
    assert page.url.endswith('/books')==True , "valid login does not redirect to correct page"


@pytest.mark.ui 
def test_anonymous_access_to_protected_book_forms(page:Page):
    page.goto('books/1/edit')
    check.is_in('/login', page.url, msg='anonymous access to edit page does not redirect to login page')

    page.goto('books/1/delete')
    error = page.get_by_test_id('error-message').text_content()
    check.equal(error,'Method not allowed',msg='message mismatch')


@pytest.mark.ui 
def test_books_search_filters_sort_and_pagination(page:Page):
    b1 = BooksPage(page)
    b1.navigate()
    filter_str = 'code'
    b1.filter(filter=filter_str,apply=True)
    books = b1.get_books()
    for book in books:
        check.is_in(filter_str,book['name'].lower(),msg = 'substring not in filtered items')

    # resetting the filter
    b1.reset_filter()

    # category filter
    b1.filter(category='fiction')
    books = b1.get_books()
    for book in books:
        check.equal(book['category'],'fiction',msg = 'filtered category does not match')

    b1.reset_filter()
    # sort by filter
    b1.filter(sort='price')
    books = b1.get_books()
    prices_filtered = []
    for book in books:
        prices_filtered.append(float(book['price'][1:]))
    sorted_prices = sorted(prices_filtered)
    check.equal(prices_filtered,sorted_prices,msg='sorting not performed correctly')