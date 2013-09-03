from lxml import objectify, etree

from . import LANGUAGES

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
        raise Exception("Invalid XML was passed to MultiLingualText")
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
