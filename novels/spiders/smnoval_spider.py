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

        self.driver.set_page_load_timeout(40)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.driver.quit()

    def parse_content(self, url):
        try:
            self.driver.get(url)
            element = WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
            log.msg('element:%s' % element, level=log.DEBUG)
        except Exception as e:
            log.msg('Wait failed due to exception: %s' % e, level=log.ERROR)
        page_source = self.driver.page_source
        bs_obj = BeautifulSoup(page_source, "lxml")
        return bs_obj.find('td', class_='a-content').p.get_text().encode('utf-8', 'ignore')

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
        tables = bs_obj.find_all('table', class_='board-list tiz')
        log.msg('Tables length %d: %s' % (len(tables), tables), level=log.DEBUG)
        for table in tables:
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
                        content = self.parse_content(root_url + href)
                        item['content'] = content
                        log.msg('Content: %s' % content, level=log.DEBUG)
                        yield item

                td_10s = noval_chap.find_all('td', class_='title_10')
                for td_10 in td_10s:
                    log.msg('td_10: %s' % td_10, level=log.DEBUG)
                    try:
                        td_10_attr = td_10.a
                        if not td_10_attr:
                            continue
                        current_page_url = td_10.a['href']
                        if current_page_url != '':
                            log.msg('Current url: %s' % current_page_url)
                            m = re.match(r'(?P<base_url>.+p=)(?P<page_num>\d+)#a0$', current_page_url)
                            if m:
                                next_page = int(m.group('page_num')) + 1
                                base_url = m.group('base_url')
                                next_url = "%s%d" % (base_url, next_page)
                                log.msg('Next url: %s' % next_url, level=log.DEBUG)
                                yield Request(root_url + next_url, callback=self.parse)
                    except AttributeError as e:
                        log.msg('Ignore td class has no href', level=log.INFO)






