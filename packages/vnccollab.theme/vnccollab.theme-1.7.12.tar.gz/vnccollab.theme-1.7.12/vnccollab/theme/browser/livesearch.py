from DateTime import DateTime

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote_plus
from Products.PythonScripts.standard import html_quote
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.Five import BrowserView

from vnccollab.common.livesearch import query

class LiveSearchReplyView(BrowserView):
    def result(self):
        context = self.context
        request = self.request
        response = self.request.response
        q = request.get('q')
        limit = int(request.get('limit', 10))
        path = request.get('path', None)

        ploneUtils = getToolByName(context, 'plone_utils')
        portal_url = getToolByName(context, 'portal_url')()
        pretty_title_or_id = ploneUtils.pretty_title_or_id

        portalProperties = getToolByName(context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        # SIMPLE CONFIGURATION
        MAX_TITLE = 29
        MAX_DESCRIPTION = 93

        mtool = getToolByName(context, 'portal_membership')

        friendly_types = ploneUtils.getUserFriendlyTypes()

        def quotestring(s):
            return '"%s"' % s

        def quote_bad_chars(s):
            bad_chars = ["(", ")"]
            for char in bad_chars:
                s = s.replace(char, quotestring(char))
            return s

        def pretty_date(when):
            result = ('%s %s, %s') % (DateTime(when).strftime('%B'), DateTime(when).strftime('%d'), DateTime(when).strftime('%Y'))
            return result

        multispace = u'\u3000'.encode('utf-8')
        for char in ('?', '-', '+', '*', multispace):
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_bad_chars(r) + '*'
        searchterms = url_quote_plus(r)

        site_encoding = context.plone_utils.getSiteEncoding()

        params = {'SearchableText': r,
                  'portal_type': friendly_types,
                  'sort_limit': limit + 1}

        if path is None:
            # useful for subsides
            params['path'] = getNavigationRoot(context)
        else:
            params['path'] = path

        # search limit+1 results to know if limit is exceeded
        #params = get_query(searchable_text, params)
        #results = catalog(**params)
        results = query(params)

        searchterm_query = '?searchterm=%s' % url_quote_plus(q)

        #request = context.request
        #response = request.response
        response.setHeader('Content-Type', 'text/xml;charset=%s' % site_encoding)

        # replace named entities with their numbered counterparts, in the xml the named ones are not correct
        #   &darr;      --> &#8595;
        #   &hellip;    --> &#8230;
        legend_livesearch = _('legend_livesearch', default='LiveSearch &#8595;')
        label_no_results_found = _('label_no_results_found', default='No matching results found.')
        label_advanced_search = _('label_advanced_search', default='Advanced Search&#8230;')
        label_show_all = _('label_show_all', default='Show all items')

        ts = getToolByName(context, 'translation_service')

        output = []

        def write(s):
            output.append(safe_unicode(s))

        if not results:
            write('''<fieldset class="livesearchContainer">''')
            write('''<legend id="livesearchLegend">%s</legend>''' % ts.translate(legend_livesearch, context=request))
            write('''<div class="LSIEFix">''')
            write('''<div id="LSNothingFound">%s</div>''' % ts.translate(label_no_results_found, context=request))
            write('''<ul class="ls-foot">''')
            write('''<li class="LSRow lsrow-adv-search">''')
            write('<b></b><a href="%s" style="font-weight:normal">%s</a>' %
                 (portal_url + '/@@search',
                  ts.translate(label_advanced_search, context=request)))
            write('''</li>''')
            write('''</ul>''')
            write('''</div>''')
            write('''</fieldset>''')
        else:
            write('''<fieldset class="livesearchContainer">''')
            write('''<legend id="livesearchLegend">%s</legend>''' % ts.translate(legend_livesearch, context=request))
            write('''<div class="LSIEFix">''')
            write('''<ul class="LSTable">''')

            for result in results[:limit]:
                # breadcrumbs
                obj = result.getObject()
                breadcrumbs_view = getMultiAdapter((obj, request), name='breadcrumbs_view')
                breadcrumbs = breadcrumbs_view.breadcrumbs()

                ls_breadcrumb = ''

                breadcrumbs_size = len(breadcrumbs) - 1

                if breadcrumbs_size > 0:
                    for ls_key in breadcrumbs[:breadcrumbs_size]:
                        ls_breadcrumb += ('''<a href="%s">%s</a> > ''' % (ls_key['absolute_url'], ls_key['Title']))

                is_folderish = result.is_folderish

                if is_folderish:
                    length_size = len(obj)
                else:
                    length_size = result.getObjSize

                #icon = plone_view.getIcon(result)
                img_class = '%s-icon' % ploneUtils.normalizeString(result.portal_type)

                member = mtool.getMemberById(result.Creator)
                if member is not None:
                    fullname = member.getProperty('fullname')
                else:
                    fullname = ''

                itemUrl = result.getURL()
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                itemUrl = itemUrl + searchterm_query

                write('''<li class="LSRow">''')
                #write(icon.html_tag() or '')
                write('''<div class="%s ls-content-icon"></div>''' % (img_class))
                write('''<div class="ls-details">''')

                full_title = safe_unicode(pretty_title_or_id(result))
                if len(full_title) > MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE], '...'))
                else:
                    display_title = full_title

                full_title = full_title.replace('"', '&quot;')
                #klass = 'contenttype-%s' % ploneUtils.normalizeString(result.portal_type)
                klass = 'ls-content-title'
                write('''<a href="%s" title="%s" class="%s">%s</a>''' % (itemUrl, full_title, klass, display_title))
                display_description = safe_unicode(result.Description)
                if len(display_description) > MAX_DESCRIPTION:
                    display_description = ''.join((display_description[:MAX_DESCRIPTION], '...'))

                # need to quote it, to avoid injection of html containing javascript and other evil stuff
                display_description = html_quote(display_description)
                write('''<div class="LSDescr">%s</div>''' % (display_description))

                if breadcrumbs_size > 0:
                    write('''<div class="LSBreadcrumb">in %s</div>''' % (ls_breadcrumb[:-3]))
                else:
                    write('''<div class="LSBreadcrumb">in Home</div>''')

                write('''<div class="LSMeta">''')
                display_type = html_quote(safe_unicode(result.Type))
                write('''<span class="LSType">%s</span>''' % (display_type))

                if result.Type == 'File' or result.Type == 'Image':
                    write('''<span class="LSType"> &#8226; %s</span>''' % (length_size))
                elif result.Type == 'Folder':
                    write('''<span class="LSType"> &#8226; %s item(s)</span>''' % (length_size))

                display_creator = html_quote(safe_unicode(fullname))

                if len(display_creator) > 0:
                    write(''' &#8226; Create by <a href="%s/author/%s" class="LSCreator">%s</a>''' %
                        (portal_url, member.getProperty('id'), display_creator))

                display_modified = html_quote(safe_unicode((pretty_date(result.modified))))
                write('''<span class="LSModified">on %s</span>''' % (display_modified))
                write('''</div>''')
                write('''</div>''')
                write('''</li>''')

                full_title, display_title, display_description, display_type = None, None, None, None
            write('''</ul><ul class="ls-foot">''')
            if len(results) > limit:
                # add a more... row
                write('''<li class="LSRow lsrow-show-all">''')
                searchquery = '@@search?SearchableText=%s&path=%s' % (searchterms, params['path'])
                write('<b></b><a href="%s" style="font-weight:normal">%s</a>' % (
                                     searchquery,
                                     ts.translate(label_show_all, context=request)))
                write('''</li>''')

            write('''<li class="LSRow lsrow-adv-search">''')
            write('<b></b><a href="%s" style="font-weight:normal">%s</a>' %
                 (portal_url + '/@@search',
                  ts.translate(label_advanced_search, context=request)))
            write('''</li>''')
            write('''</ul>''')
            write('''</div>''')
            write('''</fieldset>''')

        return '\n'.join(output).encode(site_encoding)
