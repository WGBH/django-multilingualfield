from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language

from . import LANGUAGES
from .utils import construct_MultiLingualText_from_xml

class MultiLingualText(object):
    """A class that aggregates manually-written translations for the same piece of text."""

    def __init__(self, xml=None):
        """
        `xml` : An optional block of XML formatted like this:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>

        If the above block of XML was passed (as `xml`) to an instance of MultiLingualText
        that instance would have two attributes:
        `en` with a value of 'Hello'
        `es` with a value of 'Hola'

        If `xml` is not passed to a MultiLingualText instance an attribute for each
        language in settings.LANGUAGES will be built
        """
        self.languages = LANGUAGES
        # Converting XML (passed-in as `xml`) to a python object via lxml
        if xml:
            construct_MultiLingualText_from_xml(xml, self)
        else:
            for language_code, language_verbose in LANGUAGES:
                setattr(self, language_code, "")

    def __repr__(self):
        current_language = get_language()
        try:
            val = getattr(self, current_language)
        except AttributeError:
            if current_language not in [language_code for language_code, language_verbose in LANGUAGES]:
                raise ImproperlyConfigured(
                    "django.utils.translation.get_language returned a language code ('%(current_language)s') not included in the `LANGUAGES` setting for this project. Either add an entry for the '%(current_language)s' language code to `LANGUAGES` or change your `LANGUAGE_CODE` setting to match a language code already listed in `LANGUAGES`." % {'current_language':current_language}
                )
            else:
                val = ""
        return val

    def __unicode__(self):
        return unicode(self.__repr__())
