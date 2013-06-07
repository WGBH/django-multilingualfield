# django-multilingualfield #

## About ##

A [south](http://south.aeracode.org/)-compatible django field for storing multiple manually-written translations for the same piece of text.

## Requirements ##

* `django-classy-tags` >= 0.3.4.1
* `lxml` >= 3.1.2

## Installation ##

`django-multilingualfield` isn't in the [CheeseShop](https://pypi.python.org/pypi) yet but it does have a setup.py so installation is easy with [pip](https://pypi.python.org/pypi/pip):

```bash
$ pip install https://github.com/WGBH/django-multilingualfield/archive/master.zip
```

or, if you downloaded the archive yourself:

```bash
$ pip install /path/to/archive.zip
```

## Overview ##

django has [excellent built-in auto-translation tools](https://docs.djangoproject.com/en/dev/topics/i18n/translation/) but a recent project at WGBH required manually-written translations for nearly all text content served by the site.

I didn't want to create multiple `CharField` or `TextField` attributes for each piece of text (i.e. 'title_en' and 'title_es') for multiple reasons:

1. They'd be a giant pain to keep track of.
2. Templates and/or views would be polluted with alot of crufty if/else statements.
3. The site needed to launch with support for English and Spanish but I figured new languages would be added down the road and wanted to make any future additions as smooth as possible.

### Available Fields ###

`django-multilingualfield` contains two fields ready-for-use in your django project.

1. `multilingualfield.fields.MultiLingualCharField`: Functionality mirrors that of django's `django.db.models.CharField`
2. `multilingualfield.fields.MultiLingualTextField`: Functionality mirrors that of django's `django.db.models.TextField`

At the database level, `MultiLingualCharField` and `MultiLingualTextField` are essentially identical in that their content is both stored within 'text' columns (as opposed to either 'varchar' or 'text'); they diverge only in the widgets they use.

Any options you would can pass to a `CharField` or `TextField` (i.e. blank=True, max_length=50) will work as expected but `max_length` will not be enforced at a database level (only during form creation and input validation).

## Usage ##

### Settings ###

To use `django-multilingualfield`, first make sure that [LANGUAGES](https://docs.djangoproject.com/en/dev/ref/settings/#languages) is properly defined in your settings file.

> #### NOTE ####
> NOTE: django-multilingualfield uses `[django.utils.translation.get_language](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.translation.get_language)` to determine which translation to serve by default.
> 
> If you don't have `LANGUAGE_CODE` set in your settings file it will default to 'en-us' (U.S. English). It is recommended you manually set `[LANGUAGE_CODE](https://docs.djangoproject.com/en/dev/ref/settings/#language-code)` (even if you will be choosing the default value of 'en-us') *IN ADDITION TO* adding an entry for that language code (as the _first_ language) in `[LANGUAGES](https://docs.djangoproject.com/en/dev/ref/settings/#languages)`. Here's an example:

```python
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Espa&#241;ol') # See note belo note
]
```
 > ##### NOTE #####
 > `&#241;` is the UTF8 encoding for 'ñ'

### Examples ###

#### Model Example ####

Use `MultiLingualCharField` and `MultiLingualTextField` just like you would any django field:

```python
from django.db import models

from multilingualfield.fields import (
    MultiLingualCharField,
    MultiLingualTextField
)

class TestModel(models.Model):
    title = MultiLingualCharField(max_length=180)
    short_description = MultiLingualCharField(max_length=300)
    long_description = MultiLingualTextField(blank=True, null=True)
```

`django-multilingualfield` is fully integrated with [south](http://south.aeracode.org/) so migrate to your heart's content!

##### What's Stored In The Database #####

If `LANGUAGES` is set in your project's settings file like this...

```python
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Espa&#241;ol')
]
```

...then `django-multilingualfield` will store translations for a piece of text in a single 'text' db column as XML in the following structure:

```xml
<?xml version='1.0'?>
<languages>
    <language code="en">
        Hello
    </language>
    <language code="es">
        Hola
    </language>
</languages>
```
##### What's Served By The Application #####

Even though `MultiLingualCharField` and `MultiLingualTextField` instances are stored in the database as XML they are served to the application as a python object. The above block of XML would return an instance of `multilingualfield.fields.MultiLingualText` with two attributes `en` (with a value of `u'Hello'`) and `es` (with a value of `u'Hola'`). The translation corresponding to the current language of the active thread (as determined by calling `[django.utils.translation.get_language()](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.translation.get_language)`) will be returned by directly accessing the attribute.

##### Creating Instances in the Shell #####

Let's create an instance of our above example model (`TestModel`) in the python shell:

```bash
$ python manage.py shell
```

```python
>>> from someapp.models import TestModel
>>> from multilingualfield.fields import MultiLingualText
>>> x = TestModel()
>>> x.title = MultiLingualText()
>>> x.title.en = 'Hello'
>>> x.title.es = 'Hola'
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

##### Creating Instances in the Admin #####

Both `MultiLingualCharField` and `MultiLingualTextField` are admin-ready and will provide either a `TextInput` (for `MultiLingualCharField` instances) or `Textarea` (for `MultiLingualTextField` instances) field for each language listed in `settings.LANGUAGES`.

#### Template Usage ####

Template usage is SUPER straight forward.

If you have `'django.middleware.locale.LocaleMiddleware'` added to your `[MIDDLEWARE_CLASSES](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MIDDLEWARE_CLASSES)` setting and `'django.core.context_processors.i18n'` added to your `[TEMPLATE_CONTEXT_PROCESSORS](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATE_CONTEXT_PROCESSORS)` setting then `MultiLingualCharField` and `MultiLingualTextField` instances will automatically serve the correct language (based on the current user's language preference) by directly accessing their attributes.

> ##### NOTE #####
> To better understand how Django determines language preference read the aptly titled ['How Django discovers language preference'](https://docs.djangoproject.com/en/dev/topics/i18n/translation/#how-django-discovers-language-preference) section from the i18n topic page within the official Django documentation.
