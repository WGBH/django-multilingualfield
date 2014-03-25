from __future__ import absolute_import, division, print_function, unicode_literals

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag
from django import template
from django.conf import settings

register = template.Library()


class GetTranslationForContext(AsTag):
    u"""
    Retrieves the correct 'translation' for a MultiLingualText instance based
    on the language in the current thread (by calling
    `django.utils.translation.get_language()`).

    Can be used as a standalone tag::

        {% get_for_current_language object.title %}

    Or assigned to a context variable with as::

        {% get_for_current_language object.title as the_title %}
        {{ the_title }}
    """
    name = u'get_for_current_language'
    options = Options(
        Argument(u'attr', required=True),
        u'as',
        Argument(u'varname', required=False, resolve=False)
    )

    def get_value(self, context, attr):
        try:
            return getattr(
                attr,
                context.get(u'LANGUAGE_CODE', settings.LANGUAGES[0][0])
            )
        except AttributeError:
            return u''


class GetTranslationByLanguageCode(AsTag):
    u"""
    Retrieves a specific 'translation' for a MultiLingualText instance.

    Can be used as a standalone tag::

        {% get_trans_by_code object.title 'en' %}

    Or assigned to a context variable with as::

        {% get_trans_by_code object.title 'en' as the_title %}
        {{ the_title }}
    """
    name = u'get_trans_by_code'
    options = Options(
        Argument(u'attr', required=True),
        Argument(u'language_code', required=True),
        u'as',
        Argument(u'varname', required=False, resolve=False)
    )

    def get_value(self, context, attr, language_code):
        try:
            return getattr(attr, language_code)
        except AttributeError:
            return u''


register.tag(GetTranslationForContext)
register.tag(GetTranslationByLanguageCode)
