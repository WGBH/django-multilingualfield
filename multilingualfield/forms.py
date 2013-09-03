import os

from django.db.models.fields.files import FieldFile
from django.forms import (
    CharField,
    MultiValueField,
    ValidationError,
    FileField
)

from lxml import etree

from . import LANGUAGES
from .widgets import (
    MultiLingualCharFieldWidget,
    MultiLingualTextFieldWidget,
    MultiLingualClearableFileInputWidget
)

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
        # Pulling `storage` and `upload_to` from field.formfield()
        self.storage = kwargs.get('storage', None)
        self.upload_to = kwargs.get('upload_to', None)
        # Then deleting them so superclasses won't get confused
        del kwargs['storage']
        del kwargs['upload_to']
        self.mandatory_field = kwargs['required']
        kwargs['required'] = False
        fields = [
            FileField(
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
                language = etree.Element("language", code=languages[index])
                if index == 0 and self.mandatory_field and not this_file:
                    raise ValidationError('This multi-lingual field is required therefore you must enter text in the `%s` field.' % LANGUAGES[0][1])
                if this_file:
                    # Figure out 'intended' file name and path
                    file_name_and_path = os.path.join(self.upload_to, this_file.name)
                    # Create file using this field's storage (as provided by the parent fields 'formfield' method)
                    created_file_name = self.storage.save(file_name_and_path, this_file)
                    # Finally, assign the created file name to the XML block
                    language.text = created_file_name
                xml.append(language)
        return etree.tostring(xml)
