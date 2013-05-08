import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

LANGUAGES = getattr(settings, 'LANGUAGES', None)

if not LANGUAGES:
    raise ImproperlyConfigured('The `multilingualfield` app requires that `LANGUAGES` (https://docs.djangoproject.com/en/dev/ref/settings/#languages) be set in your settings file.')