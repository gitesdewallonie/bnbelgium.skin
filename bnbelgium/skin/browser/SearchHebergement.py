# -*- coding: utf-8 -*-

from zope.formlib import form
from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import and_, or_

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from gites.core.content.ideesejour import IdeeSejour

from gites.skin import GitesMessage as _
from gites.skin import GitesLocalesMessage as localTranslate
from bnbelgium.skin.browser.interfaces import (IBNBSearchHebergement,
                                               IBNBSearchHebergementTooMuch)
from bnbelgium.skin.browser.moteur_recherche import BNB_TARIFS
from gites.skin.browser.SearchHebergement import SearchHebergement


class BNBSearchHebergement(SearchHebergement):
    """
    A search module to search BNB hebergement
    """
    label = _("Search Hebergement")

    form_fields = form.FormFields(IBNBSearchHebergement)
    too_much_form_fields = form.FormFields(IBNBSearchHebergementTooMuch)

    search_results = ViewPageTemplateFile('templates/search_results_BNB.pt')

    def getCommuneForLocalite(self, localite):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        communeTable = wrapper.getMapper('commune')
        query = session.query(communeTable).join('relatedHebergement')
        query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                  hebergementTable.heb_localite == localite))
        commune = query.first()
        return commune

    def filterByPrice(self, results, tarifMin, tarifMax):
        """
        Price in DB are like '50.00' or '50.00/70.00'
        This method parses this field and compare values to search criteria
        """
        if tarifMax is None:
            tarifMax = 1e10  #tarif max infini, plus rapide pour les comparaison
        def isRangePricedHeb(heb):
            hebTarifs = heb.heb_tarif_chmbr_avec_dej_2p
            if '/' in hebTarifs:
                hebMin, hebMax = hebTarifs.split('/')
                hebMin = int(float(hebMin))
                hebMax = int(float(hebMax))
                return (hebMin >= tarifMin and hebMin <= tarifMax) \
                       or (hebMax >= tarifMin and hebMax <= tarifMax)
            else:
                hebMin = int(float(hebTarifs))
                return hebMin >= tarifMin and hebMin <= tarifMax
        return [heb for heb in results if isRangePricedHeb(heb)]

    def sortSearchResults(self, results, commune, localite):
        """
        si le visiteur choisit une localité > hébergements de la localité
                                              (en premier) + de la commune
        si le visiteur choisit une commune > hébergements situés sur la localité
                                             identique à la commune (en premier)
                                             + tous les hébergements de la commune.
        """
        sortedResults = []
        if localite:
            firstResults = []
            nextResults = []
            for heb in results:
                if heb.heb_localite == localite:
                    firstResults.append(heb)
                else:
                    nextResults.append(heb)
        else:
            firstResults = []
            nextResults = []
            for heb in results:
                if heb.heb_localite == commune:
                    firstResults.append(heb)
                else:
                    nextResults.append(heb)
        sortedResults = firstResults + nextResults
        return sortedResults

    @form.action(localTranslate(u"Search"))
    def action_search(self, action, data):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        hebergementTable = wrapper.getMapper('hebergement')
        communeTable = wrapper.getMapper('commune')
        episTable = wrapper.getMapper('link_hebergement_epis')
        hebergementType = data.get('hebergementType')
        communesLocalites = data.get('commune')
        tarif = data.get('tarif')
        classification = data.get('classification')
        capacityMin = data.get('capacityMin')
        seeResults = self.request.form.has_key('form.seeResults')

        query = session.query(hebergementTable).join('province')

        communeNom = ''
        localite = ''
        if communesLocalites and communesLocalites != '-1':
            placeType, placeName = communesLocalites.split('|')
            if placeType == 'C':
                query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                          communeTable.com_nom == placeName))
                communeNom = placeName
                localite = placeName
            else:
                relatedCommune = self.getCommuneForLocalite(placeName)
                query = query.filter(and_(hebergementTable.heb_com_fk == communeTable.com_pk,
                                          communeTable.com_nom == relatedCommune.com_nom))
                communeNom = relatedCommune.com_nom
                localite = placeName
        hebergementTypes = ['CH', 'MH', 'CHECR']
        hebergementType = self.translateTypes(hebergementTypes)
        query = query.filter(hebergementTable.heb_typeheb_fk.in_(hebergementType))
        if classification and classification != -1:
            query = query.filter(and_(episTable.heb_nombre_epis == classification,
                                      hebergementTable.heb_pk==episTable.heb_pk))
        if capacityMin:
            if capacityMin < 16:
                capacityMax = capacityMin + 4
                query = query.filter(or_(hebergementTable.heb_cgt_cap_min.between(capacityMin, capacityMax),
                                         hebergementTable.heb_cgt_cap_max.between(capacityMin, capacityMax)))
            else:
                capacityMax = capacityMin
                capacityMin = 16
                query = query.filter(and_(hebergementTable.heb_cgt_cap_min >= capacityMin,
                                          hebergementTable.heb_cgt_cap_max >= capacityMax))

        if isinstance(self.context, IdeeSejour):
            sejour = self.context
            filteredHebergements = sejour.getHebergements()
            query = query.filter(hebergementTable.heb_pk.in_(filteredHebergements))

        query = query.order_by(hebergementTable.heb_nom)
        results = query.all()

        if tarif and tarif != -1:
            tarifRange = BNB_TARIFS[tarif]
            tarifMin = int(tarifRange['min'])
            tarifMax = tarifRange['max'] != -1 and int(tarifRange['max']) or None
            results = self.filterByPrice(results, tarifMin, tarifMax)

        results = self.sortSearchResults(results, communeNom, localite)
        self.selectedHebergements = [hebergement.__of__(self.context.hebergement) for hebergement in results]

        nbResults = len(self.selectedHebergements)
        translation_service = getToolByName(self.context,
                                            'translation_service')

        utranslate = translation_service.utranslate
        lang = self.request.get('LANGUAGE', 'en')
        if nbResults > 50 and not seeResults:   #il faut affiner la recherche
            self.form_fields = self.too_much_form_fields
            form.FormBase.resetForm(self)
            self.widgets['capacityMin'].setRenderedValue(capacityMin)

            message = utranslate('gites',
                                 "La recherche a renvoy&eacute; ${nbr} r&eacute;sultats. <br /> Il serait utile de l'affiner.",
                                 {'nbr': nbResults},
                                 target_language=lang,
                                 context=self.context)
            self.errors += (message,)
            self.status = " "
            return self.template()

        else:   #on montre tous les resultats, independamment du nombre
            if nbResults == 0:
                message = utranslate('gites',
                                     "La recherche n'a pas renvoy&eacute; de r&eacute;sultats.",
                                     target_language=lang,
                                     context=self.context)
                self.errors += (message,)
                self.status = " "
                return self.template()
            else:
                return self.search_results()
