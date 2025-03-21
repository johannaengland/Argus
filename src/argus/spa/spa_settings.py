from urllib.parse import urlsplit

from argus.site.settings.base import *
from argus.site.settings import get_str_env, normalize_url


FRONTEND = "spa"

INSTALLED_APPS = ["channels"] + INSTALLED_APPS + ["argus.spa"]

LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ARGUS_SPA_TOKEN_COOKIE_NAME = "token"
SPA_COOKIE_DOMAIN = get_str_env("ARGUS_SPA_COOKIE_DOMAIN", required=True)

# PSA for login

_SOCIAL_AUTH_DATAPORTEN_KEY = get_str_env("ARGUS_DATAPORTEN_KEY")
_SOCIAL_AUTH_DATAPORTEN_SECRET = get_str_env("ARGUS_DATAPORTEN_SECRET")

SOCIAL_AUTH_DATAPORTEN_EMAIL_KEY = _SOCIAL_AUTH_DATAPORTEN_KEY
SOCIAL_AUTH_DATAPORTEN_EMAIL_SECRET = _SOCIAL_AUTH_DATAPORTEN_SECRET

SOCIAL_AUTH_DATAPORTEN_FEIDE_KEY = _SOCIAL_AUTH_DATAPORTEN_KEY
SOCIAL_AUTH_DATAPORTEN_FEIDE_SECRET = _SOCIAL_AUTH_DATAPORTEN_SECRET

AUTHENTICATION_BACKENDS = [
    "argus.spa.dataporten.social.DataportenFeideOAuth2",
    "django.contrib.auth.backends.RemoteUserBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "argus.spa.root_urls"

# django-cors-headers
CORS_ALLOWED_ORIGINS = []
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(normalize_url(FRONTEND_URL))

# django-channels

ASGI_APPLICATION = "argus.spa.ws.asgi.application"

# fmt: off
_REDIS = urlsplit("//" + get_str_env("ARGUS_REDIS_SERVER", "127.0.0.1:6379"))
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(_REDIS.hostname, _REDIS.port or 6379)],
        },
    },
}
# fmt: on
