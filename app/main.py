"""
Entry point shim.

The real application object lives in app.api.app.
This module exists so that tools that default to `app.main:app`
(e.g. some deploy scripts, IDE run configs) still work.
"""
from app.api.app import app  # noqa: F401  re-export
