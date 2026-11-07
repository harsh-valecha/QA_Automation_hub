import os

from flask import Flask, jsonify, render_template, request

from .errors import api_error
from .store import store


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-secret"),
        ENABLE_TEST_ROUTES=os.getenv("ENABLE_TEST_ROUTES", "0") == "1",
    )
    if test_config:
        app.config.update(test_config)

    from .api import bp as api_bp
    from .ui import bp as ui_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(ui_bp)

    if app.config["ENABLE_TEST_ROUTES"]:
        # Test-only helper so every test can start from a known state.
        # NEVER enable this on a real environment.
        @app.post("/api/test/reset")
        def reset_state():
            store.reset()
            return "", 204

    def _wants_json() -> bool:
        return request.path.startswith("/api/")

    @app.errorhandler(404)
    def not_found(_):
        if _wants_json():
            return api_error(404, "not_found", "Resource not found")
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(403)
    def forbidden(_):
        if _wants_json():
            return api_error(403, "forbidden", "Forbidden")
        return render_template("error.html", code=403, message="Admin role required"), 403

    @app.errorhandler(405)
    def method_not_allowed(_):
        if _wants_json():
            return api_error(405, "method_not_allowed", "Method not allowed")
        return render_template("error.html", code=405, message="Method not allowed"), 405

    @app.errorhandler(500)
    def server_error(_):
        if _wants_json():
            return jsonify({"error": "server_error", "message": "Unexpected error"}), 500
        return render_template("error.html", code=500, message="Unexpected error"), 500

    return app
