from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import (
    SubfieldBase,
    Field
)
from django.db.models.fields.files import FieldFile
from django.utils.translation import get_language

from lxml import objectify, etree

from . import LANGUAGES
from .datastructures import MultiLingualText
from .forms import (
    MultiLingualTextFieldForm,
    MultiLingualCharFieldForm,
    MultiLingualFileFieldForm
)

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [
            "^multilingualfield\.fields\.MultiLingualTextField",
            "^multilingualfield\.fields\.MultiLingualCharField",
            "^multilingualfield\.fields\.MultiLingualFileField",
        ]
    )

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
            <language code="en">
                Hello
            </language>
            <language code="es">
                Hola
            </language>
        </languages>
        """
        if isinstance(value, MultiLingualText):
            xml_to_return = etree.Element("languages")
            for language_code, language_verbose in LANGUAGES:
                language = etree.Element("language", code=language_code)
                language.text = getattr(value, language_code)
                xml_to_return.append(language)

            return etree.tostring(xml_to_return)
        else:
            try:
                xml_as_python_object = objectify.fromstring(value)
            except etree.XMLSyntaxError:
                raise Exception("""Multi Lingual field instances must be created with either an instance of `multilingualfield.fields.MultiLingualText` or a block of XML in the following format:
<languages>
    <language code="en">
        Hello
    </language>
    <language code="es">
        Hola
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

class MultiLingualFileField(Field):
    """
    A django FileField for storing multiple files (by language)
    in a single field.
    """
    description = "Stores multiple files, organized by language. An example use case: I want to store a separate PDF for this model instance for each language on the site."

    __metaclass__ = SubfieldBase

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        self.individual_widget_max_length = kwargs.get('max_length', None)
        if self.individual_widget_max_length:
            # Removing max_length so syncdb/south don't make a DB column
            # that's too small for future language additions
            del kwargs['max_length']

        for arg in ('primary_key', 'unique'):
            if arg in kwargs:
                raise TypeError("'%s' is not a valid argument for %s." % (arg, self.__class__))

        self.storage = storage or default_storage
        self.upload_to = upload_to
        if callable(upload_to):
            self.generate_filename = upload_to

        kwargs['max_length'] = kwargs.get('max_length', 100)
        super(MultiLingualFileField, self).__init__(verbose_name, name, **kwargs)

    def db_type(self, connection):
        return 'text'

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            'form_class': MultiLingualFileFieldForm,
            'individual_widget_max_length':self.individual_widget_max_length,
            'storage': self.storage,
            'upload_to': self.upload_to
        }
        defaults.update(kwargs)
        return super(MultiLingualFileField, self).formfield(**defaults)
