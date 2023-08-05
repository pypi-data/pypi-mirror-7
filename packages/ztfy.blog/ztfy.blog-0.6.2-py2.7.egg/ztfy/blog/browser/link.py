### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.language.switch.interfaces import II18n
from zope.intid.interfaces import IIntIds
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.interfaces.link import ILinkContainer, ILinkContainerTarget
from ztfy.blog.interfaces.link import IBaseLinkInfo, IInternalLink, IInternalLinkInfo, IExternalLink, IExternalLinkInfo, ILinkFormatter
from ztfy.skin.interfaces import IDefaultView
from ztfy.skin.interfaces.container import IContainerBaseView
from ztfy.skin.interfaces.container import IStatusColumn, IActionsColumn
from ztfy.skin.interfaces.container import IContainerTableViewStatusCell, IContainerTableViewActionsCell
from ztfy.skin.layer import IZTFYBrowserLayer, IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.formjs import ajax
from z3c.template.template import getLayoutTemplate
from zope.component import adapts, getUtility, queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing import namespace
from zope.traversing.api import getParent as getParentAPI, getName
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.blog.browser import ztfy_blog_back
from ztfy.blog.link import InternalLink, ExternalLink
from ztfy.i18n.browser import ztfy_i18n
from ztfy.jqueryui import jquery_multiselect
from ztfy.skin.container import OrderedContainerBaseView
from ztfy.skin.content import BaseContentDefaultBackViewAdapter
from ztfy.skin.form import DialogAddForm, DialogEditForm
from ztfy.skin.menu import MenuItem, DialogMenuItem
from ztfy.utils.container import getContentName
from ztfy.utils.text import textToHTML
from ztfy.utils.traversing import getParent

from ztfy.blog import _


class LinkDefaultViewAdapter(BaseContentDefaultBackViewAdapter):

    adapts(IBaseLinkInfo, IZTFYBackLayer, Interface)

    def getAbsoluteURL(self):
        return '''javascript:$.ZTFY.dialog.open('%s/%s')''' % (absoluteURL(self.context, self.request), self.viewname)


