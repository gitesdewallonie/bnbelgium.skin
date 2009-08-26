# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from zope.interface import Interface
from zope.component import adapts
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from bnbelgium.skin.browser.interfaces import IBNBPortletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BNBPortletManagerRenderer(ColumnPortletManagerRenderer):
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IBNBPortletManager)
    template = ViewPageTemplateFile('templates/column.pt')
