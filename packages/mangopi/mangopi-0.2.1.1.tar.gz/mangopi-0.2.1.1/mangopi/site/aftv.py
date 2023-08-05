import re

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from mangopi.helper.decorators import memoize
from mangopi.helper.util import Util
from mangopi.site.mangasite import MangaSite


class Aftv(MangaSite):
    class Chapter(MangaSite.Chapter):
        @property
        def volume(self):
            return None

        @property
        def pages(self):
            if self.url.endswith('.html'):
                page_base_url = re.sub('(\d+)-(\d+)-(\d+)', '\\1-\\2-{index}', self.url)
            else:
                page_base_url = self.url + '/{index}'

            return [self.series.site.Page(self, page_base_url.format(index=index)) for index in
                    range(1, self.number_of_pages + 1)]

    class Series(MangaSite.Series):
        CHAPTER_FROM_SOURCE_REGEX = re.compile(
            '<a href="(?P<path>[^"]*)">[^<]*</a>[^:]*: (?P<title>[^<]*)</td>')

        class Metadata(object):
            def __init__(self, name1, picture_link, name2, author_name, path, id):
                self.name = name1
                self.picture_link = picture_link
                self.author_name = author_name
                self.path = path
                self.id = id

        @property
        def normalized_name(self):
            return self.metadata.name

        @property
        def chapters(self):
            ret = [self.site.Chapter(self, Util.unescape(match.group('title') or ''),
                                     self.TEMPLATE_URL.format(path=match.group('path'))) for match
                   in self.CHAPTER_FROM_SOURCE_REGEX.finditer(self.source)]

            return ret

        @property
        def url(self):
            return self.TEMPLATE_URL.format(path=self.metadata.path)

        @property
        @memoize
        def metadata(self):
            url = self.TEMPLATE_URL.format(
                path=('/actions/search/?q={name}'.format(name=self.name.replace(' ', '+'))))

            lines = urllib2.urlopen(url)
            first_result = str(lines.readline())

            return self.Metadata(*first_result.split('|'))
