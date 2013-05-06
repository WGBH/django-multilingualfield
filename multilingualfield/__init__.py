import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

APP_DIR = os.path.abspath(os.path.dirname(__file__))
LANGUAGES = getattr(settings, 'LANGUAGES', None)
TEST_XML_FILE_LOCATION = open(os.path.join(APP_DIR, 'multilingual-test-values.xml'), 'r')

if not LANGUAGES:
    raise ImproperlyConfigured('The `multilingualfield` app requires that `LANGUAGES` must be set in your settings file.')