from django.contrib.admin import ModelAdmin

from . import widgets
from .fields import MultiLingualCharField, MultiLingualTextField


class MultiLingualFieldModelAdmin(ModelAdmin):
    formfield_overrides = {
        MultiLingualCharField: {
            'widget': widgets.MultiLingualCharFieldDjangoAdminWidget
        },
        MultiLingualTextField: {
            'widget': widgets.MultiLingualTextFieldDjangoAdminWidget
        },
    }
