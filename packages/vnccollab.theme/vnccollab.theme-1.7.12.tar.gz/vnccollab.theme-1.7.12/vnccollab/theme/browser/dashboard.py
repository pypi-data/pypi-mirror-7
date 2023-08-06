from zope.component import getUtility

from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName


class DashboardView(BrowserView):
    """User's Dashboard.

    Lists user's group assigned portlets.
    """

    @memoize
    def empty(self):
        dashboards = [getUtility(IPortletManager, name=name)
                      for name in ['plone.dashboard1',
                                   'plone.dashboard2',
                                   'plone.dashboard3',
                                   'plone.dashboard4']]

        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        userid = member.getId()

        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard.get(USER_CATEGORY, {})
                                         .get(userid, {}))
            for groupid in member.getGroups():
                num_portlets += len(dashboard.get(GROUP_CATEGORY, {})
                                             .get(groupid, {}))
        return num_portlets == 0
