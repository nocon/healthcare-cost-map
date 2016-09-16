# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class MedicalFacilityItem(scrapy.Item):
    service = scrapy.Field()
    min_price = scrapy.Field()
    med_price = scrapy.Field()
    max_price = scrapy.Field()
    pass


class AggregatorItem(scrapy.Item):
    website = scrapy.Field()
    pass
