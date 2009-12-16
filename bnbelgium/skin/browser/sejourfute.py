# -*- coding: utf-8 -*-
"""
gites.core override

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from five import grok
from gites.core.content.interfaces import ISejourFute
from zope.interface import Interface
from z3c.sqlalchemy import getSAWrapper
from bnbelgium.skin.browser.interfaces import IBNBelgiumTheme

grok.context(Interface)
grok.templatedir('templates')
grok.layer(IBNBelgiumTheme)


class SejourFute(grok.View):
    """
    View on Idee Sejour
    """
    grok.context(ISejourFute)
    grok.name('sejour_fute_view')
    grok.require('zope2.View')

    def getHebergements(self):
        """
        Return the concerned hebergements by this Sejour fute
        = hebergements linked to the Maison du tourism +
          select hebergements
        """
        wrapper = getSAWrapper('gites_wallons')
        Hebergements = wrapper.getMapper('hebergement')
        MaisonTourisme = wrapper.getMapper('maison_tourisme')
        session = wrapper.session

        hebList = [int(i) for i in self.context.getHebergementsConcernes()]
        maisonTourismes = [int(i) for i in self.context.getMaisonsTourisme()]
        hebergements = session.query(Hebergements).filter(Hebergements.heb_pk.in_(hebList)).all()
        for maisonTourisme in maisonTourismes:
            maison = session.query(MaisonTourisme).get(maisonTourisme)
            for commune in maison.commune:
                hebergements += list(commune.relatedHebergement)
        # unique !
        hebergements = list(set(hebergements))
        hebergements.sort(lambda x, y: cmp(x.heb_nom, y.heb_nom))
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements
