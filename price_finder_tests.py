import unittest
from price_finder import PriceFinder
import os
import re


class PriceFinderTests(unittest.TestCase):

    def setUp(self):
        self.price_lists = dict()
        for f in os.listdir("cost_map/price_lists/examples"):
            if 'html' in f:
                self.price_lists["cost_map/price_lists/examples/" + f]\
                      = int(''.join(c for c in f if c.isdigit()))

    def test_detection(self):
        print '\nDETECTION:'
        for k, v in self.price_lists.iteritems():
            print k
            a = PriceFinder(open(k, "r").read())
            count = len(a.find_prices())
            self.assertEqual(count, v)

    def test_identification(self):
        print '\nIDENTIFICATION:'
        for k, v in self.price_lists.iteritems():
            print k
            a = PriceFinder(open(k, "r").read())
            self.assertTrue(a.is_a_price_list())

if __name__ == '__main__':
    unittest.main()
