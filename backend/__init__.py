"""Backend package.

Exists so the root launcher can import `backend.app` unambiguously — the
root `app.py` and the `backend/app` package would otherwise clash on the
name `app`. Deployment (Render / Docker) runs from inside `backend/`, where
`wsgi.py` imports `app` directly and this file is simply unused.
"""
