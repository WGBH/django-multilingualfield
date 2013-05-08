from django.conf import settings
from django.db.models import (
    SubfieldBase,
    Field
)

from lxml import objectify, etree

from multilingualfield import LANGUAGES
from multilingualfield.forms import (
    MultiLingualTextFieldForm,
    MultiLingualCharFieldForm
)

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^multilingualfield\.fields\.MultiLingualTextField",
            "^multilingualfield\.fields\.MultiLingualCharField",
        ]
    )

class MultiLingualText(object):
    """A class that aggregates manually-written translations for the same piece of text."""

    def __init__(self, xml=None):
        """
        `xml` : An optional block of XML formatted like this:
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
            # If xml is passed in, build out attributes accordingly.
            try:
                xml_as_python_object = objectify.fromstring(xml)
            except etree.XMLSyntaxError:
                raise Exception("Invalid XML was passed to MultiLingualText")
            else:
                # Creating a dictionary of all the languages passed in the value XML
                # with the language code (i.e. 'en', 'de', 'fr') as the key
                language_text_as_dict = {}
                for language in xml_as_python_object.language:
                    language_text_as_dict[unicode(language.language_code)] = unicode(language.language_text)
                for language_code, language_verbose in LANGUAGES:
                    if language_code in language_text_as_dict:
                        text = language_text_as_dict[language_code]
                    else:
                        text = ""

                    setattr(self, language_code, text)
        else:
            for language_code, language_verbose in LANGUAGES:
                setattr(self, language_code, "")

    def __repr__(self):
        default_language_code, default_language_verbose = LANGUAGES[0]
        return getattr(self, default_language_code)

class MultiLingualTextField(Field):
    """
    A django TextField for storing multiple manually-written
    translations of the same piece of text.
    """
    description = "Stores multiple manually-written translations of the same piece of text."

    __metaclass__ = SubfieldBase
    
    def __init__(self, *args, **kwargs):
        self.individual_widget_max_length = kwargs.get('max_length', None)
        if self.individual_widget_max_length:
            # Removing max_length so syncdb/south don't make a DB column
            # that's too small for future language additions
            del kwargs['max_length'] 
        super(MultiLingualTextField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'text'

    def to_python(self, value):
        if isinstance(value, MultiLingualText):
            return value
        else:
            return MultiLingualText(value)

    def get_prep_value(self, value):
        """
        Compresses an instance of MultiLingualText into XML in the following format:
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
        if isinstance(value, MultiLingualText):
            xml_to_return = etree.Element("languages")
            for language_code, language_verbose in LANGUAGES:
                language = etree.Element("language")
                language_code_xml_element = etree.SubElement(language, "language_code")
                language_code_xml_element.text = language_code
                language_text_xml_element = etree.SubElement(language, "language_text")
                language_text_xml_element.text = getattr(value, language_code)
                xml_to_return.append(language)

            return etree.tostring(xml_to_return)
        else:
            try:
                xml_as_python_object = objectify.fromstring(value)
            except XMLSyntaxError:
                raise Exception("""Multi Lingual field instances must be created with either an instance of `multilingualfield.fields.MultiLingualText` or a block of XML in the following format:
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
""")
            else:
                return value

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            'form_class': MultiLingualTextFieldForm,
            'individual_widget_max_length':self.individual_widget_max_length
        }
        defaults.update(kwargs)
        return super(MultiLingualTextField, self).formfield(**defaults)

class MultiLingualCharField(MultiLingualTextField):
    """
    A django CharField for storing multiple manually-written
    translations of the same piece of text.
    """
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            'form_class': MultiLingualCharFieldForm,
            'individual_widget_max_length':self.individual_widget_max_length
        }
        defaults.update(kwargs)
        return super(MultiLingualCharField, self).formfield(**defaults)