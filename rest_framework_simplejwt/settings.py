from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'SIMPLE_JWT', None)

DEFAULTS = {
    'AUTH_HEADER_TYPE': 'Bearer',

    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'TOKEN_LIFETIME': timedelta(days=1),
    'TOKEN_REFRESH_LIFETIME': timedelta(days=7),

    'SECRET_KEY': settings.SECRET_KEY,

    # Undocumented settings.  Changing these may lead to unexpected behavior.
    # Make sure you know what you're doing.  These might become part of the
    # public API eventually but that would require some adjustments.
    'TOKEN_CLASS': 'rest_framework_simplejwt.tokens.Token',
    'TOKEN_BACKEND_CLASS': 'rest_framework_simplejwt.backends.PythonJOSEBackend',
    'ALGORITHM': 'HS256',
}

IMPORT_STRING_SETTINGS = (
    'TOKEN_CLASS',
    'TOKEN_BACKEND_CLASS',
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRING_SETTINGS)
