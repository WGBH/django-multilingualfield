from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.utils.encoding import smart_str
from django.utils.translation import get_language

from lxml import objectify, etree

from . import utils, LANGUAGES, INVALID_XML_ERROR, UNKNOWN_LANGUAGE_CODE_ERROR

class MultiLingualText(object):
    u"""A class that aggregates manually-written translations for the same piece of text."""

    def __init__(self, xml=None):
        u"""
        `xml` : An optional block of XML formatted like this:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>

        If the above block of XML was passed (as `xml`) to an instance of MultiLingualText that instance would have two
        attributes:

        * `en` with a value of 'Hello'
        * `es` with a value of 'Hola'

        If `xml` is not passed to a MultiLingualText instance an attribute for each language in settings.LANGUAGES will
        be built.
        """
        self.languages = LANGUAGES
        # Converting XML (passed-in as `xml`) to a python object via lxml
        if xml:
            utils.construct_MultiLingualText_from_xml(xml, self)
        else:
            for code, verbose in LANGUAGES:
                setattr(self, code, u'')

    def get_for_current_language(self):
        """
        Returns the attribute on this object associated with the current language
        of the active thread (as provided by django.utils.translation.get_language)
        """
        current = get_language()

        try:
            val = getattr(self, current)
        except AttributeError:
            if current not in [code for code, verbose in LANGUAGES]:
                raise ImproperlyConfigured(UNKNOWN_LANGUAGE_CODE_ERROR.format(current))
            else:
                val = ''
        return val


    def __repr__(self):
        val = self.get_for_current_language()
        return smart_str(val, errors='ignore')

    def __unicode__(self):
        val = self.get_for_current_language()
        return smart_str(val, errors='strict')

    def as_xml(self):
        u"""Returns this instance as XML."""
        xml_to_return = etree.Element(u'languages')
        for key, value in self.__dict__.iteritems():
            if key != u'languages':
                language = etree.Element(u'language', code=key)
                language.text = value
                xml_to_return.append(language)
        return etree.tostring(xml_to_return)

class MultiLingualFieldFile(File):
    u"""
    A `File` subclasses used specifically for the language-keyed attributes of a MultiLingualFileField instance.

    Functions almost identically to django's FieldFile
    """
    def __init__(self, storage, name):
        super(MultiLingualFieldFile, self).__init__(None, name)
        self.name = name
        self.storage = storage
        self._committed = True

    @property
    def file(self):
        if not getattr(self, u'_file', None):
            self._file = self.storage.open(self.name, u'rb')
        return self._file

    @file.setter
    def file(self, value):
        self._file = value

    @file.deleter
    def file(self):
        del self._file

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def url(self):
        return self.storage.url(self.name)

    @property
    def size(self):
        return self.storage.size(self.name) if self._committed else self.file.size

    def open(self, mode=u'rb'):
        self.file.open(mode)
    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    @property
    def closed(self):
        file = getattr(self, u'_file', None)
        return file is None or file.closed

    def close(self):
        file = getattr(self, u'_file', None)
        if file is not None:
            file.close()

class MultiLingualFile(object):
    u"""
    A class that aggregates multiple files that each correspond to a separate language.

    Uses MultiLingualFieldFile instances (or None) for language-keyed attributes.
    """

    def __init__(self, xml=None, storage=None):
        u"""
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

        If the above block of XML was passed (as `xml`) to an instance of MultiLingualText that instance would have two
        attributes:

        * `en` with a MultiLingualFieldFile instance that pulls `path/to/file.ext` from `storage`
        * `es` with a MultiLingualFieldFile instance that pulls `path/to/file2.ext` from `storage`
        """
        self.languages = LANGUAGES
        # Converting XML (passed-in as `xml`) to a python object via lxml
        if xml and storage:
            try:
                xml_as_python_object = objectify.fromstring(xml)
            except etree.XMLSyntaxError:
                raise Exception(INVALID_XML_ERROR + ' MultiLingualText')
            else:
                # Creating a dictionary of all the languages passed in the value XML
                # with the language code (i.e. 'en', 'de', 'fr') as the key
                text_dict = {}
                try:
                    text_dict = {
                        unicode(l.get(u'code')): unicode(l.text or u'')
                        for l in xml_as_python_object.language
                    }
                except AttributeError:
                    # Empty fields throw-off lxml and cause an AttributeError
                    pass
                for code, verbose in LANGUAGES:
                    setattr(self, code, MultiLingualFieldFile(storage=storage, name=text_dict[code])
                                        if code in text_dict else None)
        else:
            for code, verbose in LANGUAGES:
                setattr(self, code, None)

    def __repr__(self):
        current = get_language()
        try:
            val = getattr(self, current)
        except AttributeError:
            if current not in [code for code, verbose in LANGUAGES]:
                raise ImproperlyConfigured(UNKNOWN_LANGUAGE_CODE_ERROR.format(current))
            return None
        return smart_str(val, errors='ignore')

    def __unicode__(self):
        return unicode(self.__repr__()) or u''

    def as_xml(self):
        u"""Returns this instance as XML."""
        xml_to_return = etree.Element(u'languages')
        for key, value in self.__dict__.iteritems():
            if key != u'languages':
                language = etree.Element(u'language', code=key)
                language.text = value.name if value else u''
                xml_to_return.append(language)
        return etree.tostring(xml_to_return)
