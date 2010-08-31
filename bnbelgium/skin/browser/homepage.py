from zope.interface import implements
from Products.Five import BrowserView
from Acquisition import aq_inner

from bnbelgium.skin.browser.interfaces import IHomepage


class Homepage(BrowserView):
    """
    Peer reviews root folder view
    """
    implements(IHomepage)

    def getText(self):
        homepageDocument = getattr(aq_inner(self.context), 'home-page')
        homepageDocument = homepageDocument.getTranslation()
        return homepageDocument.getRawText()
