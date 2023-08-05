try:
    from plone.schemaeditor.interfaces import IFieldEditorExtender
    HAVE_EDITOREXTENDER = True
except ImportError:
    HAVE_EDITOREXTENDER = False

if HAVE_EDITOREXTENDER:

    from zope.interface import implements, Interface, alsoProvides, \
        noLongerProvides
    from zope import schema
    from zope.schema import interfaces
    from zope.component import adapts, provideAdapter, adapter

    from zope.schema.interfaces import IField
    from plone.schemaeditor.interfaces import ISchemaContext

    #from plone.schemaeditor.interfaces import IBehaviorExtensionFields
    from plone.multilingualbehavior.interfaces import ILanguageIndependentField
    from zope.i18nmessageid import MessageFactory

    PMF = MessageFactory('plone.multilingualbehavior')

    class IFieldLanguageIndependent(Interface):
        languageindependent = schema.Bool(
            title=PMF(u'Language independent field'),
            description=PMF(u'The field is going to be copied on all '
                            u'translations when you edit the content'),
            required=False)

    class FieldLanguageIndependentAdapter(object):
        implements(IFieldLanguageIndependent)
        adapts(interfaces.IField)

        def __init__(self, field):
            self.field = field

        def _read_languageindependent(self):
            return ILanguageIndependentField.providedBy(self.field)

        def _write_languageindependent(self, value):
            if value:
                alsoProvides(self.field, ILanguageIndependentField)
            else:
                noLongerProvides(self.field, ILanguageIndependentField)
        languageindependent = property(_read_languageindependent,
                                       _write_languageindependent)

    # IFieldLanguageIndependent could be registered directly as a named adapter
    # providing IFieldEditorExtender for ISchemaContext and IField. But we can
    # also register a separate callable which returns the schema only if
    # additional conditions pass:
    @adapter(ISchemaContext, IField)
    def get_li_schema(schema_context, field):
        if 'plone.multilingualbehavior.interfaces.IDexterityTranslatable' \
           in schema_context.fti.behaviors:
            return IFieldLanguageIndependent

    # Register the callable which makes the field edit form know about the
    # new schema:
    provideAdapter(get_li_schema,
                   provides=IFieldEditorExtender,
                   name='plone.schemaeditor.languageindependent')

    # And the adapter for getting/setting the value.
    provideAdapter(FieldLanguageIndependentAdapter,
                   provides=IFieldLanguageIndependent)
