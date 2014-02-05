from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# Error messages
INVALID_ARGUMENT_ERROR = _(u"'{0}' is not a valid argument for {1}.")
INVALID_XML_ERROR = _(u'Invalid XML was passed to')
LANGUAGES_REQUIRED_ERROR = _(u'The `multilingualfield` app requires that `LANGUAGES` '
    u'(https://docs.djangoproject.com/en/dev/ref/settings/#languages) be set in your settings file.')
UNKNOWN_LANGUAGE_CODE_ERROR = _(u"django.utils.translation.get_language returned a language code "
    u"('{0}') not included in the `LANGUAGES` setting for this project. Either add an entry for the "
    u"'{0}' language code to `LANGUAGES` or change your `LANGUAGE_CODE` setting to match a language "
    u"code already listed in `LANGUAGES`.")
REQUIRED_ERROR = _(u'This multi-lingual field is required therefore you must provide content in {0}.')
XML_SYNTAX_ERROR = _(u"Multi Lingual field instances must be created with either an instance of "
    u"`multilingualfield.fields.MultiLingualText` or a block of XML in the following format:")

LANGUAGES = getattr(settings, u'LANGUAGES', None)
if not LANGUAGES:
    raise ImproperlyConfigured(LANGUAGES_REQUIRED_ERROR)

LANGUAGES_REPLACEMENT = getattr(settings, u'LANGUAGES_REPLACEMENT', {})
LANGUAGES_REQUIRED_TEXT = u'({0})'.format(u', '.join((v for c, v in LANGUAGES if c not in LANGUAGES_REPLACEMENT)))
