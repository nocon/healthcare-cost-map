from model import *
from price_finder import PriceFinder
import time


class Qualifier:
    count_scored = 0
    count_searched = 0
    score_threshold = 100

    def score_and_search_pages(self):
        db.connect()
        for page in Page.select().join(Content).where(
                (Page.last_scored_by < PriceFinder.score_version)):
            if page.contents[0].format == 'html':
                self.count_scored += 1
                finder = PriceFinder(page.contents[0].data)
                page.score = finder.score_price_list(page.url)
                page.last_scored_by = PriceFinder.score_version
                print 'Scored ' + str(page.score) + ' (' + page.url + ')'
                # TODO implement content removal for pages with low score
                # to save some disc space
                if page.score > self.score_threshold and\
                        page.last_searched_by < PriceFinder.search_version:
                    self.count_searched += 1
                    prices = finder.find_prices()
                    page.count_found_prices = len(prices)
                    page.last_searched_by = PriceFinder.search_version
                    print 'Found ' + str(len(prices)) + ' (' + page.url + ')'
                    # TODO optimize queries below, as they seem to be slow
                    # delete old prices detected on this page
                    delete = ServicePrice.delete().where(ServicePrice.page == page)
                    delete.execute()
                    for price in prices:
                        price.page = page
                        price.save()
                page.save()

    def search_pages(self):
        for page in Page.select().join(Content).where(
                (Page.last_searched_by < PriceFinder.search_version) &
                (Page.score > self.score_threshold)):
            self.count_searched += 1
            finder = PriceFinder(page.contents[0].data)
            prices = finder.find_prices()
            page.count_found_prices = len(prices)
            page.last_searched_by = PriceFinder.search_version
            print 'Found ' + str(len(prices)) + ' (' + page.url + ')'
            delete = ServicePrice.delete().where(ServicePrice.page == page)
            delete.execute()
            for price in prices:
                price.page = page
                price.save()
            page.save()


a = Qualifier()
start = time.time()
a.score_and_search_pages()
end = time.time()
dif = end - start
print '\nScored: ' + str(a.count_scored) + " Searched: " + str(a.count_searched)
print 'Time: ' + str(dif) + ', ' + str(dif/a.count_scored) + " per record"
print '\n'
