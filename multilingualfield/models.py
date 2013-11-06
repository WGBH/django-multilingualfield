from __future__ import absolute_import, division, print_function, unicode_literals

from . import fields, LANGUAGES


ARGUMENT = u'{0}__regex'
LANGUAGE_REGEX = u'.*<language code="{0}">[^<]+</language>.*'


class MultilingualFieldsMixin(object):
    u"""Add some utility methods related to the multilingual fields."""

    def is_translation_complete(self, language_code):
        u"""Return True if all multilingual fields of the object are not empty for the language ``language_code``."""
        for field in self.__class__.multilingual_fields():
            value = getattr(getattr(self, field.name), code)
            if value is None or len(value) == 0:
                return False
        return True

    @property
    def complete_translations(self):
        u"""
        Check the multilingual fields of the object and return a set with the languages that 'are' in all fields.

        .. todo:: a better explanation (a little bit tired today)
        """
        translations = set()
        for code, verbose in LANGUAGES:
            translations.add(code)
            for field in self.__class__.multilingual_fields():
                value = getattr(getattr(self, field.name), code)
                if value is None or len(value) == 0:
                    translations.discard(code)
                    break
        return translations

    @classmethod
    def multilingual_fields(cls):
        u"""Return a generator which returns the fields of the model that are instance of the multilingual fields."""
        mf1, mf2 = fields.MultiLingualTextField, fields.MultiLingualFileField
        return (f for f in cls._meta.fields if isinstance(f, mf1) or isinstance(f, mf2))

    @classmethod
    def objects_with_incomplete_translations(cls, language_code, fields_names=None, inverse=None):
        u"""
        Return a queryset filtering the objects that does not have all (or ``fields_names``) of his multilingual fields
        translated in ``language_code``.
        """
        if fields_names is None:
            fields_names = [f.name for f in cls.multilingual_fields()]
        language_regex = LANGUAGE_REGEX.format(language_code)
        arguments = {ARGUMENT.format(name): language_regex for name in fields_names}
        return cls.objects.filter(**arguments) if inverse else cls.objects.exclude(**arguments)
