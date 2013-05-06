from django.forms.widgets import (
    MultiWidget,
    Textarea
)

from lxml import objectify
from lxml.etree import XMLSyntaxError

from multilingualfield import LANGUAGES

class MultiLingualTextWidget(MultiWidget):
    """
    A widget that returns a `Textarea` widget for each language specified
    in settings.LANGUAGES
    """
    def __init__(self, attrs=None):
        self.languages = LANGUAGES
        widgets = [
            Textarea()
            for language_code, language_verbose in self.languages
        ]
        super(MultiLingualTextWidget, self).__init__(widgets=widgets)

    def decompress(self, value):
        """
        Receives a block of XML and returns a list of values corresponding
        in position to the current ordering of settings.LANGUAGES
        """
        language_text_as_dict = {}
        if value:
            # Converting XML (passed-in as `value`) to a python object via lxml
            try:
                xml_as_python_object = objectify.fromstring(value)
            except XMLSyntaxError:
                raise Exception("Invalid XML was passed to MultiLingualTextWidget.decompress()!")
            else:
                # Creating a dictionary of all the languages passed in the value XML
                # with the language code (i.e. 'en', 'de', 'fr') as the key
                for language in xml_as_python_object.language:
                    language_text_as_dict[unicode(language.language_code)] = unicode(language.language_text)
        # Returning text from XML tree in order dictated by self.languages
        return [
            language_text_as_dict[language_code]
            if language_code in language_text_as_dict else ""
            for language_code, language_verbose in self.languages
        ] 