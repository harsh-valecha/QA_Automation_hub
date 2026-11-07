"""In-memory data store. Deliberately simple so you can focus on testing, not on a DB."""

import copy
import itertools
import math
import secrets
import threading
from datetime import UTC, datetime

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}

SEED_BOOKS = [
    ("Clean Code", "Robert C. Martin", "9780132350884", 39.99, 12, "tech"),
    ("Fluent Python", "Luciano Ramalho", "9781492056355", 59.5, 7, "tech"),
    ("Cosmos", "Carl Sagan", "9780345539434", 18.0, 20, "science"),
    ("Sapiens", "Yuval Noah Harari", "9780062316110", 22.5, 15, "history"),
    ("The Hobbit", "J.R.R. Tolkien", "9780547928227", 14.99, 30, "fiction"),
    ("Dune", "Frank Herbert", "9780441172719", 9.99, 0, "fiction"),
    ("Pragmatic Programmer", "Andrew Hunt", "9780135957059", 49.0, 5, "tech"),
]


class DuplicateIsbnError(Exception):
    def __init__(self, isbn: str):
        super().__init__(f"ISBN {isbn} already exists")
        self.isbn = isbn


class Store:
    def __init__(self):
        self._lock = threading.RLock()
        self.tokens: dict[str, str] = {}
        self.books: dict[int, dict] = {}
        self._ids = itertools.count(1)
        self.reset()

    # ---- lifecycle -------------------------------------------------------
    def reset(self):
        """Back to the seed data. Tokens survive so logged-in sessions keep working."""
        with self._lock:
            self.books = {}
            self._ids = itertools.count(1)
            for title, author, isbn, price, stock, category in SEED_BOOKS:
                self.create_book(
                    {
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "price": price,
                        "stock": stock,
                        "category": category,
                    }
                )

    # ---- auth ------------------------------------------------------------
    def authenticate(self, username: str, password: str) -> dict | None:
        user = USERS.get(username)
        if user and secrets.compare_digest(user["password"], password):
            return {"username": username, "role": user["role"]}
        return None

    def issue_token(self, username: str) -> str:
        token = secrets.token_hex(16)
        with self._lock:
            self.tokens[token] = username
        return token

    def user_for_token(self, token: str) -> dict | None:
        username = self.tokens.get(token)
        if username in USERS:
            return {"username": username, "role": USERS[username]["role"]}
        return None

    # ---- books -----------------------------------------------------------
    def _isbn_taken(self, isbn: str, ignore_id: int | None = None) -> bool:
        return any(b["isbn"] == isbn and b["id"] != ignore_id for b in self.books.values())

    def create_book(self, clean: dict) -> dict:
        with self._lock:
            if self._isbn_taken(clean["isbn"]):
                raise DuplicateIsbnError(clean["isbn"])
            book_id = next(self._ids)
            book = {
                "id": book_id,
                **clean,
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            self.books[book_id] = book
            return copy.deepcopy(book)

    def get_book(self, book_id: int) -> dict | None:
        with self._lock:
            book = self.books.get(book_id)
            return copy.deepcopy(book) if book else None

    def update_book(self, book_id: int, clean: dict) -> dict | None:
        with self._lock:
            book = self.books.get(book_id)
            if book is None:
                return None
            if "isbn" in clean and self._isbn_taken(clean["isbn"], ignore_id=book_id):
                raise DuplicateIsbnError(clean["isbn"])
            book.update(clean)
            return copy.deepcopy(book)

    def delete_book(self, book_id: int) -> bool:
        with self._lock:
            return self.books.pop(book_id, None) is not None

    def list_books(
        self,
        q=None,
        category=None,
        min_price=None,
        max_price=None,
        sort="id",
        order="asc",
        page=1,
        per_page=5,
    ) -> dict:
        with self._lock:
            items = copy.deepcopy(list(self.books.values()))

        if q:
            needle = q.lower()
            items = [
                b for b in items if needle in b["title"].lower() or needle in b["author"].lower()
            ]
        if category:
            items = [b for b in items if b["category"] == category]
        if min_price is not None:
            items = [b for b in items if b["price"] >= min_price]
        if max_price is not None:
            items = [b for b in items if b["price"] <= max_price]

        key = (lambda b: b["title"].lower()) if sort == "title" else (lambda b: b[sort])
        items.sort(key=key, reverse=(order == "desc"))

        total = len(items)
        start = (page - 1) * per_page
        return {
            "items": items[start : start + per_page],
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": max(1, math.ceil(total / per_page)),
        }

    def stats(self) -> dict:
        with self._lock:
            books = list(self.books.values())
        by_category: dict[str, int] = {}
        for book in books:
            by_category[book["category"]] = by_category.get(book["category"], 0) + 1
        return {
            "total_books": len(books),
            "total_stock": sum(b["stock"] for b in books),
            "by_category": by_category,
        }


store = Store()
