import simplejson

from Acquisition import aq_inner, aq_parent
from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from AccessControl import getSecurityManager

from zope.event import notify
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import shasattr
from Products.Archetypes.utils import make_uuid
from Products.Archetypes.event import ObjectInitializedEvent
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.layout.viewlets.interfaces import IPortalTop
from plone.app.viewletmanager.manager import BaseOrderedViewletManager

from vnccollab.theme import messageFactory as _
from vnccollab.theme.config import PORTLETS_STATES_ANNO_KEY
from vnccollab.theme.browser.viewlets import AddContentAreaViewlet


class VNCCollabUtilView(BrowserView):
    """Utility views to call from templates"""
    
    def listFolderContentTypes(self):
        """Returns list of content types used inside
        current container.
        """
        items = []
            
        # calculate current folder's path
        cstate = getMultiAdapter((self.context, self.request),
            name='plone_context_state')
        path = '/'.join(cstate.folder().getPhysicalPath())
        
        # collect portal type list used withing current folder
        otypes = []
        catalog = getToolByName(self.context, 'portal_catalog')
        for brain in catalog(path={'query': path, 'depth': 1}):
            if brain.portal_type not in otypes:
                otypes.append(brain.portal_type)
        
        # prepare items list with type id and type title
        ttool = getToolByName(self.context, 'portal_types')
        for otype in otypes:
            item = {'id': otype, 'title': otype}
            if ttool is not None and shasattr(ttool, otype):
                item['title'] = _(safe_unicode(getattr(ttool, otype).Title()))
            items.append(item)
        
        # finally sort items and prepend 'All' filter element
        if len(items) > 0:
            items.sort(lambda x,y:cmp(x['title'], y['title']))
            items = [{'id': '', 'title': _(u'All')}] + items
        
        return tuple(items)

    def recordPortletState(self, hash, action, value):
        """Sets portlet state on site annotations"""
        # check if we got anthenticated user
        user = getSecurityManager().getUser()
        if not user or getattr(user, 'name', '') == 'Anonymous User':
            return _(u"No authenticated user found.")
        
        annotations = IAnnotations(self.context)
        users = annotations.get(PORTLETS_STATES_ANNO_KEY, None)
        if users is None:
            users = annotations[PORTLETS_STATES_ANNO_KEY] = OOBTree()
        
        userid = getattr(user, '_id', user.getId())
        portlets = users.get(userid, None)
        if portlets is None:
            portlets = users[userid] = PersistentDict()
        
        portlet = portlets.get(hash, None)
        if portlet is None:
            portlet = portlets[hash] = PersistentDict()
        
        portlet[action] = value
        
        return 'Done.'

    def searchContainersJSON(self, term=None, limit='20'):
        """Queries all contains in the site for a given term and returns
        json list of found containers.
        """
        limit = int(limit)
        if not term:
            return simplejson.dumps([])

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        # prepare search query
        for char in ('?', '-', '+', '*', u'\u3000'.encode('utf-8')):
            term = term.replace(char, ' ')
        r = " AND ".join(term.split())
        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, '"%s"' % char)
            return s
        r = quote_bad_chars(r) + '*'

        data = []
        parents = {}
        for brain in catalog(SearchableText=r, is_folderish=True,
            sort_on='sortable_title', sort_limit=limit)[:limit]:
            parent = parents.get(brain.UID)
            if not parent:
                parent = parents[brain.UID] = \
                    aq_parent(aq_inner(brain.getObject()))
            
            ptitle = ''
            if parent:
                ptitle = getattr(parent, 'Title', lambda:'')()
                if ptitle:
                    ptitle = ' (%s)' % ptitle
            
            data.append({
                'value': brain.UID,
                'label': '%s%s' % (brain.Title, ptitle),
                'desc': brain.Description})
        
        return simplejson.dumps(data)

    def renderAddContentAreaViewlet(self, uid):
        """Renders add content area viewlet for object with given uid"""
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(UID=uid)
        if len(brains) == 0:
            return ''

        obj = brains[0].getObject()
        manager = BaseOrderedViewletManager()
        alsoProvides(manager, IPortalTop)
        viewlet = getMultiAdapter((obj, self.request, self, manager),
            IViewlet, name='vnccollab.theme.addcontentarea')
        viewlet = viewlet.__of__(obj)
        viewlet.update()
        return viewlet.render()

    def uploadFile(self, file):
        """Form post handler to create file.
        
        If created successfully then redirect to it's Edit form,
        otherwise to it's Add form with validation errors.
        
        Parameter:
          @file - data to upload
        File title is taken from file as filename.
        """
        # check it's post request
        if self.request.method != 'POST' or not file or not file.filename:
            raise Exception(u'Invalid request.')
        
        context = aq_inner(self.context)
        id = make_uuid('temp-id')
        # make sure our id is unique
        id = context.invokeFactory(id=id, type_name='File')
        obj = getattr(context, id)
        obj.update(title=file.filename, file=file)
        obj._renameAfterCreation()
        if obj.checkCreationFlag():
            obj.unmarkCreationFlag()
        obj._renameAfterCreation()
        obj.reindexObject()
        notify(ObjectInitializedEvent(obj))
        
        # if file is not there then it haven't got over validation process,
        # notify user about this issue
        if not obj.get_size():
            IStatusMessage(self.request).addStatusMessage(_(u"Attached file is "
                "invalid, please, try to upload another one."), type="error")
        
        # if posted by javascript then no redirect
        if self.request.form.get('ajax_call'):
            return '%s/edit' % obj.absolute_url()
        else:
            return self.request.response.redirect('%s/edit' %
                obj.absolute_url())

    def isPopupModeOn(self):
        """Returns whether popup mode is enabled"""
        return self.request.get('popup_mode') == '1'
