from django.forms import MultiValueField

from lxml import etree

from multilingualfield import LANGUAGES
from multilingualfield.widgets import MultiLingualTextWidget

class MultiLingualTextForm(MultiValueField):
    """
    The form used for MultiLingualTextFields
    """
    widget = MultiLingualTextWidget

    def compress(self, data_list):
        """
        Compresses a list of text into XML in the following structure:
        <languages>
            <language>
                <language_code>en</language_code>
                <language_text>Hello</language_text>
            </language>
            <language>
                <language_code>es</language_code>
                <language_text>Hola</language_text>
            </language>
        </languages>
        """
        languages = [
            language_code
            for language_code, language_verbose in LANGUAGES
        ]
        xml = etree.Element("languages")
        if data_list:
            for index, entry in enumerate(data_list):
                language = etree.Element("language")
                language_code = etree.SubElement(language, "language_code")
                language_code.text = languages[index]
                language_text = etree.SubElement(language, "language_text")
                language_text.text = entry
                xml.append(language)
        return etree.tostring(xml)