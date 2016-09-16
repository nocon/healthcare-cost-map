from model import *
import time
import datetime

class Matchmaker():
    version = 1
    count_matched = 0
    count_processed = 0
    count_errors = 0

    # This match will try to guess service names based on occurence of phrase
    # in price records. It is not meant to be used to qualify every price point
    # - only to discover new service names. It requires manual verification.
    def duplicate_match(self):
        for service_prices in ServicePrice\
                .select(ServicePrice, fn.Count(ServicePrice.id).alias('count'))\
                .where(ServicePrice.servicename_id >> None)\
                .group_by(ServicePrice.service_name)\
                .having(fn.count(ServicePrice.id) > 2):
            name = service_prices.service_name
            print service_prices.count
            try:
                service = ServiceName.get(ServiceName.name == name.lower())
                assign_id = service.id
            except:
                new_service = ServiceName()
                new_service.name = name.lower()
                new_service.save()
                assign_id = new_service.id

                request = ManualActionRequest()
                request.item_type = "servicename"
                request.item_id = new_service.id
                request.priority = count
                request.save()
            query = "UPDATE serviceprice SET servicename_id = "\
                    + str(assign_id) + " WHERE servicename_id IS NULL\
                           AND service_name = %s"
            db.execute_sql(query, (name,))
            # TODO: Try to get the count of updated items, update counts

    # Try to match each unmatched record against existing database of service
    # names
    # TODO: When language detection is supported, match only agaist same
    # language.
    def match_against_list(self):
        a = 3


tool = Matchmaker()
start_datetime = datetime.datetime.now()
start = time.time()
tool.duplicate_match()
tool.match_against_list()
end = time.time()
dif = end - start
print '\nMatched: ' + str(tool.count_matched)
print 'Time: ' + str(dif)
if tool.count_processed > 0:
    print 'Performance: ' + str(dif/tool.count_processed) + " per record"
print '\n'
log = WorkLog()
log.tool_name = tool.__class__.__name__
log.tool_version = tool.version
log.time_started = start_datetime
log.duration = dif
log.count_processed = tool.count_processed
log.count_errors = tool.count_errors
log.save()
