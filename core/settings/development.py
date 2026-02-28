"""
Development settings for hirenow-core-api.
"""
import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_DATABASE", "HireNow"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "umasiva1126@"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
