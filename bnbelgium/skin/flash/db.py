# -*- coding: utf-8 -*-
"""
bnbelgium.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import select
from gites.core.flash.db import FlashGitesView
BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']


class FlashBNBView(FlashGitesView):

    def getHebergements(self):
        wrapper = getSAWrapper('gites_wallons')
        Hebergement = wrapper.getMapper('hebergement')
        TypeHebergement = wrapper.getMapper('type_heb')
        query = select([Hebergement.heb_pk,
                        TypeHebergement.type_heb_code,
                        TypeHebergement.type_heb_nom,
                        Hebergement.heb_gps_long.label('heb_gps_lat'),
                        Hebergement.heb_gps_lat.label('heb_gps_long'),
                        Hebergement.heb_cgt_cap_max,
                        Hebergement.heb_localite,
                        Hebergement.heb_cgt_cap_min,
                        Hebergement.heb_nom])
        query.append_whereclause(TypeHebergement.type_heb_pk == Hebergement.heb_typeheb_fk)
        query.append_whereclause(TypeHebergement.type_heb_code.in_(BNB_TYPES_HEB))
        return self._adaptsSAResults(query.execute().fetchall())
