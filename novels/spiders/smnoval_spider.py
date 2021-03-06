from scrapy.contrib.spiders import CrawlSpider
from selenium import webdriver
from novels.platform import get_platform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy import log
from scrapy.http import Request
from novels.items import NovelItem
import re


class SMNovelSpider(CrawlSpider):
    name = 'SMNovel'
    base_url = 'http://www.newsmth.net/nForum/board/Marvel'
    start_urls = [base_url]
    start_urls.extend([base_url + '?p=' + str(i) for i in range(2, 4)])
    platform = get_platform()

    def __init__(self):
        CrawlSpider.__init__(self)
        if self.platform == 'win':
            self.driver = webdriver.PhantomJS(executable='d:/phantomjs/bin/phantomjs.exe')
        elif self.platform == 'linux':
            self.driver = webdriver.PhantomJS()

        self.driver.set_page_load_timeout(120)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.quit()

    def parse_content(self, url):
        try:
            self.driver.get(url)
            element = WebDriverWait(self.driver, 60).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            log.msg('element:%s' % element, level=log.DEBUG)
        except Exception as e:
            log.msg('Wait failed due to exception: %s' % e, level=log.ERROR)
        page_source = self.driver.page_source
        bs_obj = BeautifulSoup(page_source, "lxml")
        log.msg('bs_obj: %s' % bs_obj, level=log.DEBUG)
        contents = bs_obj.find_all('td', class_='a-content')
        contents = [content.p.get_text().encode('utf-8', 'ignore') for content in contents]
        pagination = bs_obj.find('ul', class_='pagination')
        log.msg('pagination: %s' % pagination, level=log.DEBUG)
        page_pre = pagination.find('li', class_='page-pre')
        art_count = page_pre.i.get_text()
        log.msg('Art count: %s' % art_count, level=log.DEBUG)
        next_requests = []
        if not re.match(r'\?p=\d+$', url):
            for i in range(2, int(art_count) / 10 + 2):
                next_url = '%s?p=%d' % (url, i)
                log.msg('Next URL: %s' % next_url, level=log.DEBUG)
                next_requests.append(Request(next_url, callback=self.parse))
        log.msg('art_count: %s' % art_count, level=log.DEBUG)
        return ('\n'.join(contents), next_requests)

    def parse(self, response):
        self.driver.get(response.url)
        log.msg('Response URL: %s' % response.url, level=log.INFO)
        try:
            element = WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'table'))
            )
            log.msg('element:%s' % element, level=log.DEBUG)
        except Exception as e:
            log.msg('Wait failed due to exception: %s' % e, level=log.ERROR)

        page_source = self.driver.page_source
        bs_obj = BeautifulSoup(page_source, 'lxml')
        #log.msg("bs_obj: %s" % bs_obj, level=log.DEBUG)
        table = bs_obj.find('table', class_='board-list tiz')
        log.msg('Table: %s' % table, level=log.DEBUG)
        noval_chaps = table.find_all('tr', class_=False)
        for noval_chap in noval_chaps:
            log.msg('noval_chap: %s' % noval_chap, level=log.DEBUG)
            title = ''
            href = ''
            td_9 = noval_chap.find('td', class_='title_9')
            log.msg('td_9: %s' % td_9, level=log.DEBUG)
            if td_9:
                title = td_9.a.get_text().encode('utf-8', 'ignore')
                href = td_9.a['href']
                log.msg('Title: %s' % title, level=log.DEBUG)
                item = NovelItem()
                item['title'] = title
                root_url = 'http://www.newsmth.net'
                if href != '':
                    content, requests = self.parse_content(root_url + href)
                    item['content'] = content
                    log.msg('Content: %s' % content, level=log.DEBUG)
                    yield item

                    for request in requests:
                        yield request

