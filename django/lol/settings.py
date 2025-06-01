import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback_secret_key")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1").split()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("MYSQL_DATABASE"),
        'USER': os.getenv("MYSQL_USER"),
        'PASSWORD': os.getenv("MYSQL_PASSWORD"),
        'HOST': 'db',
        'PORT': os.getenv("MYSQL_PORT", "3306"),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'django_extensions',
    'django_cleanup.apps.CleanupConfig',
    
    # Your custom apps
    'training_data',
    'gamification', 
    'quests',
    'cards',
    'content_generation',
    'profiles',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lol.urls'
WSGI_APPLICATION = 'lol.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS settings for Phaser.js integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Phaser.js development server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Alternative frontend ports
    "http://127.0.0.1:8080",
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 django nginx").split()
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'django', 'nginx', '*']
#print("DEBUG - DJANGO_ALLOWED_HOSTS env var:", os.getenv("DJANGO_ALLOWED_HOSTS"))
#print("DEBUG - All env vars:", dict(os.environ))
# Allauth settings
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'none'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Media files for generated content
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'

# Additional settings for content generation
CONTENT_GENERATION = {
    'STABLE_DIFFUSION_API_URL': 'your-sd-api-url',
    'LLM_API_URL': 'your-llm-api-url',
    'MAX_GENERATED_FILES': 1000,  # Cleanup threshold
    'GENERATION_BATCH_SIZE': 10,
}

# Caching (optional but recommended for performance)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}