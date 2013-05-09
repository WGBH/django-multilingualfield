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

django has [excellent built-in auto-translation tools](https://docs.djangoproject.com/en/dev/topics/i18n/translation/) but a recent project at WGBH necessitated providing manually written translations for nearly all text content served by the site.

I didn't want to create multiple `CharField` or `TextField` attributes for each piece of text (i.e. 'title_en' and 'title_es') for multiple reasons:

1. They'd be a giant pain to keep track of.
2. Templates and/or views would be polluted with alot of unnecessary if/else statements.
3. The site needed to launch with support for English and Spanish but wanted to make the transition as smooth as possible if/when the day came that another language was added to the site.

### Available Fields ###

`django-multilingualfield` contains two fields ready-for-use in your django project.

1. `multilingualfield.fields.MultiLingualCharField`: Functionality mirrors that of django's `django.db.models.CharField`
2. `multilingualfield.fields.MultiLingualTextField`: Functionality mirrors that of django's `django.db.models.TextField`

At the database level, `MultiLingualCharField` and `MultiLingualTextField` are essentially identical in that their content is both stored within 'text' columns (as opposed to either 'text' or 'varchar'). They diverge only in the widgets they use.

Any options you would can pass to a `CharField` or `TextField` (i.e. blank=True, max_length=50) will work as expected but `max_length` will not be enforced at a database level (only during form creation and input validation).

## Usage ##

### Settings ###

To use `django-multilingualfield`, first make sure that `LANGUAGES` is set in your settings file ([`LANGUAGES` setting documentation](https://docs.djangoproject.com/en/dev/ref/settings/#languages)).

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

If value of `LANGUAGES` in your project's settings file is...

```python
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish')
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

Even though `MultiLingualCharField` and `MultiLingualTextField` instances are stored in the database as XML they are served by the application as a python object. The above block of XML would return an instance of `multilingualfield.fields.MultiLingualText` with two attributes `en` (with a value of `u'Hello'`) and `es` (with a value of `u'Hola'`). Also, since 'English' is at the top of `settings.LANGUAGES` it is considered the 'default' language and it's value will be returned by directly accessing the attribute.

##### Creating Instances in the Shell #####

Let's create an instance of `TestModel` in the shell:

```python
>>> from someapp.models import TestModel
>>> from multilingualfield.fields import MultiLingualText
>>> x = TestModel()
>>> x_title = MultiLingualText()
>>> x_title.en = 'Hello'
>>> x_title.es = 'Hola'
>>> x.title = x_title
>>> x.save()
>>> x.title.en
u'Hello'
>>> x.title.es
u'Hola'
>>> x.title
u'Hello'
```

##### Creating Instances in the Admin #####

Both `MultiLingualCharField` and `MultiLingualTextField` are admin-ready and will create either a `TextInput` or `Textarea` field for each language listed in `settings.LANGUAGES`.

#### Template Example ####

`django-multilingualfield` provides a simple templatetag 'get_for_current_language' that will pull the correct translation based on user's language (as provided by the global context value 'LANGUAGE_CODE')

To use it, first make sure you have 'multilingualfield' added to `settings.INSTALLED_APPS`

Then load it onto the template you want to use by including the following tag towards the top of your template file:

```html
{% load multilingual_tags %}
```

It can be used as either a standalone tag:

```html
<h1>{% get_for_current_language object.title %}</h1>
```

Or assigned to a context variable with as:

```html
{% get_for_current_language object.title as the_title %}
<h1>{{ the_title }}</h1>
```