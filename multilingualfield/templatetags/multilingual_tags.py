from django import template
from django.conf import settings

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag

register = template.Library()

LANGUAGE_COOKIE_NAME = getattr(settings, 'LANGUAGE_COOKIE_NAME')

class GetTranslationForContext(AsTag):
    """
    Retrieves the correct 'translation' for a MultiLingualText instance based
    on the value of context['LANGUAGE_CODE']

    Can be used as a standalone tag:
    {% get_for_current_language object.title %}

    Or assigned to a context variable with as:
    {% get_for_current_language object.title as the_title %}
    {{ the_title }}
    """
    name = 'get_for_current_language'
    options = Options(
        Argument('attr', required=True),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def get_value(self, context, attr):
        current_language = context.get('LANGUAGE_CODE', settings.LANGUAGES[0][0])
        try:
            text_to_return = getattr(attr, current_language)
        except AttributeError:
            text_to_return = ''
        return text_to_return

register.tag(GetTranslationForContext)