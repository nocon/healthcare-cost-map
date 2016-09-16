# -*- coding: utf-8 -*-

from peewee import *
import datetime
import sys;
reload(sys);
sys.setdefaultencoding("utf8")

db = MySQLDatabase('cost_map', user='cost')


class BaseModel(Model):
    class Meta:
        database = db


class Aggregator(BaseModel):
    starting_point = CharField()
    count_found_providers = IntegerField()
    last_crawled_by = IntegerField()
    count_crawled_pages = BigIntegerField()


class Provider(BaseModel):
    website = CharField()
    source = CharField()
    language = CharField()
    last_crawled_by = IntegerField()
    appearance_count = IntegerField()
    do_not_crawl = BooleanField()
    count_crawled_pages = BigIntegerField()
    time_found = DateTimeField()
    count_errors = IntegerField()


class Page(BaseModel):
    provider = ForeignKeyField(Provider, related_name='pages',
                               on_delete='CASCADE')
    url = CharField()
    count_found_prices = IntegerField()
    score = IntegerField()
    last_scored_by = IntegerField()
    last_searched_by = IntegerField()
    time_found = DateTimeField()


class Service(BaseModel):
    name = CharField()


class ServiceName(BaseModel):
    name = CharField()
    language = CharField()
    service = ForeignKeyField(Service, related_name='names')
    score = IntegerField()


class DiscardedDomain(BaseModel):
    name = CharField()


class Content(BaseModel):
    format = CharField()
    data = BlobField()
    page = ForeignKeyField(Page, related_name='contents', on_delete='CASCADE')


class WorkLog(BaseModel):
    tool_name = CharField()
    tool_version = IntegerField()
    time_started = DateTimeField()
    duration = IntegerField()
    count_processed = IntegerField()
    count_errors = IntegerField()


class ServicePrice(BaseModel):
    service_name = ForeignKeyField(ServiceName, related_name='prices')
    page = ForeignKeyField(Page, related_name='prices')
    service_name = CharField()
    score = IntegerField()
    min_price = DecimalField()
    med_price = DecimalField()
    max_price = DecimalField()
    text = CharField()
    code = CharField()
    unit = CharField()
    time_found = DateTimeField()
    last_matched_by = IntegerField()
    match_score = IntegerField()

    def __str__(self):
        result = u'NAME: ' + str(self.service_name)
        if self.min_price is not None:
            result += u'\nMIN: ' + str(self.min_price)
        if self.med_price is not None:
            result += u'\nMED: ' + str(self.med_price)
        if self.max_price is not None:
            result += u'\nMAX: ' + str(self.max_price)
        if self.unit is not None:
            result += u'\nUNIT: ' + str(self.unit)
        if self.code is not None:
            result += u'\nCODE: ' + str(self.code)
        return result


# Class optimised for reading. Main class accessed by the map UI.
class ServicePriceRO(BaseModel):
    min_price = DecimalField()
    med_price = DecimalField()
    max_price = DecimalField()


# This class represents request for human action.
class ManualActionRequest(BaseModel):
    action = CharField()
    time_requested = DateTimeField(default=datetime.datetime.now())
    priority = IntegerField(default=0)
    item_type = CharField()
    item_id = IntegerField()
