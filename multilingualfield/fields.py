from django.db.models import (
    SubfieldBase,
    Field
)

from south.modelsinspector import add_introspection_rules

from multilingualfield import LANGUAGES
from multilingualfield.forms import (
    MultiLingualTextForm
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
    A django field for storing multiple manually-written
    translations of the same piece of text.
    """
    description = "Stores multiple manually-written translations of the same piece of text."

    __metaclass__ = SubfieldBase

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': MultiLingualTextForm}
        defaults.update(kwargs)
        return super(MultiLingualTextField, self).formfield(**defaults)