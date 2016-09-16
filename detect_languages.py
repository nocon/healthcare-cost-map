import simplejson as json
import sys
import grequests

from model import *

db.connect()

limit = 30

rs = []
ids = []
urls = []
for provider in Provider.select().where((Provider.language >> None) &
                                        (Provider.do_not_crawl == 0)).limit(limit):
    rs.append(grequests.post(
        'http://textalytics.com/core/lang-1.1',
        data='key=bbbfc287834611e955c3c131c2e55345&of=json&txt=&url='
        + provider.website))
    ids.append(provider.id)
    urls.append(provider.website)

responses = grequests.map(rs)

for i in range(limit):
    print i
    provider = Provider.get(Provider.id == ids[i])
    try:
        print urls[i]
        print responses[i].content
        response = json.loads(responses[i].content)
        if response['status']['msg'] == 'OK':
            provider.language = response['lang_list'][0]
            print provider.website + ': ' + response['lang_list'][0]
    except:
        provider.language = 'ERROR'
        print sys.exc_info()
    provider.save()
