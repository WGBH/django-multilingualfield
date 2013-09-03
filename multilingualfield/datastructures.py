from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.utils.translation import get_language

from lxml import objectify, etree

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

    def as_xml(self):
        """
        Returns this instance as XML.
        """
        xml_to_return = etree.Element("languages")
        for key, value in self.__dict__.iteritems():
            if key != 'languages':
                language = etree.Element("language", code=key)
                language.text = value
                xml_to_return.append(language)

        return etree.tostring(xml_to_return)

class MultiLingualFieldFile(File):
    """
    A `File` subclasses used specifically for the language-keyed
    attributes of a MultiLingualFileField instance.

    Functions almost identically to django's FieldFile
    """
    def __init__(self, storage, name):
        super(MultiLingualFieldFile, self).__init__(None, name)
        self.name = name
        self.storage = storage
        self._committed = True

    def _get_file(self):
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def _get_path(self):
        return self.storage.path(self.name)
    path = property(_get_path)

    def _get_url(self):
        return self.storage.url(self.name)
    url = property(_get_url)

    def _get_size(self):
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name)
    size = property(_get_size)

    def open(self, mode='rb'):
        self.file.open(mode)
    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    def _get_closed(self):
        file = getattr(self, '_file', None)
        return file is None or file.closed
    closed = property(_get_closed)

    def close(self):
        file = getattr(self, '_file', None)
        if file is not None:
            file.close()

class MultiLingualFile(object):
    """
    A class that aggregates multiple files that each correspond
    to a separate language.

    Uses MultiLingualFieldFile instances (or None) for
    language-keyed attributes.
    """

    def __init__(self, xml=None, storage=None):
        """
        `storage` : a django storage class
        `xml` : An optional block of XML formatted like this:
        <languages>
            <language code="en">
                path/to/file.ext
            </language>
            <language code="es">
                path/to/file2.ext
            </language>
        </languages>

        If the above block of XML was passed (as `xml`) to an instance of MultiLingualText
        that instance would have two attributes:
        `en` with a MultiLingualFieldFile instance that pulls `path/to/file.ext`
        from `storage`
        `es` with a MultiLingualFieldFile instance that pulls `path/to/file2.ext`
        from `storage`
        """
        self.languages = LANGUAGES
        # Converting XML (passed-in as `xml`) to a python object via lxml
        if xml and storage:
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
                        name = language_text_as_dict[language_code]
                        f = MultiLingualFieldFile(storage=storage, name=name)
                    else:
                        f = None
                    setattr(self, language_code, f)
        else:
            for language_code, language_verbose in LANGUAGES:
                setattr(self, language_code, None)

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
                val = None
        return val

    def __unicode__(self):
        if self.__repr__():
            return self.__repr__()
        else:
            return u''

    def as_xml(self):
        """
        Returns this instance as XML.
        """
        xml_to_return = etree.Element("languages")
        for key, value in self.__dict__.iteritems():
            if key != 'languages':
                language = etree.Element("language", code=key)
                if value:
                    language.text = value.name
                else:
                    language.text = ""
                xml_to_return.append(language)

        return etree.tostring(xml_to_return)
