from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from plone.portlets.interfaces import IPortletManager
from zope.viewlet.interfaces import IViewletManager


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
