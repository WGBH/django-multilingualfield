from django.forms.widgets import (
    ClearableFileInput,
    MultiWidget,
    Textarea,
    TextInput,
    Widget
)
from django.utils.safestring import mark_safe

from lxml import objectify
from lxml.etree import XMLSyntaxError

from . import LANGUAGES
from .datastructures import MultiLingualText

class WidgetWithLanguageLabel(object):
    """
    A form widget which prepends a <label> tag corresponding
    to a language in settings.LANGUAGES
    """

    def __init__(self, attrs, language=None):
        self.label = language[1]
        self.language_code = language[0]
        super(WidgetWithLanguageLabel, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        widget = super(WidgetWithLanguageLabel, self).render(name, value, attrs)
        widget = mark_safe(
                    """<div class="control-group"><label class="control-label">%s</label><div class="controls">%s</div></div>""" % (
                                                    self.label,
                                                    widget
                                                )
                )
        return widget

class TextareaWithLabel(WidgetWithLanguageLabel, Textarea):
    """
    A form widget which prepends a <label> tag to Textarea widget
    corresponding to a language in settings.LANGUAGES
    """
    pass

class TextInputWithLabel(WidgetWithLanguageLabel, TextInput):
    """
    A form widget which prepends a <label> tag to a TextInput widget
    corresponding to a language in settings.LANGUAGES
    """
    pass

class ClearableFileInputWithLabel(WidgetWithLanguageLabel, ClearableFileInput):
    """
    A form widget which prepends a <label> tag to a TextInput widget
    corresponding to a language in settings.LANGUAGES
    """
    pass

class MultiLingualFieldBaseMixInWidget(object):
    """
    The 'base' multilingual field widget. Returns a widget (as specified by
    the `for_each_field_widget` attribute) for each language specified
    in settings.LANGUAGES
    """

    for_each_field_widget = None

    def __init__(self, attrs=None):
        widgets = [
            self.for_each_field_widget(attrs, language=language)
            for language in LANGUAGES
        ]
        super(MultiLingualFieldBaseMixInWidget, self).__init__(widgets, attrs)

class MultiLingualTextFieldWidget(MultiLingualFieldBaseMixInWidget, MultiWidget):
    """
    A widget that returns a `Textarea` widget for each language specified
    in settings.LANGUAGES
    """
    for_each_field_widget = TextareaWithLabel

    def decompress(self, value):
        """
        Receives an instance of `MultiLingualText` (or a properly-formatted
        block of XML) and returns a list of values corresponding in position
        to the current ordering of settings.LANGUAGES
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
                    raise Exception("Invalid XML was passed to MultiLingualTextFieldWidget.decompress()!")
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
    """
    A widget that returns a `TextInput` widget for each language specified
    in settings.LANGUAGES
    """
    for_each_field_widget = TextInputWithLabel

class MultiLingualClearableFileInputWidget(MultiLingualFieldBaseMixInWidget, MultiWidget):
    """
    A widget that returns a `ClearableFileInput` widget for each language specified
    in settings.LANGUAGES
    """
    for_each_field_widget = ClearableFileInputWithLabel

    def decompress(self, value):
        return []
