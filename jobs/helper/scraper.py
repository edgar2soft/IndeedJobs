# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import traceback
from webdriver_manager.chrome import ChromeDriverManager
import requests
from selenium.common.exceptions import NoSuchElementException
import random
from ..models import Job, Query
from django.db.utils import OperationalError


class scraper_indeed:

    def __init__(self):
        self.driver = self.__get_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()

        return True

    def get_account(self, url):
        self.driver.get(url)
        link_list = self.__scrape_job_links(self.driver, url)
        new_jobs = self.__save_jobs(self.driver, link_list)
        return new_jobs

    def __get_driver(self, debug=False):
        options = Options()
        #if not debug:
        options.add_argument("--headless")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        input_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        return input_driver

    def __scrape_job_links(self, driver, url):
        urls = []
        query = Query.objects.all()[0].query
        for page in range(1):

            i_url = url + "&start={}".format(page * 10)
            driver.get(i_url)
            link_list = driver.find_elements_by_xpath("//div[@class='title']/a")

            for link in link_list:
                try:
                    sel_job = Job.objects.filter(href=link.get_attribute('href'), query=query).first()
                    if sel_job != None:
                        continue
                except Job.DoesNotExist:
                    pass
                urls.append(link.get_attribute('href'))

            time.sleep(random.random() + random.randint(6, 10))

        urls_reverse = []
        for i in range(len(urls)):
            urls_reverse.append(urls[len(urls) - 1 - i])
        return urls_reverse

    def __save_jobs(self, driver, urls):
        jobs = []

        for url in urls:
            job = {}
            #print(url)
            driver.get(url)

            job['href'] = url

            time.sleep(random.random() + random.randint(6, 11))
            try:
                job['title'] = driver.find_element_by_xpath("//div[@class='jobsearch-DesktopStickyContainer']/"
                                                            "div[@class='jobsearch-JobInfoHeader-title-container']/"
                                                            "h3").text
            except NoSuchElementException:
                time.sleep(random.random() + random.randint(6, 11))
                job['title'] = driver.find_element_by_xpath("//div[@class='jobsearch-DesktopStickyContainer']/"
                                                            "div[@class='jobsearch-JobInfoHeader-title-container']/"
                                                            "h3").text

            try:
                job['cn'] = driver.find_element_by_xpath("//div[@class='jobsearch-DesktopStickyContainer']/"
                                                         "div/div/div/div/a[@target='_blank']").text
            except NoSuchElementException:
                job['cn'] = driver.find_element_by_xpath("//div[@class='jobsearch-DesktopStickyContainer']/"
                                                         "div/div/div/div").text

            try:
                job['crv'] = driver.find_element_by_xpath("//meta[@itemprop='ratingValue']").get_attribute('content')
                job['crc'] = driver.find_element_by_xpath("//meta[@itemprop='ratingCount']").get_attribute('content')
            except NoSuchElementException:
                job['crv'] = ''
                job['crc'] = ''
                pass

            div_list = driver.find_elements_by_xpath("//div[@class='jobsearch-DesktopStickyContainer']/"
                                                     "div/div/div/div")
            print("lenth = {}".format(len(div_list)))

            if div_list[len(div_list) - 2].text != "Apply On Company Site":
                job['loc'] = div_list[len(div_list) - 2].text
            else:
                job['loc'] = div_list[len(div_list) - 4].text
            if "Responded to" in div_list[len(div_list) - 2].text:
                job['loc'] = div_list[len(div_list) - 3].text

            if job['cn'] == "":
                job['cn'] = div_list[0].text


            try:
                job['metaheader'] = driver.find_element_by_xpath("//div[@class='jobsearch-JobMetadataHeader-item ']").text
            except NoSuchElementException:
                job['metaheader'] = ''
                pass

            job['desc'] = driver.find_element_by_xpath("//div[@class='jobsearch-jobDescriptionText']").text
            #print(job)

            jobs.append(job)

        query = Query.objects.all()[0].query
        for i in jobs:
            try:
                sel_job = Job.objects.filter(query=query, title=i['title'], cn=i['cn'], crv=i['crv'], crc=i['crc'],
                                             loc=i['loc'], metaheader=i['metaheader'], desc=i['desc']).first()
                if sel_job != None:
                    sel_job.href = i['href']
                    sel_job.save()
                    continue
            except Job.DoesNotExist:
                pass

            p = Job(query=query, href=i['href'], title=i['title'], cn=i['cn'], crv=i['crv'], crc=i['crc'],
                    loc=i['loc'], metaheader=i['metaheader'], desc=i['desc'])
            p.save()
        return jobs