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
from z3c.sqlalchemy import getSAWrapper
import random

BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']


class IIdeeSejour(IPortletDataProvider):
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
    implements(IIdeeSejour)

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

    render = ZopeTwoPageTemplateFile('templates/ideesejour.pt')

    def title(self):
        return self.data.title

    @property
    def available(self):
        """By default, portlets are available
        """
        return True

    def getIdeesTypes(self):
        """
        Returns the list of IdeeTypes available in the current folder
        """
        cat = getToolByName(self.context, 'portal_catalog')
        ideeSejour = getattr(self.context, 'idee-sejour')
        url = '/'.join(ideeSejour.getPhysicalPath())
        contentFilter = {}
        path = {}
        path['query'] = url
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = ['IdeeSejourFolder', 'IdeeSejour']
        contentFilter['sort_on'] = 'getObjPositionInParent'
        contentFilter['review_state'] = 'published'
        results = cat.queryCatalog(contentFilter)
        results = list(results)
        return results

    def getAvailableSejourInFolder(self):
        """
        Returns the list of IdeeSejour available in the current folder
        """
        cat = getToolByName(self.context, 'portal_catalog')
        idee_sejour_url = "/".join(self.context.getPhysicalPath())
        contentFilter = {}
        path = {}
        path['query'] = idee_sejour_url
        path['depth'] = 1
        contentFilter['path'] = path
        contentFilter['portal_type'] = ['IdeeSejourFolder', 'IdeeSejour']
        contentFilter['sort_on'] = 'getObjPositionInParent'
        contentFilter['review_state'] = 'published'
        results = cat.queryCatalog(contentFilter)
        results = [result.getObject() for result in results]
        return results

    def getHebergements(self, sejour=None):
        """
        return the list of hebergement available in the current idee sejour
        """
        wrapper = getSAWrapper('gites_wallons')
        Hebergements = wrapper.getMapper('hebergement')
        TypeHebergement = wrapper.getMapper('type_heb')
        session = wrapper.session
        if sejour is None:
            sejour = self.context

        hebList = [int(i) for i in sejour.getHebergements()]
        query = session.query(Hebergements)
        query = query.filter(Hebergements.heb_pk.in_(hebList))
        query = query.filter(TypeHebergement.type_heb_pk == Hebergements.heb_typeheb_fk)
        query = query.filter(TypeHebergement.type_heb_code.in_(BNB_TYPES_HEB))

        hebergements = query.all()
        hebergements.sort(lambda x, y: cmp(x.heb_nom, y.heb_nom))
        hebergements = [hebergement.__of__(sejour.hebergement) for hebergement in hebergements]
        return hebergements

    def getRandomIdeeSejour(self):
        """
        Get one random idee sejour
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type=['IdeeSejour'],
                                    review_state='published')
        results = list(results)
        random.shuffle(results)
        for sejour in results:
            if len(self.getHebergements(sejour.getObject())) == 0:
                continue
            if "%s/" % sejour.getURL() not in self.request.URL and \
               sejour.getURL() != self.request.URL:
                return sejour

    def getRandomVignette(self, sejour_url, amount=1):
        """
        Return a random vignette for a sejour fute
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='Vignette',
                                    path={'query': sejour_url})
        results = list(results)
        random.shuffle(results)
        return results[:amount]

    def getAllIdeesSejoursView(self):
        """
        Get the link to all the idees sejour
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/idee-sejour' % utool()


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IIdeeSejour)

    def create(self, data):
        return Assignment(title=data.get('title', u''))


class EditForm(base.EditForm):
    """Portlet edit form.
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IIdeeSejour)
