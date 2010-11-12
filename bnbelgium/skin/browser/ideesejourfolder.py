# -*- coding: utf-8 -*-
"""
gites.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from Products.CMFCore.utils import getToolByName
from sqlalchemy import select
from z3c.sqlalchemy import getSAWrapper
from zope.interface import Interface

from gites.core.content.interfaces import IIdeeSejourFolder
from gites.core.browser.ideesejourfolder import IdeeSejourFolder as CoreIdeeSejourFolder

from bnbelgium.skin.browser.interfaces import IBNBelgiumTheme

BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']

grok.context(Interface)
grok.templatedir('templates')
grok.layer(IBNBelgiumTheme)


class IdeeSejourFolder(CoreIdeeSejourFolder):
    """
    View on Idee Sejour folder
    """
    grok.context(IIdeeSejourFolder)
    grok.name('idee_sejour_folder')
    grok.require('zope2.View')

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
        bnbHebs = []
        for result in results:
            hebPks = result.getHebergements()
            wrapper = getSAWrapper('gites_wallons')
            Hebergement = wrapper.getMapper('hebergement')
            TypeHebergement = wrapper.getMapper('type_heb')
            query = select([Hebergement.heb_pk])
            query.append_whereclause(Hebergement.heb_pk.in_(hebPks))
            query.append_whereclause(TypeHebergement.type_heb_pk == Hebergement.heb_typeheb_fk)
            query.append_whereclause(TypeHebergement.type_heb_code.in_(BNB_TYPES_HEB))
            if len(query.execute().fetchall()) > 0:
                bnbHebs.append(result)
        return bnbHebs
