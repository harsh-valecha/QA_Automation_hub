import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.smoke
def test_books_page_loads(page: Page):
    page.goto("/books")
    expect(page.get_by_test_id("page-title")).to_have_text("Books")