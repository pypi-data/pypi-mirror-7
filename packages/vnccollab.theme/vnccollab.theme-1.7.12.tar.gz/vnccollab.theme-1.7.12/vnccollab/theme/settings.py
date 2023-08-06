from zope import schema
from zope.interface import Interface
from zope.component import getUtility, provideAdapter

from plone import api
from plone.registry.interfaces import IRegistry
from plone.app.registry.browser import controlpanel
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form, button, datamanager
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from vnccollab.theme import messageFactory as _


provideAdapter(datamanager.DictionaryField)


class IWorldClockSettings(Interface):

    tz_1 = schema.Choice(
        title=_(u"Clock 1 Timezone"),
        description=u'',
        required=True,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='Europe/Berlin')

    skin_1 = schema.Choice(
        title=_(u"Clock 1 Skin"),
        description=u'',
        required=True,
        values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
                'vncHeaderViewlet'),
        default='vncHeaderViewlet')

    radius_1 = schema.Int(
        title=_(u"Clock 1 Radius"),
        description=u'',
        required=True,
        default=35)

    no_seconds_1 = schema.Bool(
        title=_(u"Clock 1 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)

    tz_2 = schema.Choice(
        title=_(u"Clock 2 Timezone"),
        description=u'',
        required=False,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='Asia/Mumbai')

    skin_2 = schema.Choice(
        title=_(u"Clock 2 Skin"),
        description=u'',
        required=True,
        values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
                'vncHeaderViewlet'),
        default='vncHeaderViewlet')

    radius_2 = schema.Int(
        title=_(u"Clock 2 Radius"),
        description=u'',
        required=False,
        default=35)

    no_seconds_2 = schema.Bool(
        title=_(u"Clock 2 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)

    tz_3 = schema.Choice(
        title=_(u"Clock 3 Timezone"),
        description=u'',
        required=False,
        vocabulary='vnccollab.theme.vocabularies.TimeZonesVocabulary',
        default='America/New_York')

    skin_3 = schema.Choice(
        title=_(u"Clock 3 Skin"),
        description=u'',
        required=True,
        values=('chunkySwiss', 'chunkySwissOnBlack', 'swissRail', 'vnc',
                'vncHeaderViewlet'),
        default='vncHeaderViewlet')

    radius_3 = schema.Int(
        title=_(u"Clock 3 Radius"),
        description=u'',
        required=False,
        default=35)

    no_seconds_3 = schema.Bool(
        title=_(u"Clock 3 Without Seconds"),
        description=_(u"Do not show seconds handle."),
        required=False,
        default=False)


class WorldClockSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IWorldClockSettings
    label = _(u'WorldClock Settings')
    description = _(u'')

    def updateFields(self):
        super(WorldClockSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(WorldClockSettingsEditForm, self).updateWidgets()


class WorldClockSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = WorldClockSettingsEditForm


class IAnonymousHomepageSettings(Interface):
    """Anonymous Homepage Settings."""
    help_url = schema.URI(
        title=_(u'Help URL'),
        description=_(u'URL of the page that shows the site help.'),
        required=False,
    )

    show_register_url = schema.Bool(
        title=_(u'Show Register'),
        description=_(u'Should Register/Sing Up be shown'),
        required=False,
        default=True
    )

    register_url = schema.URI(
        title=_(u'Register URL'),
        description=_(u'URL of the page for Registration / Signup page (empty for default).'),
        required=False,
    )

    show_login_url = schema.Bool(
        title=_(u'Show Login'),
        description=_(u'Should Login link be shown'),
        required=False,
        default=True
    )

    login_url = schema.URI(
        title=_(u'Login URL'),
        description=_(u'URL of the login page (empty for default).'),
        required=False,
    )


class IAnonymousHomepageForm(IAnonymousHomepageSettings):
    """Anonymous Homepage Form."""
    logo = schema.Bytes(
        title=_(u'Homepage Logo'),
        description=_(u'Upload an image to set or replace the site logo'),
        required=False,
    )

    delete_logo = schema.Bool(
        title=_(u"Delete Logo"),
        description=_(u"Delete the customized logo."),
        required=False,
        default=False)


class AnonymousHomepageSettingsEditForm(AutoExtensibleForm, form.EditForm):
    schema = IAnonymousHomepageForm
    label = u'Anonymous Homepage Settings'
    description = _(u"""""")

    # Internal fields: not to be configured.
    control_panel_view = "plone_control_panel"
    registry_key_base = 'vnccollab.theme.settings.IAnonymousHomepageSettings'
    help_url_key = '{0}.help_url'.format(registry_key_base)
    show_register_url_key = '{0}.show_register_url'.format(registry_key_base)
    register_url_key = '{0}.register_url'.format(registry_key_base)
    show_login_url_key = '{0}.show_login_url'.format(registry_key_base)
    login_url_key = '{0}.login_url'.format(registry_key_base)

    def getContent(self):
        registry = getUtility(IRegistry)
        help_url = registry.get(self.help_url_key, '')
        show_register_url = registry.get(self.show_register_url_key, True)
        register_url = registry.get(self.register_url_key, '')
        show_login_url = registry.get(self.show_login_url_key, True)
        login_url = registry.get(self.login_url_key, '')
        return {'help_url': help_url,
                'show_register_url': show_register_url,
                'register_url': register_url,
                'show_login_url': show_login_url,
                'login_url': login_url,
                }

    def applyChanges(self, data):
        registry = getUtility(IRegistry)
        help_url = data.get('help_url', None)
        show_register_url = data.get('show_register_url', True)
        register_url = data.get('register_url', None)
        show_login_url = data.get('show_login_url', True)
        login_url = data.get('login_url', None)
        delete_logo = data['delete_logo']
        logo = data['logo']

        registry[self.help_url_key] = help_url
        registry[self.show_register_url_key] = show_register_url
        registry[self.register_url_key] = register_url
        registry[self.show_login_url_key] = show_login_url
        registry[self.login_url_key] = login_url

        portal = api.portal.get()
        custom_skin = portal.portal_skins.custom
        destination = custom_skin

        if delete_logo or logo:
            current_logo = api.content.get(
                path='/portal_skins/custom/logo.png')
            if current_logo:
                # logo.png could be not defined in ZODB, so current_logo
                # could be not None and not deleteable
                try:
                    api.content.delete(current_logo)
                except:
                    pass

        if logo:
            destination.manage_addProduct['OFSP'].manage_addImage('logo.png',
                                                                  logo)

    def updateActions(self):
        super(AutoExtensibleForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled."),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    @button.buttonAndHandler(_(u'Edit Home Page'), name='edit')
    def handleEdit(self, action):
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
            '@@manage-group-dashboard?key=AnonymousUsers'))

    @button.buttonAndHandler(_(u'Edit Carousel'), name='carousel')
    def handleCarousel(self, action):
        portal = api.portal.get()
        self.request.response.redirect("%s/%s" % (portal.absolute_url(),
            '@@edit-carousel'))


class AnonymousHomepageSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    index = ViewPageTemplateFile('browser/templates/anonhomepage_controlpanel_layout.pt')
    form = AnonymousHomepageSettingsEditForm

