from django.db.models import (
    SubfieldBase,
    Field
)

from south.modelsinspector import add_introspection_rules

from multilingualfield import LANGUAGES
from multilingualfield.forms import (
    MultiLingualTextFieldForm,
    MultiLingualCharFieldForm
)

add_introspection_rules(
    [],
    [
        "^multilingualfield\.fields\.MultiLingualTextField",
        "^multilingualfield\.fields\.MultiLingualCharField",
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