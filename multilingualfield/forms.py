from django.forms import (
    CharField,
    MultiValueField
)

from lxml import etree

from multilingualfield import LANGUAGES
from multilingualfield.widgets import (
    MultiLingualCharFieldWidget,
    MultiLingualTextFieldWidget
)

class MultiLingualTextFieldForm(MultiValueField):
    """
    The form used by MultiLingualTextField
    """
    widget = MultiLingualTextFieldWidget
    
    def widget_attrs(self, widget):
        """
        Given a Widget instance (*not* a Widget class), returns a dictionary of
        any HTML attributes that should be added to the Widget, based on this
        Field.
        """
        if self.individual_widget_max_length:
            return {'maxlength':self.individual_widget_max_length}
        else:
            return {}

    def __init__(self, *args, **kwargs):
        self.individual_widget_max_length = kwargs.get('individual_widget_max_length', None)
        if 'individual_widget_max_length' in kwargs:
            del kwargs['individual_widget_max_length']
        fields = [
            CharField(
                label=language_verbose,
                max_length=self.individual_widget_max_length
            )
            for language_code, language_verbose in LANGUAGES
        ]
        super(MultiLingualTextFieldForm, self).__init__(tuple(fields), *args, **kwargs)

    def compress(self, data_list):
        """
        Compresses a list of text into XML in the following structure:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
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
                language = etree.Element("language", code=languages[index])
                language.text = entry
                xml.append(language)
        return etree.tostring(xml, xml_declaration=True)

class MultiLingualCharFieldForm(MultiLingualTextFieldForm):
    """
    The form used by MultiLingualCharField
    """
    widget = MultiLingualCharFieldWidget