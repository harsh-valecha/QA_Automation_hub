"""Pure validation functions: no Flask, no state. Shared by the API and the UI."""

import math
import re

CATEGORIES = ("fiction", "tech", "science", "history")
SORT_FIELDS = ("id", "title", "price")
BOOK_FIELDS = ("title", "author", "isbn", "price", "stock", "category")
REQUIRED_FIELDS = ("title", "author", "isbn", "price", "category")
ISBN_RE = re.compile(r"^\d{13}$")


def _is_number(value) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _text(max_len: int):
    def check(value):
        if not isinstance(value, str) or not value.strip():
            return None, "must be a non-empty string"
        value = value.strip()
        if len(value) > max_len:
            return None, f"must be at most {max_len} characters"
        return value, None

    return check


def _isbn(value):
    if not isinstance(value, str) or not ISBN_RE.match(value):
        return None, "must be exactly 13 digits"
    return value, None


def _price(value):
    if not _is_number(value) or not math.isfinite(value):
        return None, "must be a number"
    if value <= 0:
        return None, "must be greater than 0"
    return round(float(value), 2), None


def _stock(value):
    if not isinstance(value, int) or isinstance(value, bool):
        return None, "must be an integer"
    if value < 0:
        return None, "must be 0 or more"
    return value, None


def _category(value):
    if value not in CATEGORIES:
        return None, f"must be one of: {', '.join(CATEGORIES)}"
    return value, None


FIELD_VALIDATORS = {
    "title": _text(100),
    "author": _text(60),
    "isbn": _isbn,
    "price": _price,
    "stock": _stock,
    "category": _category,
}


def validate_book(data, partial: bool = False) -> tuple[dict, dict]:
    """Return (clean_data, errors). `partial=True` is PATCH semantics."""
    if not isinstance(data, dict):
        return {}, {"_body": "must be a JSON object"}

    clean: dict = {}
    errors: dict = {}

    for key in data:
        if key not in BOOK_FIELDS:
            errors[key] = "unknown field"

    if partial and not any(key in data for key in BOOK_FIELDS):
        errors["_body"] = "at least one field is required"

    for field in REQUIRED_FIELDS:
        if field not in data and not partial:
            errors[field] = "is required"

    for field, check in FIELD_VALIDATORS.items():
        if field in data:
            value, error = check(data[field])
            if error:
                errors[field] = error
            else:
                clean[field] = value

    if not partial and "stock" not in data:
        clean["stock"] = 0

    return clean, errors


def parse_list_params(args) -> tuple[dict, dict]:
    """Validate the query string of GET /api/books (and the /books page)."""
    errors: dict = {}
    params = {
        "q": (args.get("q") or "").strip() or None,
        "category": None,
        "min_price": None,
        "max_price": None,
        "sort": "id",
        "order": "asc",
        "page": 1,
        "per_page": 5,
    }

    category = args.get("category")
    if category:
        if category in CATEGORIES:
            params["category"] = category
        else:
            errors["category"] = f"must be one of: {', '.join(CATEGORIES)}"

    for name in ("min_price", "max_price"):
        raw = args.get(name)
        if raw not in (None, ""):
            try:
                value = float(raw)
                if value < 0 or not math.isfinite(value):
                    raise ValueError
                params[name] = value
            except ValueError:
                errors[name] = "must be a number >= 0"

    sort = args.get("sort")
    if sort:
        if sort in SORT_FIELDS:
            params["sort"] = sort
        else:
            errors["sort"] = f"must be one of: {', '.join(SORT_FIELDS)}"

    order = args.get("order")
    if order:
        if order in ("asc", "desc"):
            params["order"] = order
        else:
            errors["order"] = "must be asc or desc"

    for name, low, high in (("page", 1, None), ("per_page", 1, 50)):
        raw = args.get(name)
        if raw not in (None, ""):
            try:
                value = int(raw)
                if value < low or (high is not None and value > high):
                    raise ValueError
                params[name] = value
            except ValueError:
                limit = f"between {low} and {high}" if high else f">= {low}"
                errors[name] = f"must be an integer {limit}"

    low_p, high_p = params["min_price"], params["max_price"]
    if low_p is not None and high_p is not None and low_p > high_p:
        errors["min_price"] = "must not be greater than max_price"

    return params, errors
