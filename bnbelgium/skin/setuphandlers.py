# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from Products.CMFCore.utils import getToolByName
from Products.Five.component import enableSite
from zope.app.component.interfaces import ISite
from plone.app.portlets.portlets import login
import logging
from gites.core.utils import (createFolder, createPage)
logger = logging.getLogger('BNBelgium.skin')

LANGUAGES = ['fr', 'nl', 'en', 'it', 'de']


def setupBNBelgium(context):
    if context.readDataFile('bnbelgium.skin_various.txt') is None:
        return
    logger.debug('Setup BNBelgium skin')
    portal = context.getSite()
    if not ISite.providedBy(portal):
        enableSite(portal)
    createContent(portal)
    setupSubSiteSkin(portal)
    blockParentPortlets(portal.bnb)
    return
    manager = getUtility(IPortletManager, name=u'bnbelgium.portlets',
                         context=portal)
    assignments = getMultiAdapter((portal, manager),
                                  IPortletAssignmentMapping)
    assignment = login.Assignment(title='logintest')
    assignments['login'] = assignment


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


def changeFolderView(portal, folder, viewname):
    addViewToType(portal, 'Folder', viewname)
    if folder.getLayout() != viewname:
        folder.setLayout(viewname)


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


def createContent(portal):
    #Create empty documents and folders
    bnb = createFolder(portal, 'bnb', "BnBelgium; les chambres d'hôtes en Ardenne et Wallonie", True)
    #blockParentPortlets(bnb)
    #alsoProvides(bnb, IBNBFolder)
    #### MENU SUPERIEUR ####
    createPage(bnb, "chambres-d-hote", "Chambres d'hôte")
    createPage(bnb, "decouvrir-la-wallonie", "Découvrir la Wallonie ?")
    createPage(bnb, "proposer-votre-hebergement", "Proposer votre hébergement")
    createPage(bnb, "contact", "Contact")


def setupSubSiteSkin(portal):
    portal_props = getToolByName(portal, 'portal_properties')
    editskin_props = portal_props.get('editskin_switcher')
    editskin_props.switch_skin_action = 'based on specific domains'
    editskin_props.specific_domains = ("http://www.bnbelgium.be/plone1", )
    editskin_props.edit_skin = "BNBelgium Skin"
