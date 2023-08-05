from Acquisition import aq_parent
from esdrt.content import MessageFactory as _
from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import field
from z3c.form import group
from zope import schema


# Interface class; used to define content-type schema.
class IESDRTFile(form.Schema, IImageScaleTraversable):
    """
    Files with special needs
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
        )

    form.primary('file')
    file = NamedBlobFile(
        title=_(u'File'),
        required=True,
    )

    confidential = schema.Bool(
        title=_(u'Is a confidential file?'),
        description=_(u'Confidential files are only available for people '
                      u'taking part in the review process')
    )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class ESDRTFile(dexterity.Item):
    grok.implements(IESDRTFile)
    # Add your class methods and properties here


class AddForm(dexterity.AddForm):
    grok.name('esdrt.content.esdrtfile')
    grok.context(IESDRTFile)
    grok.require('esdrt.content.AddESDRTFile')

    def update(self):
        super(AddForm, self).update()
        status = IStatusMessage(self.request)
        msg = _(u'To guarantee the full confidentiality of confidential files '
                u'we suggest you to zip your file, protect it with password '
                u'and send the password using other means'
            )
        status.add(msg, type='info')

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(IESDRTFile).omit('title')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']




# View class
# The view will automatically use a similarly named template in
# templates called esdrtfileview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class ESDRTFileView(grok.View):
    grok.context(IESDRTFile)
    grok.require('zope2.View')
    grok.name('view')

    def render(self):
        url = aq_parent(self.context).absolute_url()
        return self.response.redirect(url)