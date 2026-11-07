"""Local entry point: python run.py  ->  http://127.0.0.1:5000"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), threaded=True)
