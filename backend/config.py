"""Single env/config loader.

All `os.getenv` reads in the project live here. Every other module imports its
settings from this module instead of touching the environment.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _scrub_dead_proxies() -> None:
    """Remove injected dead-proxy env vars (Sarvam SDK honors them via httpx)."""
    for proxy_var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        if os.getenv(proxy_var, "").startswith("http://127.0.0.1:9"):
            os.environ.pop(proxy_var, None)


_scrub_dead_proxies()

# ── Redis ──────────────────────────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── MySQL ──────────────────────────────────────────────────────────────────────
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", os.getenv("MYSQL_DATABASE_V2", "property_ocr_v2"))

# ── API keys ───────────────────────────────────────────────────────────────────
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

# ── Uploads ────────────────────────────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

# ── Auth / JWT ─────────────────────────────────────────────────────────────────
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cleartitle-secret-key-production-change-me-12345")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))

# ── Google OAuth ───────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
GOOGLE_FRONTEND_REDIRECT_URI = os.getenv("GOOGLE_FRONTEND_REDIRECT_URI", "http://localhost:8000/login")

# ── API / app ──────────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000",
).split(",")
PIPELINE_LOCK_ENABLED = os.getenv("PIPELINE_LOCK_ENABLED", "true").lower() == "true"
