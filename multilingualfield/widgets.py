from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from django.forms.widgets import (
    CheckboxInput, ClearableFileInput, HiddenInput,
    MultiWidget, Textarea, TextInput, FILE_INPUT_CONTRADICTION
)
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from lxml import objectify
from lxml.etree import XMLSyntaxError

from . import datastructures, LANGUAGES, INVALID_XML_ERROR


class WidgetWithLanguageAddOn(object):
    u"""
    A form widget which appends an <add-on> tag corresponding to a
    language in ``settings.LANGUAGES``.

    Add a class depending of the ``language_code``, maybe useful
    for some jQuery functions like ``toggle()``.
    """

    def __init__(self, attrs, language=None):
        self.language_code, self.label = language
        super(WidgetWithLanguageAddOn, self).__init__(attrs)

    def render(self, *args, **kwargs):
        # FIXME do something with self.label ?
        html = super(WidgetWithLanguageAddOn, self).render(*args, **kwargs)
        return mark_safe(u'<div class="input-prepend tab_element tab_link_{0}">'
                         u'<span class="add-on control-label">{2}</span>{1}'
                         u'</div>'.format(self.language_code, html, self.label))


class WidgetWithLanguageLabel(object):
    u"""
    A form widget which prepends a <label> tag corresponding to a
    language in settings.LANGUAGES.

    Add a class depending of the ``language_code``, maybe useful for
    some jQuery functions like ``toggle()``.
    """

    def __init__(self, attrs, language=None):
        self.language_code, self.label = language
        super(WidgetWithLanguageLabel, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        html = super(WidgetWithLanguageLabel, self).render(name, value, attrs)
        return mark_safe(u'<div class="control-group tab_element tab_link{0}">'
                         u'<label class="control-label">{1}</label><div class="controls">{2}</div></div>'.format(
                         self.language_code, self.label, html))


class CustomClearableFileInput(ClearableFileInput):
    u"""
    Identical to `ClearableFileInput` only it includes an extra hidden field
    (`initial_file`) which passes along the existing file name of the file
    associated with this field (if one exists).
    """
    template_with_initial = (
        u'%(initial_file)s %(initial_text)s: '
        u'%(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
    )
    template_with_clear = (
        '<span class="clearable-file-input">'
        '%(clear)s'
        '<label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
        '</span>'
    )

    def initial_filename_name(self, name):
        u"""
        Given the name of the hidden initial_text input,
        return the HTML id for it.
        """
        return name + u'-initial'

    def render(self, name, value, attrs=None):
        substitutions = {
            u'initial_text': self.initial_text,
            u'input_text': self.input_text,
            u'clear_template': u'',
            u'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        substitutions[u'input'] = super(ClearableFileInput, self).render(
            name,
            value,
            attrs
        )

        if value and hasattr(value, u'url'):
            template = self.template_with_initial
            substitutions[u'initial'] = format_html(
                u'<a href="{0}">{1}</a>',
                value.url,
                force_text(value)
            )
            initial_filename_name = self.initial_filename_name(name)
            substitutions[u'initial_file'] = HiddenInput().render(
                initial_filename_name,
                value,
                attrs={u'id': initial_filename_name}
            )
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions[u'clear_checkbox_name'] = conditional_escape(
                    checkbox_name
                )
                substitutions[u'clear_checkbox_id'] = conditional_escape(
                    checkbox_id
                )
                substitutions[u'clear'] = CheckboxInput().render(
                    checkbox_name,
                    False,
                    attrs={u'id': checkbox_id}
                )
                substitutions[u'clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    def value_from_datadict(self, data, files, name):
        upload = super(CustomClearableFileInput, self).value_from_datadict(
            data,
            files,
            name
        )

        if not self.is_required and CheckboxInput().value_from_datadict(
                data,
                files,
                self.clear_checkbox_name(name)):
            # If the user contradicts themselves (uploads a new file AND checks
            # the "clear" checkbox), we return a unique marker object that
            # FileField will turn into a ValidationError. False signals to
            # clear any existing value, as opposed to just None
            return FILE_INPUT_CONTRADICTION if upload else False
        # Return the uploaded file or figure out the name of the hidden field
        # which holds the existant filename (if one exists)  If that hidden
        # field is in the widget, pass the file path of that file on, defaults
        # to None
        return upload or data.get(self.initial_filename_name(name), None)


class MultiLingualFieldBaseMixInWidget(object):
    u"""
    The 'base' multilingual field widget. Returns a widget (as specified by
    the `for_each_field_widget` attribute) for each language specified in
    settings.LANGUAGES.
    """

    for_each_field_widget = None

    def __init__(self, attrs=None):
        widgets = [
            self.for_each_field_widget(attrs, language=language)
            for language in LANGUAGES
        ]
        super(MultiLingualFieldBaseMixInWidget, self).__init__(widgets, attrs)

    def render(self, name, value, attrs=None):
        rendered_widget = super(
            MultiLingualFieldBaseMixInWidget, self
        ).render(name, value, attrs)
        return mark_safe(
            '<div class="multilingual-mod %s">%s</div>' % (
                self.__class__.__name__.lower(),
                rendered_widget
            )
        )


class MultiLingualTextFieldWidget(MultiLingualFieldBaseMixInWidget,
                                  MultiWidget):
    u"""
    A widget that returns a `Textarea` widget for each language specified
    in settings.LANGUAGES.
    """

    class FieldWidget(WidgetWithLanguageAddOn, Textarea):
        pass
    for_each_field_widget = FieldWidget

    def decompress(self, value):
        u"""
        Receives an instance of `MultiLingualText` (or a properly-formatted
        block of XML) and returns a list of values corresponding in position
        to the current ordering of settings.LANGUAGES.
        """
        text_dict = {}
        if value:
            # Both MultiLingualCharField and MultiLingualTextField instances
            # provide `MultiLingualText` instances by default but handling
            # for raw XML has been included for convenience.
            if isinstance(value, datastructures.MultiLingualText):
                text_dict = dict(
                    (code, getattr(value, code))
                    for code, verbose in LANGUAGES
                )
            else:
                # Converting XML (passed-in as `value`) to a python object
                # via lxml
                try:
                    xml_as_python_object = objectify.fromstring(value)
                except XMLSyntaxError:
                    raise Exception(
                        INVALID_XML_ERROR + ' MultiLingualTextFieldWidget.decompress()!'
                    )
                else:
                    # Creating a dictionary of all the languages passed in the
                    # value XML with the language code (i.e. 'en', 'de', 'fr')
                    # as the key
                    text_dict = dict(
                        (unicode(l.code), unicode(l.language_text or u''))
                        for l in xml_as_python_object.language
                    )
        # Returning text from XML tree in order dictated by LANGUAGES
        return [text_dict.get(code, u'') for code, verbose in LANGUAGES]


class MultiLingualCharFieldWidget(MultiLingualTextFieldWidget):
    u"""
    A widget that returns a `TextInput` widget for each language
    specified in settings.LANGUAGES.
    """

    class FieldWidget(WidgetWithLanguageAddOn, TextInput):
        pass
    for_each_field_widget = FieldWidget


class MultiLingualClearableFileInputWidget(MultiLingualFieldBaseMixInWidget,
                                           MultiWidget):
    u"""
    A widget that returns a `ClearableFileInput` widget for each
    language specified in settings.LANGUAGES.
    """

    class FieldWidget(WidgetWithLanguageAddOn, CustomClearableFileInput):
        pass
    for_each_field_widget = FieldWidget

    def decompress(self, value):
        u"""
        Receives an instance of `MultiLingualFile` and returns a list of
        broken-out-files corresponding in position to the current ordering
        of settings.LANGUAGES.
        """
        text_dict = dict(
            (code, getattr(value, code))
            for code, verbose in LANGUAGES
        ) if value else {}
        # Returning text from XML tree in order dictated by LANGUAGES
        return [text_dict.get(code) for code, verbose in LANGUAGES]


class MultiLingualFieldDjangoAdminBaseMixInWidget(object):
    u"""
    A mix-in class that provides django admin-specific styles
    to a MultiLingualField widget.
    """
    class Media:
        css = {
            'all': ('multilingualfield/css/multilingualfield-djangoadmin.css',),
        }


class MultiLingualCharFieldDjangoAdminWidget(
        MultiLingualFieldDjangoAdminBaseMixInWidget,
        MultiLingualCharFieldWidget):
    pass


class MultiLingualTextFieldDjangoAdminWidget(
        MultiLingualFieldDjangoAdminBaseMixInWidget,
        MultiLingualTextFieldWidget):
    pass
