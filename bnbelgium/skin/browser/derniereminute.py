# -*- coding: utf-8 -*-
"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from five import grok
from zope.interface import Interface
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import select, desc
from DateTime import DateTime
import random

from gites.core.browser.derniereminuterootfolder import DerniereMinuteRootFolder as RootDMRF
from gites.skin.interfaces import IDerniereMinuteRootFolder
from bnbelgium.skin.browser.interfaces import IBNBelgiumTheme

BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']

grok.context(Interface)
grok.templatedir('templates')
grok.layer(IBNBelgiumTheme)


class DerniereMinuteRootFolder(RootDMRF):
    """
    View for the root of the derniere minute folder
    """
    grok.context(IDerniereMinuteRootFolder)
    grok.name('derniere_minute_root_folder')
    grok.require('zope2.View')

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

    def _getValidDernieresMinutes(self):
        results = self.cat.searchResults(portal_type='DerniereMinute',
                                               end={'query': DateTime(),
                                                    'range': 'min'},
                                               review_state='published')
        results = list(results)
        results = self._filterBNBHebergements(results)
        random.shuffle(results)
        return results

    def getLastHebergements(self):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        Hebergement = wrapper.getMapper('hebergement')
        TypeHebergement = wrapper.getMapper('type_heb')
        query = session.query(Hebergement)
        query = query.filter(Hebergement.heb_site_public == '1')
        query = query.filter(TypeHebergement.type_heb_pk == Hebergement.heb_typeheb_fk)
        query = query.filter(TypeHebergement.type_heb_code.in_(BNB_TYPES_HEB))
        query = query.order_by(desc(Hebergement.heb_pk))
        query = query.limit(10)
        results = [hebergement.__of__(self.context.hebergement) for hebergement in query.all()]
        return results
