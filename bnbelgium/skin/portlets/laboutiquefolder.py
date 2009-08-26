# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
import random


class ILaBoutique(IPortletDataProvider):
    """A portlet which renders a menu
    """
    title = schema.TextLine(title=u'Title',
                            description=u'The title of the menu',
                            required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(ILaBoutique)

    def __init__(self, title=u'', menu_id=u''):
        self._title = title

    @property
    def title(self):
        return self._title


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ZopeTwoPageTemplateFile('templates/boutique.pt')

    def title(self):
        return self.data.title

    @property
    def available(self):
        """By default, portlets are available
        """
        return True

    def getRandomBoutiqueItem(self):
        """
        Get one random boutiqueItem
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type=['BoutiqueItem'],
                                    review_state='published')
        results = list(results)
        random.shuffle(results)
        for boutiqueItem in results:
            if "%s/" % boutiqueItem.getURL() not in self.request.URL and \
               boutiqueItem.getURL() != self.request.URL:
                return boutiqueItem.getObject()
        return None

    def getAllBoutiqueItemsView(self):
        """
        Get the link to all boutique items
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/la-boutique' % utool()


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ILaBoutique)

    def create(self, data):
        return Assignment(title=data.get('title', u''))


class EditForm(base.EditForm):
    """Portlet edit form.
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ILaBoutique)
