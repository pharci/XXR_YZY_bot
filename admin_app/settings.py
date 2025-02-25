from pathlib import Path
import os
from import_export.formats.base_formats import CSV, XLSX
EXPORT_FORMATS = [XLSX, CSV]

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

DEBUG = True
ALLOWED_HOSTS = ['*', 'https://a08hub.ru']

CSRF_TRUSTED_ORIGINS = [
    'https://a08hub.ru',
]

INSTALLED_APPS = [
    "admin_interface",
    'django_jsonform',
    'rangefilter',
    'django_admin_logs',
    "import_export",
    'column_toggle',
    "colorfield",
    "nested_admin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'admin_app.accounts',
    'admin_app.orders',
    'admin_app.bot',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'admin_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders':[
                'admin_tools.template_loaders.Loader',
                ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.getenv("DATABASE_NAME", "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "static"

DJANGO_ADMIN_LOGS_DELETABLE = True

IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'can_export_data'
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000