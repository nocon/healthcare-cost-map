from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from cost_map.helpers import get_domain, get_regex
from model import *


def view_processed_links(value):
        #print value
        return value


class AggregatorSpider(CrawlSpider):
    version = 1
    name = 'aggregator'
    count_crawled_pages = 0

    def __init__(self, **kw):
        url = kw.get('url') or kw.get('domain') or\
            'http://localhost:8000/ITERATOR.html'
        print 'Spider approaching ' + get_domain(url)
        self.allowed_domains = [get_domain(url)]
        self.start_urls = [url.replace('ITERATOR', '1')]
        self.domains = dict()
        self.url = url
        if 'ITERATOR' in url:
            self.rules = [(Rule(LinkExtractor(
                allow=(get_regex(url))),
                callback='parse_me',
                follow=True))]
        else:
            self.rules = [(Rule(LinkExtractor(
                allow=()),
                callback='parse_me',
                follow=True))]
        super(AggregatorSpider, self).__init__(**kw)
        # self.cookies_seen = set()

    def parse_me(self, response):
        self.count_crawled_pages += 1
        print 'Spider crawling ' + response.url
        for link in response.xpath('//a/@href').extract():
            if (link.startswith("http") or
                link.startswith("www")) and not\
                    self.allowed_domains[0] in link:
                    domain = get_domain(link)
                    if domain in self.domains:
                        self.domains[domain] += 1
                    else:
                        self.domains[domain] = 1

    def closed(self, reason):
        print 'Spider is hiding the data'
        for domain in self.domains:
            print 'Spider hides ' + str(self.domains[domain]) + ' of ' + domain
            if Provider.select()\
                    .where(Provider.website == domain)\
                    .count() == 0:
                Provider.create(website=domain,
                                source=self.allowed_domains[0],
                                appearance_count=self.domains[domain])
            else:
                provider = Provider.get(Provider.website == domain)
                provider.appearance_count += self.domains[domain]
                provider.save()
        aggregator = Aggregator.get(Aggregator.start_url == self.url)
        aggregator.count_crawled_pages = self.count_crawled_pages
        aggregator.last_crawled_by = self.version
        aggregator.count_found_providers = len(self.domains)
        aggregator.save()
