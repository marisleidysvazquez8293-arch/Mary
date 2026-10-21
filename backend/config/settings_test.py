"""
Lightweight settings for unit tests (no PostGIS required).

Usage:
    DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Keep django.contrib.gis installed for app imports, but do not use PostGIS.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
