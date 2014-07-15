# -*- coding: utf-8 -*-

from model import *
from bs4 import BeautifulSoup as BS
from cost_map.helpers import get_decimal, is_a_phone_number, count_digits, replace_insensitive, remove_format_characters
import re
import decimal


class PriceFinder:
    version = 4
    from_translations = [u"from", u"от", u"od"]
    to_translations = [u"to", u"до", u"do"]
    date_translations = [u"year", u"roku", u"года"]
    time_translations = [u"min", u"minute", u"minut"]
    per_translations = [u"per", u"za", u"за", u'/']
    currencies = [u"EUR", u"GBP", u"£", u"€", u"zl", u"zł", u"USD", u"PLN"]
    prices = [u"price", u"cena", u"cennik"]
    hour_abbreviations = [u"p.h."]
    #BESPOKE
    banned_from_price = [u"level"]

    def __init__(self, text):
        self.soup = BS(text)
        self.verbose = False
        self.warnings = set()
        #BESPOKE to medicine
        if 'CPT' in self.soup.text:
            self.special_code_format = r"\d{5}$"
        else:
            self.special_code_format = ''

    # TODO Implement
    # Fast method to determine if a given text is a price list.
    # Depending on result, find_prices may follow up.
    def score_price_list(self, url):
        score = 0
        for tag in self.soup.findAll(["title", "h1", "h2", "h3"]):
            for price in self.prices:
                if price.upper() in tag.text.upper():
                    score += 100
        for price in self.prices:
                if price.upper() in url.upper():
                    score += 100
        for currency in self.currencies:
            if currency.upper() in self.soup.text.upper():
                score += 10
        score += count_digits(self.soup.text) / len(self.soup.text) * 100
        return score

    def find_prices(self):
        prices = list()
        previous_tag = None
        code = None
        # Go through all potential service names, and look
        # for price next to them
        for tag in self.soup.findAll(["div", "p", "td", "span"]):
            #Search only bottom level tags
            lengths = [len(i.text) for i in
                       tag.findChildren(["div", "p", "td", "span"])]
            if sum(lengths) == 0:
                if self.special_code_format != '' and\
                        self.is_a_special_code(tag.text):
                    code = tag.text.strip()
                    #print repr(code)
                elif self.is_a_price(tag.text) and\
                        previous_tag is not None and\
                        previous_tag.text.strip is not '':
                    price = self.determine_the_price(tag.text)
                    if not price is None:
                        price.service_name = previous_tag.text.strip()
                        price.text = previous_tag.text + ' &&&& ' + tag.text
                        price.code = code
                        prices.append(price)
                        previous_tag = None
                        code = None
                        if self.verbose is True:
                            print ""
                            print repr(price.text)
                            print str(price)
                elif len(remove_format_characters(tag.text)) > 0:
                    #print repr(tag.text)
                    previous_tag = tag
        print 'Found: ' + str(len(prices)) + ' prices'
        return prices

    def is_a_special_code(self, text):
        return re.search(self.special_code_format, text)

    # Fast method to determine if a given text is a price.
    # Depending on result, determine_the_price may follow.
    def is_a_price(self, text):
        a = text.replace(' ', '').replace(u"\xa0", '')\
            .replace('\r', '').replace('\n', '').replace('\t', '').upper()

        if len(a) == 0:
            return False

        if len(a) > 30:
            return False

        if is_a_phone_number(text):
            #TODO - save the phone number for Provider
            return False

        if self.is_a_date(text):
            return False

        if self.is_time(text):
            return False

        if count_digits(a) / len(a) < 0.1:
            return False

        # This rule was created to combat price detection on
        # Malarone 250/100mg tablets
        if '/' in a and any(c.isalpha() for c in a.split('/')[0]):
            self.warnings.add('/ rule executed on ' + text)
            return False

        # This rule is supposed to deal with 'word, ' occurences
        for i, c in enumerate(a):
            if c == ',' and i > 0 and not a[i-1].isdigit():
                return False

        # Last resort rule
        if self.is_banned(text):
            return False

        return True

    def determine_the_price(self, text):
        # remove white space
        a = remove_format_characters(text)

        # handle 'from' occurences
        contains_from = False
        for from_translation in self.from_translations:
            if from_translation.upper() in a.upper():
                contains_from = True

        # handle 'to' occurences
        for to_translation in self.to_translations:
            a = replace_insensitive(a, to_translation, '-')

        # handle 'per occurences'
        price_unit = None
        for per_translation in self.per_translations:
            if per_translation.upper() in a.upper():
                price_unit = a.lower().split(per_translation.lower(), 1)[1]\
                              .strip()

        # handle hour abbreviations
        for abbreviation in self.hour_abbreviations:
            if abbreviation.upper() in a.upper():
                price_unit = "hour"
                a = a.replace(abbreviation, '')

        # remove meaningless characters
        a = filter(lambda x: x.isdigit() or x == '-'
                   or x == ',' or x == '.' or x == '+', a)

        # prepare price object
        price = ServicePrice()
        try:
            if '-' in a:
                prices = a.split('-')
                price.min_price = get_decimal(prices[0])
                price.max_price = get_decimal(prices[1])
            elif '+' in a:
                prices = a.split('+')
                price.med_price = get_decimal(prices[0])+get_decimal(prices[1])
            else:
                if contains_from:
                    price.min_price = get_decimal(a)
                else:
                    price.med_price = get_decimal(a)
            price.unit = price_unit
            return price
        except:
            return None

    def is_a_date(self, text):
        for translation in self.date_translations:
            if translation.upper() in text.upper():
                return True
        return False

    def is_banned(self, text):
        for translation in self.banned_from_price:
            if translation.upper() in text.upper():
                self.warnings.add("Ban rule applied on " + text)
                return True
        return False

    def is_time(self, text):
        # Time is acceptable only as a unit, hence 'per' check        
        for per_translation in self.per_translations:
            if per_translation.upper() in text.upper():
                return False

        for translation in self.time_translations:
            if translation.upper() in text.upper():
                self.warnings.add("Time rule applied on " + text)
                return True
        return False
