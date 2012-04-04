# Scrapy settings for tripcrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'tripcrawler'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['tripcrawler.spiders']
NEWSPIDER_MODULE = 'tripcrawler.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

