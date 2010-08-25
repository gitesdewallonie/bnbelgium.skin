# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from zope.component import queryMultiAdapter

BNB_TYPES_HEB = ['CH', 'MH', 'CHECR']
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

    search_results = ViewPageTemplateFile('templates/search_results_BNB.pt')

    def getHebergementByNameOrPk(self, reference):
        """
        Get the url of the hebergement by Pk or part of the name
        """
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebTable = wrapper.getMapper('hebergement')
        proprioTable = wrapper.getMapper('proprio')
        typeTable = wrapper.getMapper('type_heb')
        try:
            int(reference)
        except ValueError:
            # we have a heb name to search for
            query = session.query(hebTable).join('proprio').join('type')
            query = query.filter(hebTable.heb_site_public == '1')
            query = query.filter(proprioTable.pro_etat == True)
            query = query.filter(typeTable.type_heb_code.in_(BNB_TYPES_HEB))
            query = query.filter(hebTable.heb_nom.ilike("%%%s%%" % reference))
            query = query.order_by(hebTable.heb_nom)
            query = query.limit(100)  # performance matters
            self.selectedHebergements = [hebergement.__of__(self.context.hebergement) for hebergement in query.all()]
            if len(self.selectedHebergements) == 1:
                hebURL = queryMultiAdapter((self.selectedHebergements[0], self.request),
                                           name="url")
                self.request.response.redirect(str(hebURL))
                return ''
            return self.search_results()
        else:
            # we have a heb pk to search for
            hebergement = session.query(hebTable).get(reference)
            if hebergement and \
               int(hebergement.heb_site_public) == 1 and \
               hebergement.proprio.pro_etat and \
               hebergement.type.type_heb_code in BNB_TYPES_HEB:
               # L'hébergement doit être actif, ainsi que son propriétaire
                hebURL = queryMultiAdapter((hebergement.__of__(self.context.hebergement), self.request), name="url")
                self.request.response.redirect(str(hebURL))
                return ''
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

    def getGroupedHebergementTypes(self):
        """
        retourne les deux groupes de types d'hebergements
        """
        # get some translation interfaces
        translation_service = getToolByName(self.context,
                                            'translation_service')

        utranslate = translation_service.utranslate
        lang = self.request.get('LANGUAGE', 'en')
        return [{'pk': -2,
                 'name': utranslate('gites', "Gites et Meubles",
                                    context=self.context,
                                    target_language=lang,
                                    default="Gites")},
                {'pk': -3,
                 'name': utranslate('gites', "Chambre d'hote",
                                    context=self.context,
                                    target_language=lang,
                                    default="Chambre d'hote")}]
