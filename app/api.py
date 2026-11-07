import time

from flask import Blueprint, g, jsonify, request, url_for

from .auth import require_auth
from .errors import api_error
from .store import DuplicateIsbnError, store
from .validation import parse_list_params, validate_book

bp = Blueprint("api", __name__, url_prefix="/api")


def _json_body():
    """Return (data, error_response). Malformed or non-JSON bodies -> 400."""
    data = request.get_json(silent=True)
    if data is None:
        return None, api_error(
            400, "invalid_json", "Body must be valid JSON with Content-Type: application/json"
        )
    return data, None


# ---- health / stats ------------------------------------------------------
@bp.get("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


@bp.get("/stats")
def stats():
    return jsonify(store.stats())


@bp.get("/slow")
def slow():
    """Responds after ?ms=... (max 5000). Practise waits, timeouts and loading states."""
    try:
        ms = max(0, min(int(request.args.get("ms", "1000")), 5000))
    except ValueError:
        return api_error(400, "bad_request", "ms must be an integer")
    time.sleep(ms / 1000)
    return jsonify({"message": "done", "waited_ms": ms})


# ---- auth ----------------------------------------------------------------
@bp.post("/auth/login")
def login():
    data, error = _json_body()
    if error:
        return error
    details = {}
    for field in ("username", "password"):
        if not isinstance(data, dict) or not isinstance(data.get(field), str) or not data[field]:
            details[field] = "is required"
    if details:
        return api_error(422, "validation_error", "Invalid login payload", details)
    user = store.authenticate(data["username"], data["password"])
    if user is None:
        return api_error(401, "unauthorized", "Invalid username or password")
    token = store.issue_token(user["username"])
    return jsonify({"token": token, "token_type": "Bearer", "role": user["role"]})


@bp.get("/auth/me")
@require_auth()
def me():
    return jsonify(g.user)


# ---- books ---------------------------------------------------------------
@bp.get("/books")
def list_books():
    params, errors = parse_list_params(request.args)
    if errors:
        return api_error(400, "bad_request", "Invalid query parameters", errors)
    return jsonify(store.list_books(**params))


@bp.post("/books")
@require_auth()
def create_book():
    data, error = _json_body()
    if error:
        return error
    clean, errors = validate_book(data)
    if errors:
        return api_error(422, "validation_error", "Invalid book payload", errors)
    try:
        book = store.create_book(clean)
    except DuplicateIsbnError as exc:
        return api_error(409, "conflict", str(exc), {"isbn": "already exists"})
    response = jsonify(book)
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_book", book_id=book["id"])
    return response


@bp.get("/books/<int:book_id>")
def get_book(book_id: int):
    book = store.get_book(book_id)
    if book is None:
        return api_error(404, "not_found", f"Book {book_id} not found")
    return jsonify(book)


def _update(book_id: int, partial: bool):
    data, error = _json_body()
    if error:
        return error
    clean, errors = validate_book(data, partial=partial)
    if errors:
        return api_error(422, "validation_error", "Invalid book payload", errors)
    try:
        book = store.update_book(book_id, clean)
    except DuplicateIsbnError as exc:
        return api_error(409, "conflict", str(exc), {"isbn": "already exists"})
    if book is None:
        return api_error(404, "not_found", f"Book {book_id} not found")
    return jsonify(book)


@bp.put("/books/<int:book_id>")
@require_auth()
def replace_book(book_id: int):
    return _update(book_id, partial=False)


@bp.patch("/books/<int:book_id>")
@require_auth()
def patch_book(book_id: int):
    return _update(book_id, partial=True)


@bp.delete("/books/<int:book_id>")
@require_auth(admin=True)
def delete_book(book_id: int):
    if not store.delete_book(book_id):
        return api_error(404, "not_found", f"Book {book_id} not found")
    return "", 204
