import subprocess
import datetime
import os
from model import *



def find_contents():
    count = 0
    db.connect()
    for content in Content.select().where(Content.format == 'pdf'):
        count += 1
        filename = str(datetime.datetime.now())\
            .replace(':', '')\
            .replace(' ', '')\
            .replace('.', '')\
            .replace('-', '')
        pdf_file = open('local_copies/' + filename + '.pdf', "w")
        pdf_file.write(content.data)
        pdf_file.close()
        cmd = 'cd /home/radek/Method/CostMap/cost_map/local_copies &&' +\
            ' pdftohtml -i -c -noframes ' +\
            filename + '.pdf ' + filename + '.html'
        subprocess.Popen(cmd, shell=True).wait()
        try:
            content.data = open('local_copies/' + filename + '.html', "r").read()
            content.format = 'html'
            os.remove('local_copies/' + filename + '.html')
        except:
            content.format = 'error'
        os.remove('local_copies/' + filename + '.pdf')
        content.save()
    return count


print 'Converted: ' + str(find_contents())
