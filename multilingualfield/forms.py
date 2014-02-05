from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.forms import CharField, MultiValueField, ValidationError, FileField
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from lxml import etree

from . import widgets, LANGUAGES, LANGUAGES_REPLACEMENT, LANGUAGES_REQUIRED_TEXT, REQUIRED_ERROR

# This list is used to validate file uploads
FILE_FIELD_CLASSES = File.__subclasses__() + [TemporaryUploadedFile, InMemoryUploadedFile]


class MultiLingualTextField(MultiValueField):
    u"""The field used by MultiLingualTextField."""
    widget = widgets.MultiLingualTextFieldWidget

    def widget_attrs(self, widget):
        u"""
        Given a Widget instance (*not* a Widget class), returns a dictionary of any HTML attributes that should be added
        to the Widget, based on this Field.
        """
        return {u'maxlength': self.individual_widget_max_length} if self.individual_widget_max_length else {}

    def __init__(self, *args, **kwargs):
        self.individual_widget_max_length = kwargs.get(u'individual_widget_max_length', None)
        if u'individual_widget_max_length' in kwargs:
            del kwargs[u'individual_widget_max_length']
        self.mandatory_field = kwargs[u'required']
        kwargs[u'required'] = False
        # Uncomment the next line when django 1.7 is released
        #kwargs[u'require_all_fields'] = kwargs[u'required'] = False
        fields = []
        for code, verbose in LANGUAGES:
            field = CharField(label=verbose, required=self.mandatory_field and code not in LANGUAGES_REPLACEMENT,
                              max_length=self.individual_widget_max_length)
            field.error_messages.setdefault(u'incomplete', REQUIRED_ERROR.format(verbose))
            fields.append(field)
        super(MultiLingualTextField, self).__init__(tuple(fields), *args, **kwargs)

    def compress(self, data_list):
        u"""
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
        xml = etree.Element(u'languages')
        if self.mandatory_field and not data_list:
            raise ValidationError(REQUIRED_ERROR.format(LANGUAGES_REQUIRED_TEXT))
        elif data_list:
            for index, entry in enumerate(data_list):
                code, verbose = LANGUAGES[index]
                language = etree.Element(u'language', code=code)
                if code not in LANGUAGES_REPLACEMENT and not entry and self.mandatory_field:
                    raise ValidationError(REQUIRED_ERROR.format(verbose))
                language.text = entry
                xml.append(language)
        return etree.tostring(xml)


class MultiLingualCharField(MultiLingualTextField):
    u"""The field used by MultiLingualCharField."""
    widget = widgets.MultiLingualCharFieldWidget


class FileOrAlreadyExistantFilePathField(FileField):
    u"""
    A FileField subclass that provides either an instance of a 'File' (as determined by FILE_FIELD_CLASSES), a bool
    (which means the file is being 'cleared' from a model instance) or a str/unicode (a path to an existent file).
    """

    def clean(self, data, initial=None):
        # If the widget got contradictory inputs, we raise a validation error
        if not type(data) in File.__subclasses__():
            return data
        if data is FILE_INPUT_CONTRADICTION:
            raise ValidationError(self.error_messages[u'contradiction'])
        # False means the field value should be cleared; further validation is not needed.
        if data is False:
            if not self.required:
                return False
            # If the field is required, clearing is not possible (the widget shouldn't return False data in that
            # case anyway). False is not in validators.EMPTY_VALUES; if a False value makes it this far it should be
            # validated from here on out as None (so it will be caught by the required check).
            data = None
        return initial if (not data and initial) else super(FileOrAlreadyExistantFilePathField, self).clean(data)


class MultiLingualFileField(MultiValueField):
    u"""The field used by MultiLingualFileField."""
    widget = widgets.MultiLingualClearableFileInputWidget

    def widget_attrs(self, widget):
        u"""
        Given a Widget instance (*not* a Widget class), returns a dictionary of any HTML attributes that should be added
        to the Widget, based on this Field.
        """
        return {u'maxlength': self.individual_widget_max_length} if self.individual_widget_max_length else {}

    def __init__(self, *args, **kwargs):
        self.individual_widget_max_length = kwargs.get(u'individual_widget_max_length', None)
        if u'individual_widget_max_length' in kwargs:
            del kwargs[u'individual_widget_max_length']
        self.mandatory_field = kwargs[u'required']
        fields = [
            FileOrAlreadyExistantFilePathField(label=verbose, max_length=self.individual_widget_max_length)
            for code, verbose in LANGUAGES
        ]
        super(MultiLingualFileField, self).__init__(tuple(fields), *args, **kwargs)

    def compress(self, data_list):
        u"""
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
        #languages = [code for code, verbose in LANGUAGES]
        #xml = etree.Element(u'languages')
        if self.mandatory_field and not data_list:
            raise ValidationError(REQUIRED_ERROR.format(LANGUAGES_REQUIRED_TEXT))
        elif data_list:
            for index, this_file in enumerate(data_list):
                code, verbose = LANGUAGES[index]
                if (code not in LANGUAGES_REPLACEMENT and self.mandatory_field
                    and not this_file and not type(this_file) in FILE_FIELD_CLASSES):
                    raise ValidationError(REQUIRED_ERROR.format(verbose))
        return data_list
