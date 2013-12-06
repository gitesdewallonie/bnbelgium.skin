# -*- coding: utf-8 -*-

import tempfile
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.app.component.interfaces import ISite
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from Products.Five.component import enableSite
from Products.CMFCore.utils import getToolByName
from Products.LocalFS.LocalFS import manage_addLocalFS
import logging

from bnbelgium.skin.portlets import (sejourfute, derniereminute, ideesejour)
from gites.skin.setuphandlers import createTranslationsForObject, \
                                     changeFolderView
from gites.core.utils import createFolder, createPage, publishObject
from bnbelgium.skin.browser.interfaces import IBNBPortletManager
from zope.interface import alsoProvides
from plone.portlets.manager import PortletManager

logger = logging.getLogger('BNBelgium.skin')
LANGUAGES = ['en', 'nl', 'fr', 'it', 'de']


def registerPortletManager(portal):
    sm = portal.getSiteManager()
    registeredPortletManagers = [r.name for r in sm.registeredUtilities()
                                    if r.provided.isOrExtends(IPortletManager)]
    if 'bnbelgium.portlets' not in registeredPortletManagers:
        manager = PortletManager()
        alsoProvides(manager, IBNBPortletManager)
        sm.registerUtility(component=manager,
                               provided=IPortletManager,
                               name='bnbelgium.portlets')


def setupBNBelgium(context):

    if context.readDataFile('bnbelgium.skin_various.txt') is None:
        return
    logger.debug('Setup BNBelgium skin')
    portal = context.getSite()
    if not ISite.providedBy(portal):
        enableSite(portal)
    registerPortletManager(portal)
    setupLanguages(portal)
    createLocalFS(portal)
    # createContent(portal)
    createHebergementFolder(portal, 'hebergement')
    # setupSubSiteSkin(portal)
    blockParentPortlets(portal)
    clearPortlets(portal)
    changeFolderView(portal, portal, 'bnb_homepage')
    setupPromoBoxesPortlets(portal)


def createLocalFS(portal):
    if 'photos_heb' not in portal.objectIds():
        manage_addLocalFS(portal, 'photos_heb', 'Photos heb',
                          tempfile.gettempdir())


def setupLanguages(portal):
    lang = getToolByName(portal, 'portal_languages')
    lang.supported_langs = LANGUAGES
    lang.setDefaultLanguage('fr')
    lang.display_flags = 0


def getManager(folder, column):
    if column == 'left':
        manager = getUtility(IPortletManager, name=u'plone.leftcolumn', context=folder)
    else:
        manager = getUtility(IPortletManager, name=u'plone.rightcolumn', context=folder)
    return manager


def addViewToType(portal, typename, templatename):
    pt = getToolByName(portal, 'portal_types')
    foldertype = getattr(pt, typename)
    available_views = list(foldertype.getAvailableViewMethods(portal))
    if not templatename in available_views:
        available_views.append(templatename)
        foldertype.manage_changeProperties(view_methods=available_views)


def clearColumnPortlets(folder, column):
    manager = getManager(folder, column)
    assignments = getMultiAdapter((folder, manager), IPortletAssignmentMapping)
    for portlet in assignments:
        del assignments[portlet]


def clearPortlets(folder):
    clearColumnPortlets(folder, 'left')
    clearColumnPortlets(folder, 'right')


def blockParentPortlets(folder):
    manager = getManager(folder, 'left')
    assignable = getMultiAdapter((folder, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
    manager = getManager(folder, 'right')
    assignable = getMultiAdapter((folder, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def setupPromoBoxesPortlets(folder):
    portal = getToolByName(folder, 'portal_url').getPortalObject()
    manager = getUtility(IPortletManager, name='bnbelgium.portlets', context=portal)
    assignments = getMultiAdapter((folder, manager), IPortletAssignmentMapping)
    if 'sejourfute' in assignments.keys():
        del assignments['sejourfute']
    if 'derniereminute' in assignments.keys():
        del assignments['derniereminute']
    if 'ideesejour' in assignments.keys():
        del assignments['ideesejour']

    if 'sejourfute' not in assignments.keys():
        assignment = sejourfute.Assignment('Sejour Fute')
        assignments['sejourfute'] = assignment
    if 'derniereminute' not in assignments.keys():
        assignment = derniereminute.Assignment('Derniere minute')
        assignments['derniereminute'] = assignment
    if 'ideesejour' not in assignments.keys():
        assignment = ideesejour.Assignment('Idee sejour')
        assignments['ideesejour'] = assignment
    # if 'laboutique' not in assignments.keys():
    #     assignment = laboutiquefolder.Assignment('La boutique')
    #     assignments['laboutique'] = assignment


def createContent(portal):
    #Create empty documents and folders
    bnb = portal
    chambreHote = createPage(bnb, "chambres-dhotes", "Chambres d'hôtes")
    chambreHote.setLanguage('fr')
    chambreHote._at_creation_flag = True
    decouvrirWallonie = createPage(bnb, "decouvrir-la-wallonie", "Découvrir la Wallonie ?")
    decouvrirWallonie.setLanguage('fr')
    proposerHebergement = createPage(bnb, "proposer-votre-hebergement", "Proposer votre hébergement")
    proposerHebergement.setLanguage('fr')
    contact = createPage(bnb, "contact", "Contact")
    contact.setLanguage('fr')
    mapFolder = createFolder(bnb, "map", "Map", True)
    changeFolderView(portal, mapFolder, 'hebergement_map')
    createTranslationsForObject(mapFolder)


def setupSubSiteSkin(portal):
    portal_props = getToolByName(portal, 'portal_properties')
    editskin_props = portal_props.get('editskin_switcher')
    editskin_props.switch_skin_action = 'based on specific domains'
    specDomains = ["http://www.bnbelgium.be/plone",
                   "http://bnb2.affinitic.be/plone"]
    for i in editskin_props.getProperty('specific_domains'):
        if i not in specDomains:
            specDomains.append(i)
    editskin_props.specific_domains = tuple(specDomains)
    editskin_props.edit_skin = "BNBelgium Skin"


def createHebergementFolder(parentFolder, folderId):
    if folderId not in parentFolder.objectIds():
        parentFolder.invokeFactory('HebergementFolder', folderId)
    createdFolder = getattr(parentFolder, folderId)
    createdFolder.reindexObject()
    publishObject(createdFolder)
    createdFolder.reindexObject()
    createdFolder.update()
    return createdFolder
