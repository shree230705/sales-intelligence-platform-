"""
Local development entry point.

In Docker/production we use gunicorn pointed at `app:create_app()`
directly (see backend/Dockerfile), so this file is only used for
`python run.py` during local development.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
