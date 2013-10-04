import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import SubfieldBase, Field
from lxml import objectify, etree

from . import LANGUAGES, INVALID_ARGUMENT_ERROR, XML_SYNTAX_ERROR
from .datastructures import MultiLingualText, MultiLingualFile
from .forms import MultiLingualTextFieldForm, MultiLingualCharFieldForm, MultiLingualFileFieldForm, FILE_FIELD_CLASSES

if u'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            u'^multilingualfield\.fields\.MultiLingualTextField',
            u'^multilingualfield\.fields\.MultiLingualCharField',
            u'^multilingualfield\.fields\.MultiLingualFileField',
        ]
    )

class MultiLingualTextField(Field):
    u"""A django TextField for storing multiple manually-written translations of the same piece of text."""
    description = u'Stores multiple manually-written translations of the same piece of text.'

    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        self.individual_widget_max_length = kwargs.get(u'max_length', None)
        if self.individual_widget_max_length:
            # Removing max_length so syncdb/south don't make a DB column
            # that's too small for future language additions
            del kwargs[u'max_length']
        super(MultiLingualTextField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return u'text'

    def to_python(self, value):
        u"""Takes XML data from the database and converts it into an instance of MultiLingualText."""
        # Obviously MultiLingualText instances aren't stored in the database but this conditional is there
        # 'just-in-case' since a seralizer might be utilized in the future for this field.
        # -> Else : Use the XML stored in the database to create a MultiLingualText instance
        return value if isinstance(value, MultiLingualText) else MultiLingualText(xml=value)

    def get_prep_value(self, value):
        u"""
        Converts an instance of MultiLingualText into what will ultimately be stored in the database, a block of XML in
        the following format:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>
        """
        # Checks to see if this is a `MultiLingualText` instance
        if isinstance(value, MultiLingualText):
            # If it is, convert the instance to XML
            xml = value.as_xml()
        else:
            # Otherwise check to see if it is a valid block of XML
            try:
                objectify.fromstring(value)
            except etree.XMLSyntaxError:
                # If not, raise an Exception
                raise Exception(XML_SYNTAX_ERROR +
"""<languages>
    <language code="en">
        Hello
    </language>
    <language code="es">
        Hola
    </language>
</languages>
""")
            else:
                # Otherwise set `xml` to `value`
                xml = value
        return xml

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            u'form_class': MultiLingualTextFieldForm,
            u'individual_widget_max_length': self.individual_widget_max_length
        }
        defaults.update(kwargs)
        return super(MultiLingualTextField, self).formfield(**defaults)

class MultiLingualCharField(MultiLingualTextField):
    u"""A django CharField for storing multiple manually-written translations of the same piece of text."""
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            u'form_class': MultiLingualCharFieldForm,
            u'individual_widget_max_length': self.individual_widget_max_length
        }
        defaults.update(kwargs)
        return super(MultiLingualCharField, self).formfield(**defaults)

class MultiLingualFileField(Field):
    u"""A django FileField for storing multiple files (by language) in a single field."""
    description = (u'Stores multiple files, organized by language. An example use case: '
                   u'I want to store a separate PDF for this model instance for each language on the site.')

    __metaclass__ = SubfieldBase

    def __init__(self, verbose_name=None, name=None, upload_to=u'', storage=None, **kwargs):
        self.individual_widget_max_length = kwargs.get(u'max_length', None)
        if self.individual_widget_max_length:
            # Removing max_length so syncdb/south don't make a DB column
            # that's too small for future language additions
            del kwargs[u'max_length']

        for arg in (u'primary_key', u'unique'):
            if arg in kwargs:
                raise TypeError(INVALID_ARGUMENT_ERROR.format(arg, self.__class__))

        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to
        super(MultiLingualFileField, self).__init__(verbose_name, name, **kwargs)

    def db_type(self, connection):
        return u'text'

    def to_python(self, value):
        u"""Takes XML data from the database and converts it into an instance of MultiLingualFile."""
        if isinstance(value, MultiLingualFile):
            return value
        elif isinstance(value, list):
            languages = [code for code, verbose in LANGUAGES]
            xml_block = etree.Element(u'languages')
            for index, this_file in enumerate(value):
                language = etree.Element(u'language', code=languages[index])
                # If `this_file` exists and is a 'File'
                if this_file and (type(this_file) in FILE_FIELD_CLASSES):
                    # Figure out 'intended' file name and path
                    file_name_and_path = os.path.join(self.upload_to, this_file.name)
                    # Create file using this field's storage (as provided by the parent fields 'formfield' method)
                    created_file_name = self.storage.save(file_name_and_path, this_file)
                    # Finally, assign the created file name to the XML block
                    language.text = created_file_name
                # Otherwise...
                else:
                    # ...if it's a bool it means the field is being cleared, otherwise it's a filename and path.
                    language.text = u'' if isinstance(this_file, bool) else this_file
                xml_block.append(language)
            xml = etree.tostring(xml_block)
        else:
            xml = value
        return MultiLingualFile(xml=xml, storage=self.storage)

    def get_prep_value(self, value):
        u"""
        Converts an instance of MultiLingualFile into what will ultimately be stored in the database, a block of XML in
        the following format:
        <languages>
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>
        """
        # Checks to see if this is a `MultiLingualFile` instance
        return value.as_xml() if isinstance(value, MultiLingualFile) else value

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults while letting the caller override them.
        defaults = {
            u'form_class': MultiLingualFileFieldForm,
            u'individual_widget_max_length': self.individual_widget_max_length
        }
        defaults.update(kwargs)
        return super(MultiLingualFileField, self).formfield(**defaults)
