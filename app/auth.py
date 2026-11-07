from functools import wraps

from flask import g, request

from .errors import api_error
from .store import store


def current_api_user() -> dict | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return store.user_for_token(header[len("Bearer ") :].strip())
    return None


def require_auth(admin: bool = False):
    """401 = we don't know who you are. 403 = we know you, but you may not do this."""

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_api_user()
            if user is None:
                response = api_error(401, "unauthorized", "Missing or invalid bearer token")
                response.headers["WWW-Authenticate"] = "Bearer"
                return response
            if admin and user["role"] != "admin":
                return api_error(403, "forbidden", "Admin role required")
            g.user = user
            return view(*args, **kwargs)

        return wrapper

    return decorator
