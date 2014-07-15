from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from model import *
from cost_map.helpers import get_domain
import datetime


class ProviderSpider(CrawlSpider):
    version = 26
    name = 'provider'

    def __init__(self, **kw):
        self.provider = kw.get('provider')
        self.provider.count_crawled_pages = 0
        self.pages = list()
        self.contents = list()
        url = self.provider.website
        print 'Spider approaching ' + url
        self.url = url
        self.allowed_domains = [get_domain(url)]
        self.start_urls = ['http://' + url]
        self.rules = [
            Rule(LinkExtractor(
                 allow=(),
                 deny_extensions=['mng', 'pct', 'bmp', 'gif', 'jpg',
                                  'jpeg', 'png', 'pst', 'psp', 'tif',
                                  'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps',
                                  'svg', 'mp3', 'wma', 'ogg', 'wav', 'ra',
                                  'aac', 'mid', 'au', 'aiff', '3gp', 'asf',
                                  'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt',
                                  'rm', 'swf', 'wmv', 'm4a', 'css', 'doc',
                                  'exe', 'bin', 'rss', 'zip', 'rar']),
                 callback='parse_me',
                 follow=True,
                 )
            ]
        super(ProviderSpider, self).__init__(**kw)
        # TODO: Make this crawler look like normal browser (delays, user agent)

    def parse_me(self, response):
        # print 'Spider is crawling ' + response.url
        self.provider.count_crawled_pages += 1
        ct = response.headers.get("content-type", "").lower()
        page = Page()
        page.provider = self.provider
        page.url = response.url
        page.time_found = datetime.datetime.now()
        content = Content()
        content.data = response.body
        if "pdf" in ct:
            content.format = "pdf"
            #TODO implement PDF conversion here
        else:
            content.format = "html"
        self.pages.append(page)
        self.contents.append(content)

    def closed(self, reason):
        print 'Spider has crawled ' + self.provider.website\
            + ' and found ' + str(len(self.pages)) + ' pages'
        if len(self.pages) > 0:
            # wipe or archive old pages and their contents
            delete = Page.delete().where(Page.provider == self.provider)
            delete.execute()
            self.provider.last_crawled_by = self.version
            self.provider.save()
            for i, item in enumerate(self.pages):
                self.pages[i].save()
                self.contents[i].page = self.pages[i]
                self.contents[i].save()
