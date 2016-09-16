import subprocess
import datetime
import os
import urllib
from twisted.internet import reactor


def import_pdf(url):
    os.chdir('/home/radek/Method/CostMap/cost_map/cost_map/pdfs')
    filename = str(datetime.datetime.now())\
        .replace(':', '')\
        .replace(' ', '')\
        .replace('.', '')\
        .replace('-', '')
    urllib.urlretrieve(url, filename + '.pdf')
    #processProtocol = MyProcessProtocol()
    reactor.spawnProcess(None,
                         '/usr/bin',
                         '/home/radek/Method/CostMap/cost_map/cost_map/pdfs',
                         args=['pdftohtml', '-i', '-c', '-noframes',
                               filename + '.pdf', filename + '.html'],
                         env={'HOME': os.environ['HOME']},
                         )
    cmd = 'cd /home/radek/Method/CostMap/cost_map/cost_map/pdfs &&' +\
          ' pdftohtml -i -c -noframes ' +\
          filename + '.pdf ' + filename + '.html'
    subprocess.Popen(cmd, shell=True).wait()
    result = open(filename + '.html', "r").read()
    os.remove(filename + '.html')
    os.remove(filename + '.pdf')
    return result


#print import_pdf("http://www.wapro.pl/wapro/resources/wapro/cennik_WAPRO.pdf")
