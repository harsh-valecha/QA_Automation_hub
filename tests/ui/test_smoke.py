import csv
from pathlib import Path
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.smoke
def test_books_page_loads(page: Page):
    page.goto("/books")
    assert page.title()=='Books · QA Practice Hub','Title mismatch'

@pytest.mark.ui 
@pytest.mark.smoke
def test_core_pages_render_smoke(page:Page):
    # check login page render without error
    page.goto("/login")
    expect(page).to_have_title('Log in · QA Practice Hub')
    
    # check play
    page.goto("/playground")
    expect(page).to_have_title('Playground · QA Practice Hub')


@pytest.mark.ui 
def test_root_redirect_and_unknown_route_renders_404(page:Page , base_url):
    page.goto("/")
    expect(page).to_have_url(f"{base_url}/books")

    response = page.goto("/this-route-does-not-exist")
    assert response is not None
    assert response.status == 404
    expect(page.locator("body")).to_contain_text("404")

@pytest.mark.ui 
def test_books_csv_download_smoke(page:Page):
    page.goto("/playground")
    with page.expect_download() as download_info:
        page.get_by_test_id("download-csv").click()

    download = download_info.value
    csv_path = Path(__file__).resolve().parents[2] / download.suggested_filename
    download.save_as(csv_path)

    with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, [])
        rows = list(reader)

    assert headers, "CSV should contain headers"
    assert rows, "CSV should contain data rows"
    assert all(len(row) == len(headers) for row in rows), "Each CSV row should match the header columns"
