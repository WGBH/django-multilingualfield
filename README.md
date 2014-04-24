# django-multilingualfield #

## About ##

A [south](http://south.aeracode.org/)-compatible suite of django fields that make it easy to manage multiple translations of text-based content (including files/images).

### Current Version ###

0.3

## Requirements ##

* `django-classy-tags` >= 0.3.4.1
* `lxml` >= 3.1.2

## Installation ##

Installation is easy with [pip](https://pypi.python.org/pypi/pip):

```
$ pip install django-multilingualfield
```

### Settings ###

To use `django-multilingualfield`, first add `multilingualfield` to `INSTALLED_APPS`:

```
INSTALLED_APPS += ('multilingualfield')
```

Secondly, make sure that [`LANGUAGES`](https://docs.djangoproject.com/en/dev/ref/settings/#languages) is properly defined in your settings file.

If you don't have [`LANGUAGE_CODE`](https://docs.djangoproject.com/en/dev/ref/settings/#language-code) set in your settings file it will default to 'en-us' (U.S. English). It is recommended you manually set [`LANGUAGE_CODE`](https://docs.djangoproject.com/en/dev/ref/settings/#language-code) (even if you are keeping the default value of 'en-us') *IN ADDITION TO* adding an entry for that language code (as the _first_ language) in [`LANGUAGES`](https://docs.djangoproject.com/en/dev/ref/settings/#languages). Here's an example:

```
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Espa&#241;ol') # See note below note
]
```
> ##### NOTE #####
> `&#241;` is the UTF8 encoding for 'ñ'

If you'd like to use MultiLingual* fields in templates you'll need django's `'django.middleware.locale.LocalMiddleware'` added to your [`MIDDLEWARE_CLASSES`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MIDDLEWARE_CLASSES) setting and `'django.core.context_processors.i18n'` added to your [`TEMPLATE_CONTEXT_PROCESSORS`](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATE_CONTEXT_PROCESSORS) setting:

```
MIDDLEWARE_CLASSES += (
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.i18n',
)
```

> ##### NOTE #####
> django-multilingualfield uses [`django.utils.translation.get_language`](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.translation.get_language) to determine which translation to serve by default.
> To better understand how Django determines language preference read the aptly titled ['How Django discovers language preference'](https://docs.djangoproject.com/en/dev/topics/i18n/translation/#how-django-discovers-language-preference) section from the i18n topic page within the official django documentation.

## Overview ##

django has [excellent translation tools](https://docs.djangoproject.com/en/dev/topics/i18n/translation/) but a recent project at WGBH required manually-written translations for nearly all text & image content served by the site.

I didn't want to create multiple `CharField`, `TextField` or `ImageField` attributes for each field that needed translations (i.e. 'title_en' and 'title_es') for multiple reasons:

1. They'd be a giant pain to keep track of.
2. Templates and/or views would be polluted with alot of crufty if/else statements.
3. The site needed to launch with support for English and Spanish but I figured new languages would be added down the road and wanted to make any future additions as smooth as possible.

### Available Fields ###

`django-multilingualfield` contains three fields ready-for-use in your django project.

1. `multilingualfield.fields.MultiLingualCharField`: Functionality mirrors that of django's `django.db.models.CharField`
2. `multilingualfield.fields.MultiLingualTextField`: Functionality mirrors that of django's `django.db.models.TextField`
2. `multilingualfield.fields.MultiLingualFileField`: Functionality mirrors that of django's `django.db.models.FileField`

At the database level, `MultiLingualCharField`, `MultiLingualTextField` and `MultiLingualFileField` are essentially identical in that their content is stored within 'text' columns (as opposed to either 'varchar' or 'text'); they diverge only in the widgets/forms they use.

Any options you would pass to a `CharField`, `TextField` or `FileField` (i.e. `blank=True`, `max_length=50`, `upload_to='path/'`, `storage=StorageClass()`) will work as expected but `max_length` **will not be enforced at a database level** (only during form creation and input validation).

## Examples ##

### Model Example ###

Use `MultiLingualCharField`, `MultiLingualTextField` and `MultiLingualFileField` just like you would any django field:

```
from django.db import models

from multilingualfield import fields as mlf_fields

class TestModel(models.Model):
    title = mlf_fields.MultiLingualCharField(
        max_length=180
    )
    short_description = mlf_fields.MultiLingualCharField(
        max_length=300
    )
    long_description = mlf_fields.MultiLingualTextField(
        blank=True,
        null=True
    )
    image = mlf_fields.MultiLingualFileField(
        upload_to='images/',
        blank=True,
        null=True
    )
```

`django-multilingualfield` is fully integrated with [south](http://south.aeracode.org/) so migrate to your heart's content!

##### What's Stored In The Database #####

If `LANGUAGES` is set in your project's settings like this...

```
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Espa&#241;ol')
]
```

...then `django-multilingualfield` will store translations for a piece of text in a single 'text' db column as XML in the following structure:

```
<languages>
    <language code="en">
        Hello
    </language>
    <language code="es">
        Hola
    </language>
</languages>
```
 > ##### NOTE #####
 > The example above includes whitespace for readability, the final value stored in the database will have all between-tag whitespace removed.

##### What's Served By The Application #####

Even though `MultiLingualCharField` and `MultiLingualTextField` instances are stored in the database as XML they are served to the application as a python object. The above block of XML would return an instance of `multilingualfield.fields.MultiLingualText` with two attributes:

* `en` (with a value of `u'Hello'`)
* `es` (with a value of `u'Hola'`)

The translation corresponding to the current language of the active thread (as determined by calling [`django.utils.translation.get_language`](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.translation.get_language)) will be returned by directly accessing the field.

##### Creating Instances in the Shell #####

Let's create an instance of our above example model (`TestModel`) in the python shell:

```
$ python manage.py shell
```

```
>>> from testapp.models import TestModel
>>> from multilingualfield.datastructures import MultiLingualText
>>> title = MultiLingualText()
>>> title.en = 'Hello'
>>> title.es = 'Hola'
>>> x = TestModel(title=title)
>>> x.save()
>>> x.title.en
u'Hello'
>>> x.title.es
u'Hola'
>>> x.title
u'Hello'
>>> from django.utils.translation import get_language, activate
>>> get_language()
'en-us'
# NOTE: 'en-us' will ALWAYS be the current language in the active
# thread when you load the python shell via manage.py. To learn why
# visit: https://code.djangoproject.com/ticket/12131#comment:6
>>> activate('en')
>>> get_language()
'en'
>>> activate('es')
>>> get_language()
'es'
>>> x.title
u'Hola'
>>> activate('en')
>>> x.title
'en'
```

### Admin Integration ###

Both `MultiLingualCharField` and `MultiLingualTextField` are admin-ready and will provide either a `TextInput` (for `MultiLingualCharField` instances) or `Textarea` (for `MultiLingualTextField` instances) field for each language listed in `settings.LANGUAGES`.

#### Improved Admin Styling ####

The default formfields for MultiLingual* fields do not include admin-friendly styling so if you want them to look pretty within the admin you have a few options:

1. Swap-out `admin.ModelAdmin` for `MultiLingualFieldModelAdmin` in your admin configs for models that have MultiLingual* fields:

    ```
    # testapp.admin
    from django.contrib import admin

    from multilingualfield.admin import MultiLingualFieldModelAdmin

    from .models import TestModel


    class TestModelAdmin(MultiLingualFieldModelAdmin):
        """
        Adds admin-friendly styling to all MultiLingual* fields
        for TestModel within the admin
        """
        list_display = ('title',)

    admin.site.register(TestModel, TestModelAdmin)
    ```

2. Manually specify MultiLingual* widgets with [`formfield_overrides`](https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.formfield_overrides):

    ```
    # testapp.admin
    from django.contrib import admin

    from multilingualfield import widgets as mlf_widgets
    from multilingualfield import fields as mlf_fields

    from .models import TestModel


    class TestModelAdmin(admin.ModelAdmin):
        """
        Adds admin-friendly styling to all MultiLingual* fields
        for TestModel via formfield_overrides
        """
        list_display = ('title',)
        formfield_overrides = {
            mlf_fields.MultiLingualCharField: {
                'widget': mlf_widgets.MultiLingualCharFieldDjangoAdminWidget
            },
            mlf_fields.MultiLingualTextField: {
                'widget': mlf_widgets.MultiLingualTextFieldDjangoAdminWidget
            },
        }

    admin.site.register(TestModel, TestModelAdmin)
    ```

3. Manually specify MultiLingual* widgets on a ModelForm subclass:

    ```
    # testapp.forms
    from django.forms.models import ModelForm

    from multilingualfield import widgets as mlf_widgets

    from .models import TestModel


    class TestModelForm(ModelForm):

        class Meta:
            model = TestModel
            fields=(
                'title',
                'short_description',
                'long_description'
            )
            widgets = {
                'title': mlf_widgets.MultiLingualCharFieldDjangoAdminWidget,
                'short_description': mlf_widgets.MultiLingualCharFieldDjangoAdminWidget,
                'long_description': mlf_widgets.MultiLingualTextFieldDjangoAdminWidget
            }
    ```

    Integrating the custom form into your admin configuration:

    ```
    # testapp.admin
    from django.contrib import admin

    from .forms import TestModelForm
    from .models import TestModel


    class TestModelAdmin(admin.ModelAdmin):
        """
        Adds admin-friendly styling to all MultiLingual* fields
        via a custom form
        """
        form = TestModelForm

    admin.site.register(TestModel, TestModelAdmin)
    ```

### Template Example ###

Template usage is simple & straight forward, here's an example template for how you might render a instance of `TestModel`:

```
{% load i18n %}
<html>
    <head>
        <title>{{ object.title }}</title>
    </head>
    <body>
        <h1>{{ object.title }}</h2>
        <p>{{ object.short_description }}</p>
        {% if object.long_description %}
            {{ object.long_description }}
        {% else %}
            {% trans 'No long description provided' %}
        {% endif %}
    </body>
</html>
```

> ##### NOTE #####
> For more information about the `trans` templatetag used in the example above check out the [django docs](https://docs.djangoproject.com/en/dev/topics/i18n/translation/#trans-template-tag).

The example above is typical for most use cases (when you want to render values associated with the user's current language thread) but you always have access to the language-specific attributes:

```
{% load i18n %}
<html>
    <head>
        <title>{{ object.title }}</title>
    </head>
    <body>
        <h1>{{ object.title }}</h2>
        <!-- Forcing the English display of object.title -->
        <h2>{% trans 'Title (English)' %}: {{ object.title.en }}</h2>

        <!-- Forcing the Spanish display of object.title -->
        <h2>{% trans 'Title (Spanish)' %}: {{ object.title.es }}</h2>

        <p>{{ object.short_description }}</p>
        {% if object.long_description %}
            {{ object.long_description }}
        {% else %}
            {% trans 'No long description provided' %}
        {% endif %}
    </body>
</html>
```

# TODO
* Version bump
* Upload to PyPI (adjust installation docs prior)
