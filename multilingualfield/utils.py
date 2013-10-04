
from django.core.files.storage import default_storage
from lxml import objectify, etree

from . import LANGUAGES, INVALID_XML_ERROR

def construct_MultiLingualText_from_xml(xml, instance):
    u"""
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

    * `instance`: A MultiLingualText instance

    If the above block of XML was passed to this function (as `xml`) `instance` will now have two attributes:

    * `en` with a value of 'Hello'
    * `es` with a value of 'Hola'
    """
    try:
        xml_as_python_object = objectify.fromstring(xml)
    except etree.XMLSyntaxError:
        raise Exception(INVALID_XML_ERROR + ' MultiLingualText')
    else:
        # Creating a dictionary of all the languages passed in the value XML
        # with the language code (i.e. 'en', 'de', 'fr') as the key
        text_dict = {}
        try:
            text_dict = {unicode(l.get(u'code')): unicode(l.text or u'') for l in xml_as_python_object.language}
        except AttributeError:
            # Empty fields throw-off lxml and cause an AttributeError
            pass
        for code, verbose in LANGUAGES:
            setattr(instance, code, text_dict.get(code, u''))


def construct_MultiLingualFile_from_xml(xml, instance, storage=default_storage):
    u"""
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

    * `instance`: A MultiLingualFile instance

    If the above block of XML was passed to this function (as `xml`) `instance` will now have two attributes:
    * `en` with a file stored
    * `es` with a value of 'Hola'
    """
    from .datastructures import MultiLingualFieldFile
    try:
        xml_as_python_object = objectify.fromstring(xml)
    except etree.XMLSyntaxError:
        raise Exception(INVALID_XML_ERROR + ' MultiLingualText')
    else:
        # Creating a dictionary of all the languages passed in the value XML
        # with the language code (i.e. 'en', 'de', 'fr') as the key
        text_dict = {}
        try:
            text_dict = {unicode(l.get('code')): unicode(l.text or u'') for l in xml_as_python_object.language}
        except AttributeError:
            # Empty fields throw-off lxml and cause an AttributeError
            pass
        for code, verbose in LANGUAGES:
            setattr(instance, code, MultiLingualFieldFile(storage=storage, name=text_dict[code])
                                    if code in text_dict else None)
