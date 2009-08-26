"""
gites.skin

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
#from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from z3c.sqlalchemy import getSAWrapper
from DateTime import DateTime
import random


class ISejourFute(IPortletDataProvider):
    """A portlet which renders a menu
    """
    title = schema.TextLine(title=u'Title',
                            description=u'The title of the menu',
                            required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

       This is what is actually managed through the portlets UI and associated
       with columns.
    """
    implements(ISejourFute)

    def __init__(self, title=u'', menu_id=u''):
        self._title = title

    @property
    def title(self):
        return self._title


class Renderer(base.Renderer):
    """Portlet renderer.

       This is registered in configure.zcml. The referenced page template is
       rendered, and the implicit variable 'view' will refer to an instance
       of this class. Other methods can be added and referenced in the template.
    """

    render = ZopeTwoPageTemplateFile('templates/sejourfute.pt')

    def title(self):
        return self.data.title

    @property
    def available(self):
        """By default, portlets are available
        """
        return True

    def getRandomSejourFute(self):
        """
        Retourne 1 sejour futé (non expiré) au hasard.
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='SejourFute',
                                    end={'query': DateTime(),
                                              'range': 'min'},
                                    review_state='published')
        results = list(results)
        random.shuffle(results)
        for sejour in results:
            if "%s/" % sejour.getURL() not in self.request.URL and \
               sejour.getURL() != self.request.URL:
                return [sejour]
        if len(results) > 0:
            return [results[0]]
        else:
            return None

    def getAllSejoursView(self):
        """
        Get the link to all sejour fute
        """
        utool = getToolByName(self.context, 'portal_url')
        return '%s/sejour-fute' % utool()

    def getRandomVignette(self, sejour_url, amount=1):
        """
        Return a random vignette for a sejour fute
        """
        cat = getToolByName(self.context, 'portal_catalog')
        results = cat.searchResults(portal_type='Vignette',
                                         path={'query': sejour_url})
        results = list(results)
        random.shuffle(results)
        return results[:amount]

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
        hebergements = session.query(Hebergements).select_by(Hebergements.c.heb_pk.in_(*hebList))
        for maisonTourisme in maisonTourismes:
            maison = session.query(MaisonTourisme).get(maisonTourisme)
            for commune in maison.commune:
                hebergements += list(commune.relatedHebergement)
        # unique !
        hebergements = list(set(hebergements))
        hebergements.sort(lambda x, y: cmp(x.heb_nom, y.heb_nom))
        hebergements = [hebergement.__of__(self.context.hebergement) for hebergement in hebergements]
        return hebergements

    def getAllSejourFute(self):
        results = self.cat.searchResults(portal_type='SejourFute',
                                               end={'query': DateTime(),
                                                    'range': 'min'},
                                               review_state='published')
        results = list(results)
        random.shuffle(results)
        return results


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISejourFute)

    def create(self, data):
        return Assignment(title=data.get('title', u''))


class EditForm(base.EditForm):
    """Portlet edit form.
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISejourFute)
