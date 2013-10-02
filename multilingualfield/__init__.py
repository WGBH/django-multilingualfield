from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# Error messages
INVALID_ARGUMENT_ERROR = _("'%s' is not a valid argument for %s.")
INVALID_XML_ERROR = _('Invalid XML was passed to')
LANGUAGES_REQUIRED_ERROR = _('The `multilingualfield` app requires that `LANGUAGES` '
    '(https://docs.djangoproject.com/en/dev/ref/settings/#languages) be set in your settings file.')
UNKNOWN_LANGUAGE_CODE_ERROR = _("django.utils.translation.get_language returned a language code "
    "('%(current_language)s') not included in the `LANGUAGES` setting for this project. Either add an entry for the "
    "'%(current_language)s' language code to `LANGUAGES` or change your `LANGUAGE_CODE` setting to match a language "
    "code already listed in `LANGUAGES`.")
REQUIRED_ERROR = _('This multi-lingual field is required therefore you must enter text in `%s` field.')
XML_SYNTAX_ERROR = _("Multi Lingual field instances must be created with either an instance of "
    "`multilingualfield.fields.MultiLingualText` or a block of XML in the following format:")

LANGUAGES = getattr(settings, 'LANGUAGES', None)

if not LANGUAGES:
    raise ImproperlyConfigured(LANGUAGES_REQUIRED_ERROR)
