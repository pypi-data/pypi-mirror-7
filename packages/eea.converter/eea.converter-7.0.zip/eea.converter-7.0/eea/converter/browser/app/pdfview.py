""" PDF Views
"""
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.converter.utils import truncate

class Cover(BrowserView):
    """ PDF Cover
    """
    template = ViewPageTemplateFile('../zpt/pdf.cover.pt')

    def truncate(self, text, length=300, orphans=10, suffix=u".", end=u"."):
        """
        Truncate text by the number of characters without cutting words at
        the end.

        Orphans is the number of trailing chars not to cut, for example

        If end char provided try to separate by it
        """
        return truncate(text, length, orphans, suffix, end)

    def __call__(self, **kwargs):
        return self.template()

class Disclaimer(Cover):
    """ PDF Disclaimer
    """
    template = ViewPageTemplateFile('../zpt/pdf.disclaimer.pt')

class Toc(Cover):
    """ PDF Table of Contents
    """
    template = ViewPageTemplateFile('../zpt/pdf.toc.pt')

    @property
    def toc_links(self):
        """ Enable Table of contents links
        """
        return True

class BackCover(Cover):
    """ PDF Back Cover
    """
    template = ViewPageTemplateFile('../zpt/pdf.cover.back.pt')


class Body(Cover):
    """ PDF Body
    """
    template = ViewPageTemplateFile('../zpt/pdf.body.pt')

    def __call__(self, **kwargs):

        layout = self.context.getLayout()
        if not layout:
            return self.index()

        try:
            view = self.context.restrictedTraverse(layout)
        except Exception:
            return self.index()

        return view()

class Header(Cover):
    """ PDF Header
    """
    template = ViewPageTemplateFile('../zpt/pdf.header.pt')

class Footer(Cover):
    """ PDF Footer
    """
    template = ViewPageTemplateFile('../zpt/pdf.footer.pt')
