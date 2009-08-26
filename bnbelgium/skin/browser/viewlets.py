# -*- coding: utf-8 -*-
"""
BNBelgium.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id$
"""
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from zope.component import getMultiAdapter
from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector


class BNBelgiumSectionsViewlet(GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/headerBNBelgium.pt')

    def logo_tag(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        portal = portal_state.portal()
        logoName = portal.restrictedTraverse('base_properties').logoName
        return portal.restrictedTraverse(logoName).tag()


class BNBMenuSupViewlet(GlobalSectionsViewlet):
        render = ViewPageTemplateFile('templates/menu_sup.pt')


class BNBMoteurRechercheViewlet(GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/moteur_recherche.pt')


class BNBOutilsPromoViewlet(GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/outil_promo.pt')


class ApplicaTranslatableLanguageSelector(TranslatableLanguageSelector):
    """Language selector for translatable content.
    """
    render = ViewPageTemplateFile('templates/language_selector.pt')


class BNBelgiumFooter(GlobalSectionsViewlet):
    render = ViewPageTemplateFile('templates/footerBNBelgium.pt')