from zope import schema
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from plone.portlets.interfaces import IPortletManager
from zope.viewlet.interfaces import IViewletManager
from gites.skin import GitesMessage as _


class IPromoOutil(IViewletManager):
    """
    Viewelet manager qui gere les viewlets promo de la homepage
    sejour fute - idee sejour - boutique - derniere minute
    """


class IBNBelgiumTheme(IDefaultPloneLayer):
    """
    Theme for BNBelgium
    """


class IHomePageNews(Interface):
    """
    Gestion des viewlets sur la homepage
    """


class IBNBPortletManager(IPortletManager):
    """
    Portlet Manager
    """


class IMoteurRecherche(Interface):

    def getHebergementByPk(heb_pk):
        """
        Get the url of the hebergement by Pk
        """

    def getCommunes():
        """
        Get communes list
        """

    def getTarifs():
        """
        Get tarifs list
        """

    def getClassification():
        """
        Get classifications list
        """

    def getHebergementTypes():
        """
        retourne les types d hebergements
        table type_heb
        """

    def getGroupedHebergementTypes():
        """
        retourne les deux groupes de types d'hebergements
        """


class IBNBSearchHebergement(Interface):
    """
    A basic search module to search BNB hebergement
    """

    commune = schema.Choice(
        title=_('Town'),
        required=True,
        vocabulary="bnbelgium.communes")

    tarif = schema.Choice(
        title=_('Price'),
        required=True,
        vocabulary="bnbelgium.tarif")

    classification = schema.Choice(
        title=_('Classification'),
        required=True,
        vocabulary="bnbelgium.classification")

    capacityMin = schema.Int(title=_('Minimum Capacity'),
                             required=False)


class IBNBSearchHebergementTooMuch(Interface):
    """
    A basic search module to search BNB hebergement
    """
    seeResults = schema.Bool(title=_('Show results even if more than 50'),
                             required=False)

    commune = schema.Choice(
        title=_('Town'),
        required=True,
        vocabulary="bnbelgium.communes")

    tarif = schema.Choice(
        title=_('Price'),
        required=True,
        vocabulary="bnbelgium.tarif")

    classification = schema.Choice(
        title=_('Classification'),
        required=True,
        vocabulary="bnbelgium.classification")

    capacityMin = schema.Int(title=_('Minimum Capacity'),
                             required=False)
