# Scrapy settings for novels project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'novels'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['novels.spiders']
NEWSPIDER_MODULE = 'novels.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
ITEM_PIPELINES = {
    'novels.pipelines.FilePipeline': 300
}

