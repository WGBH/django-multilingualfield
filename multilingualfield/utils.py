
from django.core.files.storage import default_storage
from lxml import objectify, etree

from . import LANGUAGES, INVALID_XML_ERROR

def construct_MultiLingualText_from_xml(xml, instance):
    """
    Arguments:
    `xml` : A block of XML formatted like this:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>

    `instance`: A MultiLingualText instance

    If the above block of XML was passed to this function (as `xml`)
    `instance` will now have two attributes:
        `en` with a value of 'Hello'
        `es` with a value of 'Hola'
    """
    try:
        xml_as_python_object = objectify.fromstring(xml)
    except etree.XMLSyntaxError:
        raise Exception(INVALID_XML_ERROR + ' MultiLingualText')
    else:
        # Creating a dictionary of all the languages passed in the value XML
        # with the language code (i.e. 'en', 'de', 'fr') as the key
        language_text_as_dict = {}
        try:
            for language in xml_as_python_object.language:
                if language.text:
                    language_text = unicode(language.text)
                else:
                    language_text = ''
                language_text_as_dict[unicode(language.get('code'))] = language_text
        except AttributeError:
            # Empty fields throw-off lxml and cause an AttributeError
            pass
        for language_code, language_verbose in LANGUAGES:
            if language_code in language_text_as_dict:
                text = language_text_as_dict[language_code]
            else:
                text = ""

            setattr(instance, language_code, text)

def construct_MultiLingualFile_from_xml(xml, instance, storage=default_storage):
    """
    Arguments:
    `xml` : A block of XML formatted like this:
        <languages>
            <language code="en">
                path/to/file.ext
            </language>
            <language code="es">
                path/to/file2.ext
            </language>
        </languages>

    `instance`: A MultiLingualFile instance

    If the above block of XML was passed to this function (as `xml`)
    `instance` will now have two attributes:
        `en` with a file stored
        `es` with a value of 'Hola'
    """
    from .datastructures import MultiLingualFieldFile
    try:
        xml_as_python_object = objectify.fromstring(xml)
    except etree.XMLSyntaxError:
        raise Exception(INVALID_XML_ERROR + ' MultiLingualText')
    else:
        # Creating a dictionary of all the languages passed in the value XML
        # with the language code (i.e. 'en', 'de', 'fr') as the key
        language_text_as_dict = {}
        try:
            for language in xml_as_python_object.language:
                if language.text:
                    language_text = unicode(language.text)
                else:
                    language_text = ''
                language_text_as_dict[unicode(language.get('code'))] = language_text
        except AttributeError:
            # Empty fields throw-off lxml and cause an AttributeError
            pass
        for language_code, language_verbose in LANGUAGES:
            if language_code in language_text_as_dict:
                name = language_text_as_dict[language_code]
                f = MultiLingualFieldFile(storage=storage, name=name)
            else:
                f = None
            setattr(instance, language_code, f)
