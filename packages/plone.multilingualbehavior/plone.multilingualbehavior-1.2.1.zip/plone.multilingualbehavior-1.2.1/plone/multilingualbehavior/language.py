from zope import interface

from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.multilingual.interfaces import ILanguage
from plone.app.dexterity.behaviors.metadata import ICategorization


# Patch for hiding 'language' field from the edit form
ICategorization['language'].readonly = True


class Language(object):

    def __init__(self, context):
        self.context = context

    interface.implements(ILanguage)

    def get_language(self):
        language = self.context.language
        if not language:
            language = LANGUAGE_INDEPENDENT
        return language

    def set_language(self, language):
        self.context.language = language
