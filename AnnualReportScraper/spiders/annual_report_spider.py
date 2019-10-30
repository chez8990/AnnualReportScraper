import scrapy
import pandas as pd
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver

class ReportSpider:
    name = "report_spider"
    allowed_domains = ['hkexnews.hk']
    start_urls = ['https://www.hkexnews.hk/index.htm']

    def __init__(self):
        self.companies = pd.read_csv('../../companies.csv')
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(response.url)

        for _, stock in self.companies.iterrows():

            query = stock['Stock Code']
            query = query.iloc[0]

            elem = self.driver.find_element_by_xpath('//*[@id="searchStockCode"]')
            elem.clear()
            elem.send_keys(query)

            time.sleep(2)

            self.driver.find_element_by_xpath('//*[@id="autocomplete-list-0"]/div[1]/div[1]/table/tbody/tr[1]').click()
            self.driver.find_element_by_xpath('//*[@id="date-picker"]/div[1]/b[1]/ul/li[21]/button').click()
            elem.submit()

            time.sleep(3)
            load_more = self.driver.find_element_by_xpath('//*[@id="recordCountPanel2"]/div[1]/div/div[1]/ul/li/a')

            while load_more is not None:
                load_more.click()
                time.sleep(4)
                load_more = self.driver.find_element_by_xpath('//*[@id="recordCountPanel2"]/div[1]/div/div[1]/ul/li/a')

            source = self.driver.page_source
            bsobj = bs(source, 'html.parser')
            result_docs = bsobj.findAll('div', attrs={'class': 'doc-link'})

            reports_links = []

            for row in result_docs:
                if 'annual report' in row.text.lower():
                    reports_links.append(row.a.get('href'))

            return reports_links

