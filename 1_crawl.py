from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from cost_map.spiders.aggregator_spider import AggregatorSpider
from cost_map.spiders.provider_spider import ProviderSpider
from scrapy.utils.project import get_project_settings
from model import *


class SpiderNest():

    count = 0

    def release_the_spiders(self):
        db.connect()
        # for aggregator in Aggregator.select().where(
        #         Aggregator.last_crawled_by < AggregatorSpider.version):
        #     spider = AggregatorSpider(domain=aggregator.starting_point)
        #     settings = get_project_settings()
        #     crawler = Crawler(settings)
        #     crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        #     crawler.configure()
        #     crawler.crawl(spider)
        #     crawler.start()
        
        for provider in Provider.select().where(
                (Provider.language == 'pl') &
                (Provider.last_crawled_by < ProviderSpider.version) &
                (Provider.do_not_crawl == 0)).limit(10):
            self.count += 1
            spider = ProviderSpider(provider=provider)
            settings = get_project_settings()
            crawler = Crawler(settings)
            crawler.signals.connect(self.stop, signal=signals.spider_closed)
            crawler.signals.connect(self.error, signal=signals.spider_error)
            crawler.configure()
            crawler.crawl(spider)
            crawler.start()
        if self.count > 0:
            reactor.run()
        print 'Spiders have finished.'

    def stop(self):
        self.count -= 1
        if self.count == 0:
            reactor.stop()

    def error(failure, response, spider):
        spider.provider.count_errors += 1

nest = SpiderNest()
nest.release_the_spiders()
