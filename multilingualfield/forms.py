from django.core.files.base import File
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    TemporaryUploadedFile
)
from django.forms import (
    CharField,
    MultiValueField,
    ValidationError,
    FileField
)
from django.forms.widgets import CheckboxInput, FILE_INPUT_CONTRADICTION

from lxml import etree

from . import LANGUAGES
from .widgets import (
    MultiLingualCharFieldWidget,
    MultiLingualTextFieldWidget,
    MultiLingualClearableFileInputWidget
)

# This list is used to validate file uploads
FILE_FIELD_CLASSES = File.__subclasses__() + [
                                TemporaryUploadedFile,
                                InMemoryUploadedFile
                            ]

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
        self.mandatory_field = kwargs['required']
        kwargs['required'] = False
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
        if self.mandatory_field and not data_list:
            raise ValidationError('This multi-lingual field is required therefore you must enter text in `%s` field.' % LANGUAGES[0][1])
        elif data_list:
            for index, entry in enumerate(data_list):
                language = etree.Element("language", code=languages[index])
                if index == 0 and self.mandatory_field and not entry:
                    raise ValidationError('This multi-lingual field is required therefore you must enter text in the `%s` field.' % LANGUAGES[0][1])
                language.text = entry
                xml.append(language)
        return etree.tostring(xml)

class MultiLingualCharFieldForm(MultiLingualTextFieldForm):
    """
    The form used by MultiLingualCharField
    """
    widget = MultiLingualCharFieldWidget

class FileOrAlreadyExistantFilePathField(FileField):
    """
    A FileField subclass that provides either an instance of a 'File'
    (as determined by FILE_FIELD_CLASSES), a bool (which means the file
    is being 'cleared' from a model instance) or a str/unicode (a path
    to an existant file).
    """

    def clean(self, data, initial=None):
        # If the widget got contradictory inputs, we raise a validation error
        if type(data) in File.__subclasses__():
            if data is FILE_INPUT_CONTRADICTION:
                raise ValidationError(self.error_messages['contradiction'])
            # False means the field value should be cleared; further validation is
            # not needed.
            if data is False:
                if not self.required:
                    return False
                # If the field is required, clearing is not possible (the widget
                # shouldn't return False data in that case anyway). False is not
                # in validators.EMPTY_VALUES; if a False value makes it this far
                # it should be validated from here on out as None (so it will be
                # caught by the required check).
                data = None
            if not data and initial:
                return initial
            return super(FileOrAlreadyExistantFilePathField, self).clean(data)
        else:
            return data

class MultiLingualFileFieldForm(MultiValueField):
    """
    The form used by MultiLingualFileField
    """
    widget = MultiLingualClearableFileInputWidget

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
        self.mandatory_field = kwargs['required']
        kwargs['required'] = False
        fields = [
            FileOrAlreadyExistantFilePathField(
                label=language_verbose,
                max_length=self.individual_widget_max_length
            )
            for language_code, language_verbose in LANGUAGES
        ]
        super(MultiLingualFileFieldForm, self).__init__(tuple(fields), *args, **kwargs)

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
        if self.mandatory_field and not data_list:
            raise ValidationError('This multi-lingual field is required therefore you must enter text in `%s` field.' % LANGUAGES[0][1])
        elif data_list:
            for index, this_file in enumerate(data_list):
                if index == 0 and self.mandatory_field and not this_file and not type(this_file) in FILE_FIELD_CLASSES:
                        raise ValidationError('This multi-lingual field is required therefore you must enter text in the `%s` field.' % LANGUAGES[0][1])
        return data_list
