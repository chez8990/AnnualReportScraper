
from __future__ import absolute_import
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import scrapy
import os
import pandas as pd
import time
import requests


class ReportSpider(scrapy.Spider):
    name = "report_spider"
    allowed_domains = ['hkexnews.hk']
    start_urls = ['https://www.hkexnews.hk/index.htm']

    def __init__(self):
        parent_dir = os.path.abspath(os.path.join(__file__, "../.."))

        self.companies = pd.read_csv(os.path.join(parent_dir, 'data', 'companies.csv'))
        self.save_path = os.path.join(parent_dir, 'data')

        options = webdriver.ChromeOptions()

        options.add_argument("--no-sandbox");
        options.add_argument("--disable-dev-shm-usage");
        self.driver = webdriver.Chrome(os.path.join(parent_dir, 'driver', 'chromedriver'), options=options)

    def parse(self, response):
        for _, stock in self.companies.iterrows():
            self.driver.get(self.start_urls[0])
            time.sleep(3)

            query = str(stock['Stock Code']).zfill(5)

            elem = self.driver.find_element_by_xpath('//*[@id="searchStockCode"]')
            elem.clear()
            elem.send_keys(query)

            time.sleep(2)

            self.driver.find_element_by_xpath('//*[@id="autocomplete-list-0"]/div[1]/div[1]/table/tbody/tr[1]').click()
            elem.submit()

            time.sleep(3)
            load_more = self.driver.find_element_by_xpath('//*[@id="recordCountPanel2"]/div[1]/div/div[1]/ul/li/a')

            while load_more is not None:
                load_more.click()
                time.sleep(2)
                try:
                    load_more = self.driver.find_element_by_xpath('//*[@id="recordCountPanel2"]/div[1]/div/div[1]/ul/li/a')
                except:
                    break

            source = self.driver.page_source
            bsobj = bs(source, 'html.parser')
            result_docs = bsobj.findAll('div', attrs={'class': 'doc-link'})

            reports_links = []
            reports_names = []

            for row in result_docs:
                if 'annual report' in row.text.lower():
                    reports_links.append(row.a.get('href'))
                    reports_names.append(row.a.text)

            for link, name in zip(reports_links, reports_names):
                pdf_name = link.split('/')[-1]

                # check if stock directory exists
                if not os.path.isdir(os.path.join(self.save_path, query)):
                    os.mkdir(os.path.join(self.save_path, query))

                # download the reports pdf
                try:
                    response = requests.get('https://www1.'+self.allowed_domains[0]+link)
                    with open(os.path.join(self.save_path, query, name+'.pdf'), 'wb') as f:
                        f.write(response.content)
                except:
                    pass

