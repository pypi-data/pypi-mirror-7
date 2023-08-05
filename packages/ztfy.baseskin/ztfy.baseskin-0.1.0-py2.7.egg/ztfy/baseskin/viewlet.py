### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2014 Thierry Florac <tflorac AT ulthar.net>
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
from zope.contentprovider.interfaces import IContentProvider

# import local interfaces
from ztfy.baseskin.interfaces.form import IFormViewletsManager, IFormPrefixViewletsManager, \
    IWidgetsPrefixViewletsManager, IWidgetsSuffixViewletsManager, IFormSuffixViewletsManager

# import Zope3 packages
from z3c.template.template import getViewTemplate
from zope.component import adapts
from zope.interface import implements, Interface
from zope.viewlet.viewlet import ViewletBase as Viewlet
from zope.viewlet.manager import ViewletManagerBase as ViewletManager, WeightOrderedViewletManager

# import local packages
from ztfy.baseskin.layer import IBaseSkinLayer


class ViewletManagerBase(ViewletManager):
    """Template based viewlet manager class"""

    template = getViewTemplate()


class WeightViewletManagerBase(WeightOrderedViewletManager):
    """Template based weighted viewlet manager class"""

    template = getViewTemplate()


class ViewletBase(Viewlet):
    """Template based viewlet"""

    render = getViewTemplate()


class ContentProviderBase(object):
    """Generic template based content provider"""

    adapts(Interface, IBaseSkinLayer, Interface)
    implements(IContentProvider)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        pass

    render = getViewTemplate()


class FormViewletManager(WeightOrderedViewletManager):
    """Base form viewlet manager"""

    implements(IFormViewletsManager)


class FormPrefixViewletManager(FormViewletManager):
    """Form prefix viewlet manager, displayed before form"""

    implements(IFormPrefixViewletsManager)


class WidgetsPrefixViewletManager(FormViewletManager):
    """Form widgets prefix display manager, displayed before widgets"""

    implements(IWidgetsPrefixViewletsManager)


class WidgetsSuffixViewletManager(FormViewletManager):
    """Form widgets suffix viewlet manager, displayed after widgets"""

    implements(IWidgetsSuffixViewletsManager)


class FormSuffixViewletManager(FormViewletManager):
    """Form suffix viewlet manager, displayed after form"""

    implements(IFormSuffixViewletsManager)
