# Scrapy settings for cost_map project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cost_map'

SPIDER_MODULES = ['cost_map.spiders']
NEWSPIDER_MODULE = 'cost_map.spiders'
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware': 1,
    'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 2,
}
DOWNLOAD_TIMEOUT = 10
DEPTH_LIMIT = 5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cost_map (+http://www.yourdomain.com)'
