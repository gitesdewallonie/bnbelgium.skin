# -*- coding: utf-8 -*-

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.component import queryMultiAdapter


class CommunesVocabulary(object):
    """
    Vocabulaire pour les communes et localités
    """
    implements(IVocabularyFactory)

    def getCommunes(self, context):
        request = context.REQUEST
        view = queryMultiAdapter((context, request),
                                 name="moteur_recherche_view")
        return view.getCommunes()

    def __call__(self, context, name=None):
        """
        return the commune vocabulary in the db
        """
        items = []
        blankTerm = SimpleTerm(value='-1', token='-1', title=' ')
        items.append(blankTerm)
        for commune in self.getCommunes(context):
            try:
                term = SimpleTerm(value=commune,
                                  token=commune,
                                  title=commune)
            except:
                pass
            else:
                items.append(term)
        return SimpleVocabulary(items)

CommunesVocabularyFactory = CommunesVocabulary()


class TarifsVocabulary(object):
    """
    Vocabulaire pour les tarifs
    """
    implements(IVocabularyFactory)

    def getTarifs(self, context):
        request = context.REQUEST
        view = queryMultiAdapter((context, request),
                                 name="moteur_recherche_view")
        return view.getTarifs()

    def __call__(self, context, name=None):
        """
        return the tarif vocabulary in the db
        """
        items = []
        blankTerm = SimpleTerm(value='-1', token='-1', title=' ')
        items.append(blankTerm)
        for tarif in self.getTarifs(context):
            infinite = tarif['max'] == -1 and u"> " or u""
            maxPrice = tarif['max'] != -1 and u" - %s€" % tarif['max'] or u""
            title = u"%s%s€%s" % (infinite, tarif['min'], maxPrice)
            term = SimpleTerm(value=tarif['pk'],
                              token=tarif['pk'],
                              title=title)
            items.append(term)
        return SimpleVocabulary(items)

TarifsVocabularyFactory = TarifsVocabulary()


class ClassificationVocabulary(object):
    """
    Vocabulaire pour les classifications
    """
    implements(IVocabularyFactory)

    def getClassifications(self, context):
        request = context.REQUEST
        view = queryMultiAdapter((context, request),
                                 name="moteur_recherche_view")
        return view.getClassifications()

    def __call__(self, context, name=None):
        """
        return the classification vocabulary in the db
        """
        classification_items = []
        blankTerm = SimpleTerm(value=-1, token=-1, title=' ')
        classification_items.append(blankTerm)
        for value in xrange(1, 5): #classification de 1 a 4
            term = SimpleTerm(value=value,
                              token=value,
                              title=str(value))
            classification_items.append(term)
        return SimpleVocabulary(classification_items)

ClassificationsVocabularyFactory = ClassificationVocabulary()
