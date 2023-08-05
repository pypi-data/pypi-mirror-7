import re
import string

from mangopi.helper.util import Util
from mangopi.site.mangasite import MangaSite


class Noez(MangaSite):
    class Chapter(MangaSite.Chapter):
        @property
        def pages(self):
            return [
                self.series.site.Page(self, '{url}/{index}.html'.format(url=self.url, index=index))
                for index in range(1, self.number_of_pages + 1)]

    class Series(MangaSite.Series):
        @property
        def normalized_name(self):
            def fixFormatting(s):
                for i in string.punctuation:
                    s = s.replace(i, " ")
                p = re.compile('\s+')
                s = p.sub(' ', s)
                s = s.lower().strip().replace(' ', '_')
                return s

            return fixFormatting(self.name)

        @property
        def chapters(self):
            ret = [self.site.Chapter(self, Util.unescape(match.group('title') or ''),
                                     match.group('url')) for match in
                   self.CHAPTER_FROM_SOURCE_REGEX.finditer(self.source)]
            ret.reverse()

            return ret
