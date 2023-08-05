# -*- coding: utf-8 -*-

from zope.interface import implements

from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IValue

from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base

from interfaces import ILanguageIndependentField
from plone.multilingual.manager import TranslationManager


def isLanguageIndependent(field):
    if field.interface is None:
        return False

    if ILanguageIndependentField.providedBy(field):
        return True
    else:
        return False


class ValueBase(object):
    implements(IValue)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.field = field
        self.form = form
        self.widget = widget

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')


class AddingLanguageIndependentValue(ValueBase):
    def getTranslationUuid(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if 'tg' in session.keys():
            return session['tg']

    def get(self):
        uuid = self.getTranslationUuid()

        if isLanguageIndependent(self.field) and uuid:
            manager = TranslationManager(uuid)
            result = manager.get_restricted_translations()

            if len(result) >= 1:

                orig_lang = result.keys()[0]
                obj = result[orig_lang]
                name = self.field.__name__
                try:
                    value = getattr(aq_base(obj), name)
                except AttributeError:
                    pass
                else:
                    return value

        if self.field.default is None:
            return NO_VALUE

        return self.field.default

