from __future__ import absolute_import
from lxml.html import fromstring, HTMLParser
from lxml.cssselect import CSSSelector
from urlparse import urljoin
import re

from grab import DataNotFound


REX_NUMBER = re.compile(r'\d+')

class Extension(object):
    export_attributes = ['tree', 'follow_link', 'xpath', 'itercss', 'css', 'css_text', 'css_number']

    def extra_reset(self, grab):
        grab._lxml_tree = None

    @property
    def tree(self):
        if self._lxml_tree is None:
            parser = HTMLParser(encoding=self.config['charset'])
            self._lxml_tree = fromstring(self.response.body, parser=parser)
        return self._lxml_tree

    def follow_link(self, anchor=None, href=None):
        """
        Find link and follow it.
        """

        if anchor is None and href is None:
            raise Exception('You have to provide anchor or href argument')
        self.tree.make_links_absolute(self.config['url'])
        for item in self.tree.iterlinks():
            if item[0].tag == 'a':
                found = False
                text = item[0].text or u''
                url = item[2]
                # if object is regular expression
                if anchor:
                    if hasattr(anchor, 'finditer'):
                        if anchor.search(text):
                            found = True
                    else:
                        if text.find(anchor) > -1:
                            found = True
                if href:
                    if hasattr(href, 'finditer'):
                        if href.search(url):
                            found = True
                    else:
                        if url.startswith(href) > -1:
                            found = True
                if found:
                    url = urljoin(self.config['url'], item[2])
                    return self.request(url=item[2])
        raise DataNotFound('Cannot find link ANCHOR=%s, HREF=%s' %\
                           (anchor, href))

    def xpath(self, path, filter=None):
        """
        Shortcut to ``self.tree.xpath``.
        """

        items = self.tree.xpath(path)
        if filter:
            return [x for x in items if filter(x)]
        else:
            return items 

    def css(self, path):
        """
        Shortcut to lxml.cssselect.

        Return first element

        Documentation: http://lxml.de/cssselect.html
        """

        return self.itercss(path)[0]

    def itercss(self, path):
        """
        Shortcut to lxml.cssselect

        Documentation: http://lxml.de/cssselect.html
        """

        sel = CSSSelector(path)
        return sel(self.tree)


    def css_text(self, path):
        """
        Extract text of first element found by css path.
        """

        return self.css(path).text_content().strip()


    def css_number(self, path):
        """
        Find number in text of first element found by css path.
        """

        sel = CSSSelector(path)
        return REX_NUMBER.search(self.css_text(path)).group(0)
