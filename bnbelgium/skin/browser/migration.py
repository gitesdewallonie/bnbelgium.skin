# -*- coding: utf-8 -*-
"""
bnbelgium.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from Products.Five import BrowserView
from bnbelgium.skin.interfaces import IBNBelgiumRootFolder
from zope.interface import alsoProvides


class Migration(BrowserView):

    def __call__(self):
        alsoProvides(self.context.bnb, IBNBelgiumRootFolder)
