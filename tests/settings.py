DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

INSTALLED_APPS = [
    "tests",
]

DEBUG = False

SITE_ID = 1

SECRET_KEY = "test-secret-key-not-for-production"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True
