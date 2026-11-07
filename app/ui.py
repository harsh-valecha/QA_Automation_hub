import csv
import io
from functools import wraps

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .store import USERS, DuplicateIsbnError, store
from .validation import CATEGORIES, parse_list_params, validate_book

bp = Blueprint("ui", __name__)


def current_user() -> dict | None:
    name = session.get("username")
    if name in USERS:
        return {"username": name, "role": USERS[name]["role"]}
    return None


@bp.app_context_processor
def inject_globals():
    return {"current_user": current_user(), "categories": CATEGORIES}


def login_required(admin: bool = False):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("Please log in to continue.", "info")
                return redirect(url_for("ui.login", next=request.path))
            if admin and user["role"] != "admin":
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator


def _safe_next(target: str | None) -> str:
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("ui.books")


def _form_to_data(form) -> dict:
    """HTML forms send strings; convert what we can and let validation reject the rest."""

    def convert(raw: str, cast):
        try:
            return cast(raw)
        except ValueError:
            return raw

    data = {
        "title": form.get("title", ""),
        "author": form.get("author", ""),
        "isbn": form.get("isbn", "").strip(),
        "category": form.get("category", ""),
        "price": convert(form.get("price", "").strip(), float),
    }
    stock = form.get("stock", "").strip()
    if stock != "":
        data["stock"] = convert(stock, int)
    return data


@bp.get("/")
def index():
    return redirect(url_for("ui.books"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        user = store.authenticate(username, request.form.get("password", ""))
        if user:
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(_safe_next(next_url))
        flash("Invalid username or password", "error")
        return render_template("login.html", username=username), 401
    return render_template("login.html", username="")


@bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("ui.login"))


@bp.get("/books")
def books():
    params, errors = parse_list_params(request.args)
    query = {k: v for k, v in request.args.items() if k != "page" and v}
    if errors:
        flash("Ignored invalid filters: " + ", ".join(errors), "error")
        params, _ = parse_list_params({})
        query = {}
    result = store.list_books(**params)
    return render_template("books.html", result=result, params=params, query=query)


@bp.route("/books/new", methods=["GET", "POST"])
@login_required()
def book_new():
    values, errors = {}, {}
    if request.method == "POST":
        values = _form_to_data(request.form)
        clean, errors = validate_book(values)
        if not errors:
            try:
                book = store.create_book(clean)
            except DuplicateIsbnError:
                errors = {"isbn": "already exists"}
            else:
                flash(f"Book '{book['title']}' created.", "success")
                return redirect(url_for("ui.book_detail", book_id=book["id"]))
        return render_template("book_form.html", mode="create", values=values, errors=errors), 422
    return render_template("book_form.html", mode="create", values=values, errors=errors)


@bp.get("/books/<int:book_id>")
def book_detail(book_id: int):
    book = store.get_book(book_id)
    if book is None:
        abort(404)
    return render_template("book_detail.html", book=book)


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required()
def book_edit(book_id: int):
    book = store.get_book(book_id)
    if book is None:
        abort(404)
    values, errors = dict(book), {}
    if request.method == "POST":
        values = _form_to_data(request.form)
        clean, errors = validate_book(values)
        if not errors:
            try:
                store.update_book(book_id, clean)
            except DuplicateIsbnError:
                errors = {"isbn": "already exists"}
            else:
                flash(f"Book '{clean['title']}' updated.", "success")
                return redirect(url_for("ui.book_detail", book_id=book_id))
        return render_template(
            "book_form.html", mode="edit", book_id=book_id, values=values, errors=errors
        ), 422
    return render_template(
        "book_form.html", mode="edit", book_id=book_id, values=values, errors=errors
    )


@bp.post("/books/<int:book_id>/delete")
@login_required(admin=True)
def book_delete(book_id: int):
    book = store.get_book(book_id)
    if book is None:
        abort(404)
    store.delete_book(book_id)
    flash(f"Book '{book['title']}' deleted.", "success")
    return redirect(url_for("ui.books"))


@bp.get("/books/export.csv")
def books_export():
    """File download (page.expect_download)."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "title", "author", "isbn", "price", "stock", "category"])
    for b in store.list_books(per_page=50)["items"]:
        writer.writerow(
            [b[k] for k in ("id", "title", "author", "isbn", "price", "stock", "category")]
        )
    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=books.csv"},
    )


# ---- playground: one page with the classic Playwright topics --------------
@bp.get("/playground")
def playground():
    return render_template("playground.html", upload_result=None)


@bp.post("/playground/upload")
def playground_upload():
    """File upload (set_input_files). Nothing is stored; we just echo name and size."""
    file = request.files.get("file")
    result = None
    if file and file.filename:
        result = {"name": file.filename, "size": len(file.read())}
    return render_template("playground.html", upload_result=result)


@bp.get("/playground/frame")
def playground_frame():
    """Loaded inside an <iframe> and also opened in a new tab (target=_blank)."""
    return render_template("frame.html")
