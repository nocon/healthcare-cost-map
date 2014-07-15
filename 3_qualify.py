from model import *
from price_finder import PriceFinder
import time


class Qualifier:
    count_qualified = 0
    count_searched = 0

    def qualify_pages(self):
        db.connect()
        for page in Page.select().join(Content).where(
                (Page.last_scored_by < PriceFinder.score_version)):
            if page.contents[0].format == 'html':
                self.count_qualified += 1
                finder = PriceFinder(page.contents[0].data)
                page.score = finder.score_price_list(page.url)
                page.last_scored_by = PriceFinder.version
                print page.url + " : " + str(page.score)
                # TODO implement content removal for pages with low score
                # to save some disc space
                if page.score > 100 and\
                    page.last_searched_by < PriceFinder.finder_version:
                    self.count_searched += 1
                    prices = finder.find_prices()
                    page.count_found_prices = len(prices)
                    page.last_searched_by = PriceFinder.version
                    # TODO optimize queries below, as they seem to be slow
                    # delete old prices detected on this page
                    delete = ServicePrice.delete().where(ServicePrice.page == page)
                    delete.execute()
                    for price in prices:
                        price.page = page
                        price.save()
                page.save()

a = Qualifier()
start = time.time()
a.qualify_pages()
end = time.time()
dif = end - start
print '\nQualified: ' + str(a.count_qualified) + " Searched: " + str(a.count_searched)
print 'Time: ' + str(dif) + ', ' + str(dif/a.count_qualified) + " per record"
print '\n'
