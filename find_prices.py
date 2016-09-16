from price_finder import PriceFinder
import os

os.system('clear')
a = PriceFinder(open("cost_map/price_lists/examples/9.html", "r").read())
a.verbose = True
if a.is_a_price_list():
    a.find_prices()
for warning in a.warnings:
    print warning
