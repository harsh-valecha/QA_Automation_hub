from typing import Literal
from playwright.sync_api import Page
from pages.login import BasePage

class BooksPage(BasePage):
    URL = 'books'

    def __init__(self, page:Page):
        super().__init__(page)
        self.total_stats_txt = page.get_by_test_id('stats-total')
        self.stock_stats_txt = page.get_by_test_id('stats-stock')
        self.filter_input = page.get_by_placeholder('Search title or author')
        self.category_dropdown = page.get_by_test_id('category-filter')
        self.sort_dropdown = page.get_by_test_id('sort-select')
        self.order_dropdown = page.locator("[name='order']")
        self.apply_btn = page.get_by_test_id('apply-filters')
        self.reset_btn = page.get_by_test_id('reset-filters')
        self.book_titles_txt = page.get_by_test_id('book-title')
        self.author_txt = page.get_by_test_id('book-author')
        self.book_isbn_txt = page.get_by_test_id('book-isbn')
        self.book_price_txt = page.get_by_test_id('book-price')
        self.book_stock_txt = page.get_by_test_id('book-stock')
        self.book_category_txt = page.get_by_test_id('book-category')
        self.book_edit_btn = page.get_by_test_id('edit-book')
        self.book_delete_btn = page.get_by_test_id('delete-book')
        

    def filter(
        self,
        filter:str = None,
        category:Literal['All categories','fiction','tech','science','history'] = 'All categories',
        sort:Literal['sort: id','sort: title','sort: price'] = 'sort: id',
        order:Literal['asc','desc'] = 'asc',
        apply:bool = True
    ):
        self.filter_input.fill(filter or '')
        self.category_dropdown.select_option(value=category)
        self.sort_dropdown.select_option(value=sort)
        self.order_dropdown.select_option(value=order)
        if apply:
            self.apply_btn.click()
        

    def edit_book(self,url:str):
        edit = EditPage(self.page,url=url)

    def delete_book(self):
        pass

    def reset_filter(self):
        self.reset_btn.click()

    def get_books(self):
        books = []
        for row in self.page.get_by_test_id('book-row').all():
            books.append({
                'name':row.get_by_test_id('book-title').text_content(),
                'author':row.get_by_test_id('book-author').text_content(),
                'isbn':row.get_by_test_id('book-isbn').text_content(),
                'price':row.get_by_test_id('book-price').text_content(),
                'stock':row.get_by_test_id('book-stock').text_content(),
                'category':row.get_by_test_id('book-category').text_content()
            })
        return books


class EditPage(BasePage):
    URL = ''

    def __init__(self, page:Page , url:str):
        super().__init__(page)
        self.URL = url
        self.title_input = page.get_by_test_id('input-title')
        self.author_input = page.get_by_test_id('input-author')
        self.isbn_input = page.get_by_test_id('input-isbn')
        self.price_input = page.get_by_test_id('input-price')
        self.stock_input = page.get_by_test_id('input-stock')
        self.category_dropdown = page.get_by_test_id('input-isbn')
        self.save_btn = page.get_by_test_id('submit-book')
        self.cancel_btn = page.get_by_test_id('cancel-link')

    def edit(self, 
             title:str ,
             author:str , 
             isbn:int ,
             price:float , 
             stock: int , 
             category: Literal['fiction','tech','science','history'],
             save:bool = True,
             cancel:bool = False):
        self.title_input.fill(title)
        self.author_input.fill(author)
        self.isbn_input.fill(isbn)
        self.price.fill(price)
        self.stock.fill(stock)
        self.category_dropdown.select_option(category)
        if save:
            self.save_btn.click()
        if cancel:
            self.cancel_btn.click()
        
