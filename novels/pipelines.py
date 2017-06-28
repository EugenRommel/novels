# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import os
from scrapy import log


class FilePipeline(object):
    DATA_DIR = 'data'
    def __init__(self):
        pass

    def process_item(self, item, spider):
        log.msg('Process item: %s' % item, level=log.DEBUG)
        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)
        if item['title'] != '':
            file_name = '%s.txt' % item['title']
            file_path = os.path.join(self.DATA_DIR, file_name)
            log.msg('Writing to file: %s' % file_path)
            with open(file_path, 'a') as f:
                f.write(item['content'])
        return item
