# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
#from Products.Five import BrowserView
from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import desc, select
from DateTime import DateTime
import random

BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']


class IDerniereMinute(IPortletDataProvider):
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
    implements(IDerniereMinute)

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

    render = ZopeTwoPageTemplateFile('templates/derniereminute.pt')

    def title(self):
        return self.data.title

    @property
    def available(self):
        """By default, portlets are available
        """
        return True

    def _filterBNBHebergements(self, hebergements):
        hebBrains = {}
        for hebergement in hebergements:
            obj = hebergement.getObject()
            hebPk = int(obj.hebergementsConcernes[0])
            hebBrains[hebPk] = hebergement
        wrapper = getSAWrapper('gites_wallons')
        Hebergement = wrapper.getMapper('hebergement')
        TypeHebergement = wrapper.getMapper('type_heb')
        query = select([Hebergement.heb_pk])
        query.append_whereclause(Hebergement.heb_pk.in_(hebBrains.keys()))
        query.append_whereclause(TypeHebergement.type_heb_pk == Hebergement.heb_typeheb_fk)
        query.append_whereclause(TypeHebergement.type_heb_code.in_(BNB_TYPES_HEB))
        bnbPks = [r.heb_pk for r in query.execute().fetchall()]
        return [hebBrains[pk] for pk in bnbPks]

    def _getValidDerniereMinute(self):
        """
        Retourne 1 sejour futé (non expiré) au hasard.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='DerniereMinute',
                                         end={'query': DateTime(),
                                              'range': 'min'},
                                         review_state='published')
        results = list(results)
        results = self._filterBNBHebergements(results)
        random.shuffle(results)
        return results

    def getRandomDerniereMinute(self):
        """
        Retourne 1 derniere minute au hasard
        """
        results = self._getValidDerniereMinute()
        for derniereMinute in results:
            if "%s/" % derniereMinute.getURL() not in self.request.URL and \
               derniereMinute.getURL() != self.request.URL:
                return [derniereMinute.getObject()]

    def getAllDerniereMinuteLink(self):
        """
        Get the link to all sejour fute
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/dernieres-minutes' % utool()

    def getNiceEventStartDate(self, obj):
        startDate = obj.getEventStartDate()
        return startDate.strftime("%d-%m")

    def getNiceEventEndDate(self, obj):
        endDate = obj.getEventEndDate()
        return endDate.strftime("%d-%m")

    def getText(self, obj):
        return obj.getText()

    def getCategory(self, obj):
        return obj.getCategory()

    def getLastPromotions(self):
        results = self._getValidDerniereMinute()
        validPromotions = []
        for promotionBrain in results:
            promotion = promotionBrain.getObject()
            if promotion.getCategory() == 'promotion':
                validPromotions.append(promotion)
        return validPromotions

    def getLastDerniereMinute(self):
        results = self._getValidDerniereMinute()
        validLastMinut = []
        for lastMinutBrain in results:
            lastMinut = lastMinutBrain.getObject()
            if lastMinut.getCategory() == 'derniere-minute':
                validLastMinut.append(lastMinut)
        return validLastMinut

    def getLastHebergements(self):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        table = wrapper.getMapper('hebergement')
        results = session.query(table).select(order_by=[desc(table.c.heb_pk)],
                                             limit=10)
        results = [hebergement.__of__(self.context.hebergement) for hebergement in results]
        return results


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IDerniereMinute)

    def create(self, data):
        return Assignment(title=data.get('title', u''))


class EditForm(base.EditForm):
    """Portlet edit form.
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IDerniereMinute)
