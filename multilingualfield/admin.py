from django.contrib.admin import ModelAdmin

from . import widgets, fields


class MultiLingualFieldModelAdmin(ModelAdmin):
    formfield_overrides = {
        fields.MultiLingualCharField: {
            'widget': widgets.MultiLingualCharFieldDjangoAdminWidget
        },
        fields.MultiLingualTextField: {
            'widget': widgets.MultiLingualTextFieldDjangoAdminWidget
        },
        fields.MultiLingualFileField: {
            'widget': widgets.MultiLingualClearableFileInputDjangoAdminWidget
        },
    }
