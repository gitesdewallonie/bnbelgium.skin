# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from zope.component import queryMultiAdapter

BNB_TYPES_HEB = ['CH', 'CHECR']
BNB_TARIFS = [{'pk':0,
               'min':30,
               'max':50},
              {'pk':1,
               'min':50,
               'max':70},
              {'pk':2,
               'min':70,
               'max':90},
              {'pk':3,
               'min':90,
               'max':110},
              {'pk':4,
               'min':110,
               'max':-1}]


class BNBMoteurRecherche(BrowserView):

    def getHebergementByPk(self, heb_pk):
        """
        Get the url of the hebergement by Pk
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        HebTable = wrapper.getMapper('hebergement')
        try:
            int(heb_pk)
        except ValueError:
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            return queryMultiAdapter((portal, self.request),
                                      name="unknown_gites")()
        hebergement = session.query(HebTable).get(heb_pk)
        if hebergement and hebergement.type.type_heb_code in BNB_TYPES_HEB:
            hebURL = queryMultiAdapter((hebergement.__of__(self.context.hebergement),
                                        self.request), name="url")
            return self.request.RESPONSE.redirect(str(hebURL))
        else:
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            return queryMultiAdapter((portal, self.request),
                                       name="unknown_gites")()

    def getCommunes(self):
        """
        Get communes list
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        communeTable = wrapper.getMapper('commune')
        typeTable = wrapper.getMapper('type_heb')
        hebergementTable = wrapper.getMapper('hebergement')
        query = session.query(hebergementTable).join('type')
        query = query.filter(typeTable.type_heb_code.in_(BNB_TYPES_HEB))
        query = query.order_by(hebergementTable.heb_localite)
        results = query.all()
        communes = set()
        for heb in results:
            communes.add((heb.commune.com_nom, 'C'))
            communes.add((heb.heb_localite, 'L'))

        def removeDuplicates(results):
            uniqueResults = []
            for result in results:
                if result[1]=='C':
                    if not (result[0], 'L') in results:
                        uniqueResults.append(result)
                else:
                    uniqueResults.append(result)
            return uniqueResults

        communes = removeDuplicates(communes)
        communes.sort()
        return communes

    def getTarifs(self):
        """
        Get tarifs list
        """
        return BNB_TARIFS

    def getClassification(self):
        """
        Get classifications list
        """
        return [value for value in xrange(1, 5)]

    def getHebergementTypes(self):
        """
        retourne les types d hebergements
        table type_heb
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        TypeHeb = wrapper.getMapper('type_heb')
        results = session.query(TypeHeb).all()
        language = self.request.get('LANGUAGE', 'en')
        typesList = []
        for typeHeb in results:
            types = {}
            types['pk'] = typeHeb.type_heb_pk
            types['name'] = typeHeb.getTitle(language)
            typesList.append(types)
        return typesList
