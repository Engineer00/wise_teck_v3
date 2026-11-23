"""Wise-Teck v3 (Django) settings.

Development needs nothing: SQLite + DEBUG. On the server set environment variables (e.g. in the
systemd unit or a .env file loaded by it):

    DJANGO_SECRET_KEY=...            (required when DJANGO_DEBUG=0)
    DJANGO_DEBUG=0
    DJANGO_ALLOWED_HOSTS=wiseteck.dev,www.wiseteck.dev
    DJANGO_CSRF_TRUSTED_ORIGINS=https://wiseteck.dev,https://www.wiseteck.dev
    POSTGRES_DB=wiseteck  POSTGRES_USER=wiseteck  POSTGRES_PASSWORD=...  [POSTGRES_HOST=localhost  POSTGRES_PORT=5432]
    EMAIL_HOST=...  EMAIL_PORT=587  EMAIL_HOST_USER=...  EMAIL_HOST_PASSWORD=...  DEFAULT_FROM_EMAIL=...
"""

import os
from pathlib import Path

from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name, default=""):
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("dev-only-not-secret" if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError("Set DJANGO_SECRET_KEY when DJANGO_DEBUG=0")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "core.middleware.AnalyticsCSPMiddleware",
    "core.middleware.PermissionsPolicyMiddleware",
    "core.middleware.RedirectFallbackMiddleware",
    "core.stats.VisitStatsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if os.environ.get("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ.get("POSTGRES_USER", ""),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # long section forms with many cards
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "adminpanel_login"

# Security headers (every response). The CSP lists the only places the site loads things from: itself
# (fonts and icons are served from the site too); photos may also be https links typed in the admin.
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
    "font-src": [CSP.SELF, "data:"],
    "img-src": [CSP.SELF, "data:", "https:"],
    "connect-src": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
    "form-action": [CSP.SELF],
    "base-uri": [CSP.SELF],
    "object-src": [CSP.NONE],
}
# Pages that load Google Analytics (Site Settings → Google Analytics ID) also allow Google's tag and beacons.
GOOGLE_ANALYTICS = [
    "https://*.googletagmanager.com",
    "https://*.google-analytics.com",
    "https://*.analytics.google.com",
]
SECURE_CSP_ANALYTICS = {
    **SECURE_CSP,
    "script-src": [CSP.SELF, "https://*.googletagmanager.com"],
    "connect-src": [CSP.SELF, *GOOGLE_ANALYTICS],
}
# Rate limits (core/throttle.py): attempts per address, per minutes.
THROTTLE = {"login": (5, 15), "contact": (5, 10)}
SESSION_COOKIE_AGE = 8 * 60 * 60  # admins are signed out after 8 hours
PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"  # the site is never shown inside a frame

if not DEBUG:  # behind Nginx with HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # browsers always use https for a year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # .dev domains are https-only in every browser anyway
    SECURE_HSTS_PRELOAD = True
    # Nginx redirects http -> https before Django sees the request (see DEPLOY.md), so Django doesn't redirect too.
    SILENCED_SYSTEM_CHECKS = ["security.W008"]

# Email (contact form alerts). Without EMAIL_HOST the emails are printed in the terminal.
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Wise-Teck Website <no-reply@wise-teck.org>")

# Daily Google Lighthouse check (core/lighthouse.py): the GitHub workflow posts its results with this shared
# secret (repository secret LIGHTHOUSE_TOKEN = the same value). Empty = results are not accepted.
LIGHTHOUSE_TOKEN = os.environ.get("LIGHTHOUSE_TOKEN", "")
LIGHTHOUSE_WORKFLOW_URL = os.environ.get(
    "LIGHTHOUSE_WORKFLOW_URL", "https://github.com/Engineer00/wise_teck_v3/actions/workflows/lighthouse.yml"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