class LinkContainerNamespaceTraverser(namespace.view):
    """++static++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, ILinkContainerTarget)
        if result is not None:
            return ILinkContainer(result)
        raise TraversalError('++links++')


class ILinkAddFormMenuTarget(Interface):
    """Marker interface for link add menu"""


class LinkContainerContentsViewMenuItem(MenuItem):
    """Links container contents menu"""

    title = _("Links")

    def render(self):
        jquery_multiselect.need()
        ztfy_blog_back.need()
        return super(LinkContainerContentsViewMenuItem, self).render()


class ILinkContainerContentsView(Interface):
    """Marker interface for links container contents view"""

class LinkContainerContentsView(OrderedContainerBaseView):
    """Links container contents view"""

    implements(ILinkAddFormMenuTarget, ILinkContainerContentsView)

    legend = _("Topic links")
    cssClasses = { 'table': 'orderable' }

    def __init__(self, *args, **kw):
        super(LinkContainerContentsView, self).__init__(*args, **kw)

    @property
    def values(self):
        return ILinkContainer(self.context).values()

    @ajax.handler
    def ajaxRemove(self):
        oid = self.request.form.get('id')
        if oid:
            intids = getUtility(IIntIds)
            target = intids.getObject(int(oid))
            parent = getParentAPI(target)
            del parent[getName(target)]
            return "OK"
        return "NOK"

    @ajax.handler
    def ajaxUpdateOrder(self):
        self.updateOrder(ILinkContainer(self.context))


class LinkContainerTableViewCellStatus(object):

    adapts(IBaseLinkInfo, IZTFYBrowserLayer, IContainerBaseView, IStatusColumn)
    implements(IContainerTableViewStatusCell)

    def __init__(self, context, request, view, table):
        self.context = context
        self.request = request
        self.view = view
        self.table = table

    @property
    def content(self):
        info = IInternalLinkInfo(self.context, None)
        if info is not None:
            adapter = queryMultiAdapter((info.target, self.request, self.view, self.table), IContainerTableViewStatusCell)
            if adapter is not None:
                return adapter.content
        return ''


class LinkContainerContentsViewActionsColumnCellAdapter(object):

    adapts(IBaseLinkInfo, IZTFYBrowserLayer, ILinkContainerContentsView, IActionsColumn)
    implements(IContainerTableViewActionsCell)

    def __init__(self, context, request, view, column):
        self.context = context
        self.request = request
        self.view = view
        self.column = column
        self.intids = getUtility(IIntIds)

    @property
    def content(self):
        klass = "workflow icon icon-trash"
        result = '''<span class="%s" title="%s" onclick="$.ZTFY.form.remove(%d, this);"></span>''' % (klass,
                                                                                                      translate(_("Delete link"), context=self.request),
                                                                                                      self.intids.register(self.context))
        return result


class BaseLinkAddForm(DialogAddForm):
    """Base link add form"""

    layout = getLayoutTemplate()
    parent_interface = ILinkContainerTarget
    parent_view = LinkContainerContentsView

    @ajax.handler
    def ajaxCreate(self):
        return super(BaseLinkAddForm, self).ajaxCreate(self)

    def add(self, link):
        title = II18n(link).queryAttribute('title', request=self.request)
        if not title:
            title = translate(_("Untitled link"), context=self.request)
        name = getContentName(self.context, title)
        self.context[name] = link


class InternalLinkAddForm(BaseLinkAddForm):
    """Internal link add form"""

    legend = _("Adding new internal link")

    fields = field.Fields(IInternalLinkInfo).omit('target')
    resources = (ztfy_i18n,)

    def create(self, data):
        result = InternalLink()
        result.title = data.get('title', {})
        return result


class LinkContainerAddInternalLinkMenuItem(DialogMenuItem):
    """Internal link add menu"""

    title = _(":: Add internal link...")

    target = InternalLinkAddForm


class ExternalLinkAddForm(BaseLinkAddForm):
    """External link add form"""

    legend = _("Adding new external link")

    fields = field.Fields(IExternalLinkInfo)
    resources = (ztfy_i18n,)

    def create(self, data):
        result = ExternalLink()
        result.title = data.get('title', {})
        return result


class LinkContainerAddExternalLinkMenuItem(DialogMenuItem):
    """External link add menu"""

    title = _(":: Add external link...")

    target = ExternalLinkAddForm


class BaseLinkEditForm(DialogEditForm):
    """Base link edit form"""

    legend = _("Edit link properties")

    layout = getLayoutTemplate()
    parent_interface = ILinkContainerTarget
    parent_view = LinkContainerContentsView

    @ajax.handler
    def ajaxEdit(self):
        return super(BaseLinkEditForm, self).ajaxEdit(self)


class InternalLinkEditForm(BaseLinkEditForm):
    """Internal link edit form"""

    fields = field.Fields(IInternalLinkInfo).omit('target')


class ExternalLinkEditForm(BaseLinkEditForm):
    """External link edit form"""

    fields = field.Fields(IExternalLinkInfo)


class InternalLinkFormatter(object):
    """Internal link default view"""

    adapts(IInternalLink, IZTFYBrowserLayer, Interface)
    implements(ILinkFormatter)

    def __init__(self, link, request, view):
        self.link = link
        self.request = request
        self.view = view

    def render(self):
        target = self.link.target
        adapter = queryMultiAdapter((self.link, self.request, self.view), IDefaultView)
        if adapter is not None:
            url = adapter.absoluteURL()
        else:
            url = absoluteURL(target, self.request)
        title = II18n(self.link).queryAttribute('title', request=self.request) or \
                II18n(target).queryAttribute('title', request=self.request)
        desc = II18n(self.link).queryAttribute('description', request=self.request) or \
               II18n(target).queryAttribute('description', request=self.request)
        result = ''
        if self.link.language:
            result += '''<img src="/--static--/ztfy.i18n/img/flags/%s.png" alt="" />''' % self.link.language.replace('-', '_', 1)
        result += '''<a href="%s">%s</a>''' % (url, title)
        if desc:
            result += '''<div class="desc">%s</div>''' % textToHTML(desc, request=self.request)
        return '''<div class="link link-internal">%s</link>''' % result


class ExternalLinkFormatter(object):
    """External link default view"""

    adapts(IExternalLink, IZTFYBrowserLayer, Interface)
    implements(ILinkFormatter)

    def __init__(self, link, request, view):
        self.link = link
        self.request = request
        self.view = view

    def render(self):
        title = II18n(self.link).queryAttribute('title', request=self.request)
        desc = II18n(self.link).queryAttribute('description', request=self.request)
        result = ''
        if self.link.language:
            result += '''<img src="/--static--/ztfy.i18n/img/flags/%s.png" alt="" />''' % self.link.language.replace('-', '_', 1)
        result += '''<a href="%s">%s</a>''' % (self.link.url, title)
        if desc:
            result += '''<div class="desc">%s</div>''' % textToHTML(desc, request=self.request)
        return '''<div class="link link-external">%s</link>''' % result
