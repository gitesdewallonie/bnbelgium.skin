# -*- coding: utf-8 -*-
"""
GitesSkin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: translations.py 1859 2008-03-12 16:05:18Z jfroche $
"""
from Products.Five.browser import BrowserView
#from Products.CMFCore.utils import getToolByName


class Translate(BrowserView):
    """
    Translate object
    """

    def getTranslatedObjectUrl(self, path):
        """
        """
        #portal = getToolByName(self.context, 'portal_url').getPortalObject()
        #bnbFolder = getattr(portal, 'bnb')
        #try:
        #    obj = self.context.restrictedTraverse(path)
        #except KeyError:
        #    obj = bnbFolder.restrictedTraverse(path)
        #translatedObject = obj.getTranslation()
        #if translatedObject:
        #    url = translatedObject.absolute_url()
        #else:
        #    url = obj.absolute_url()
        #return url
        return