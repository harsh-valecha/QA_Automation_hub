from flask import jsonify


def api_error(status: int, code: str, message: str, details: dict | None = None):
    """Every API error has the same shape: {"error", "message", optional "details"}."""
    body = {"error": code, "message": message}
    if details:
        body["details"] = details
    response = jsonify(body)
    response.status_code = status
    return response
