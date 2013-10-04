from django.forms.widgets import (
    CheckboxInput,
    ClearableFileInput,
    HiddenInput,
    MultiWidget,
    Textarea,
    TextInput,
    Widget
)
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from lxml import objectify
from lxml.etree import XMLSyntaxError

from . import LANGUAGES, INVALID_XML_ERROR
from .datastructures import MultiLingualText

class WidgetWithLanguageLabel(object):
    u"""A form widget which prepends a <label> tag corresponding to a language in settings.LANGUAGES."""

    def __init__(self, attrs, language=None):
        self.label = language[1]
        self.language_code = language[0]
        super(WidgetWithLanguageLabel, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        widget = super(WidgetWithLanguageLabel, self).render(name, value, attrs)
        # Add a class depending of the language_code, maybe useful for some jQuery functions like toggle() ;-)
        widget = mark_safe('<div class="control-group language_%s"><label class="control-label">%s</label>'
                           '<div class="controls">%s</div></div>' % (self.language_code, self.label, widget))
        return widget

class TextareaWithLabel(WidgetWithLanguageLabel, Textarea):
    u"""
    A form widget which prepends a <label> tag to Textarea widget corresponding to a language in settings.LANGUAGES.
    """
    pass

class TextInputWithLabel(WidgetWithLanguageLabel, TextInput):
    u"""
    A form widget which prepends a <label> tag to a TextInput widget corresponding to a language in settings.LANGUAGES.
    """
    pass

class CustomClearableFileInput(ClearableFileInput):
    u"""
    Identical to `ClearableFileInput` only it includes an extra hidden field (`initial_file`) which passes along the
    existing file name of the file associated with this field (if one exists).
    """
    template_with_initial = '%(initial_file)s %(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'

    def initial_filename_name(self, name):
        u"""Given the name of the hidden initial_text input, return the HTML id for it."""
        return name + '-initial'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>', value.url, force_text(value))
            initial_filename_name = self.initial_filename_name(name)
            substitutions['initial_file'] = HiddenInput().render(initial_filename_name, value, attrs={'id': initial_filename_name})
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    def value_from_datadict(self, data, files, name):
        upload = super(CustomClearableFileInput, self).value_from_datadict(data, files, name)

        if not self.is_required and CheckboxInput().value_from_datadict(
            data, files, self.clear_checkbox_name(name)):
            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        # If no file has been uploaded...
        if upload is None:
            # ...figure out the name of the
            # hidden field which holds the existant filename (if one exists)
            initial_filename = self.initial_filename_name(name)
            if data.get(initial_filename, None):
                # If that hidden field is in the widget, pass the
                # file path of that file on
                return data.get(initial_filename)
            else:
                # Otherwise return None
                return None
        # Otherwise...
        else:
            # Return the uploaded file.
            return upload


class ClearableFileInputWithLabel(WidgetWithLanguageLabel, CustomClearableFileInput):
    u"""
    A form widget which prepends a <label> tag to a TextInput widget corresponding to a language in settings.LANGUAGES.
    """


class MultiLingualFieldBaseMixInWidget(object):
    u"""
    The 'base' multilingual field widget. Returns a widget (as specified by the `for_each_field_widget` attribute) for
    each language specified in settings.LANGUAGES.
    """

    for_each_field_widget = None

    def __init__(self, attrs=None):
        widgets = [
            self.for_each_field_widget(attrs, language=language)
            for language in LANGUAGES
        ]
        super(MultiLingualFieldBaseMixInWidget, self).__init__(widgets, attrs)

class MultiLingualTextFieldWidget(MultiLingualFieldBaseMixInWidget, MultiWidget):
    u"""
    A widget that returns a `Textarea` widget for each language specified in settings.LANGUAGES.
    """
    for_each_field_widget = TextareaWithLabel

    def decompress(self, value):
        u"""
        Receives an instance of `MultiLingualText` (or a properly-formatted block of XML) and returns a list of values
        corresponding in position to the current ordering of settings.LANGUAGES.
        """
        language_text_as_dict = {}
        if value:
            # Both MultiLingualCharField and MultiLingualTextField instances
            # provide `MultiLingualText` instances by default but handling
            # for raw XML has been included for convenience.
            if isinstance(value, MultiLingualText):
                for language_code, language_verbose in LANGUAGES:
                    language_text_as_dict[language_code] = getattr(value, language_code)
            else:
                # Converting XML (passed-in as `value`) to a python object via lxml
                try:
                    xml_as_python_object = objectify.fromstring(value)
                except XMLSyntaxError:
                    raise Exception(INVALID_XML_ERROR + ' MultiLingualTextFieldWidget.decompress()!')
                else:
                    # Creating a dictionary of all the languages passed in the value XML
                    # with the language code (i.e. 'en', 'de', 'fr') as the key
                    for language in xml_as_python_object.language:
                        language_text = language.language_text
                        if not language_text:
                            language_text_as_unicode = ''
                        else:
                            language_text_as_unicode = unicode(language_text)
                        language_text_as_dict[unicode(language.language_code)] = language_text_as_unicode
        # Returning text from XML tree in order dictated by LANGUAGES
        return [
            language_text_as_dict[language_code]
            if language_code in language_text_as_dict else ""
            for language_code, language_verbose in LANGUAGES
        ]

class MultiLingualCharFieldWidget(MultiLingualTextFieldWidget):
    u"""A widget that returns a `TextInput` widget for each language specified in settings.LANGUAGES."""
    for_each_field_widget = TextInputWithLabel

class MultiLingualClearableFileInputWidget(MultiLingualFieldBaseMixInWidget, MultiWidget):
    u"""
    A widget that returns a `ClearableFileInput` widget for each language specified in settings.LANGUAGES.
    """
    for_each_field_widget = ClearableFileInputWithLabel

    def decompress(self, value):
        u"""
        Receives an instance of `MultiLingualFile` and returns a list of broken-out-files corresponding in position to
        the current ordering of settings.LANGUAGES.
        """

        language_text_as_dict = {}
        if value:
            for language_code, language_verbose in LANGUAGES:
                language_text_as_dict[language_code] = getattr(value, language_code)
        # Returning text from XML tree in order dictated by LANGUAGES
        return [
            language_text_as_dict[language_code]
            if language_code in language_text_as_dict else None
            for language_code, language_verbose in LANGUAGES
        ]
