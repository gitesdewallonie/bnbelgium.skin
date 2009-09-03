# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from Products.CMFCore.utils import getToolByName
import logging

from gites.skin.portlets import (sejourfute, derniereminute, ideesejour,
                                 laboutiquefolder)
from gites.skin.setuphandlers import createTranslationsForObject, \
                                     changeFolderView
from gites.core.utils import createFolder, createPage, publishObject
from bnbelgium.skin.browser.interfaces import IBNBPortletManager
from zope.interface import alsoProvides
from plone.portlets.manager import PortletManager

logger = logging.getLogger('BNBelgium.skin')


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
    registerPortletManager(portal)
    createContent(portal)
    createHebergementFolder(portal.bnb, 'hebergement')
    setupSubSiteSkin(portal)
    blockParentPortlets(portal.bnb)
    clearPortlets(portal.bnb)
    changeFolderView(portal, portal.bnb, 'bnb_homepage')
    setupPromoBoxesPortlets(portal.bnb)
    return
    #manager = getUtility(IPortletManager, name=u'bnbelgium.portlets',
    #                     context=portal)
    #assignments = getMultiAdapter((portal, manager),
    #                              IPortletAssignmentMapping)
    #assignment = login.Assignment(title='logintest')
    #assignments['login'] = assignment


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
    if 'sejourfute' not in assignments.keys():
        assignment = sejourfute.Assignment('Sejour Fute')
        assignments['sejourfute'] = assignment
    if 'derniereminute' not in assignments.keys():
        assignment = derniereminute.Assignment('Derniere minute')
        assignments['derniereminute'] = assignment
    if 'ideesejour' not in assignments.keys():
        assignment = ideesejour.Assignment('Idee sejour')
        assignments['ideesejour'] = assignment
    if 'laboutique' not in assignments.keys():
        assignment = laboutiquefolder.Assignment('La boutique')
        assignments['laboutique'] = assignment


def createContent(portal):
    #Create empty documents and folders
    bnb = createFolder(portal, 'bnb', "BnBelgium; les chambres d'hôtes en Ardenne et Wallonie", True)
    createPage(bnb, "chambres-d-hote", "Chambres d'hôte")
    createPage(bnb, "decouvrir-la-wallonie", "Découvrir la Wallonie ?")
    createPage(bnb, "proposer-votre-hebergement", "Proposer votre hébergement")
    createPage(bnb, "contact", "Contact")
    mapFolder = createFolder(bnb, "map", "Map", True)
    changeFolderView(portal, mapFolder, 'hebergement_map')
    createTranslationsForObject(mapFolder)


def setupSubSiteSkin(portal):
    portal_props = getToolByName(portal, 'portal_properties')
    editskin_props = portal_props.get('editskin_switcher')
    editskin_props.switch_skin_action = 'based on specific domains'
    editskin_props.specific_domains = ("http://www.bnbelgium.be/gites", )
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
