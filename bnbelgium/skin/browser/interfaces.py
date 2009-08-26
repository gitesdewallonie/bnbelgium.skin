from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from plone.portlets.interfaces import IPortletManager


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
