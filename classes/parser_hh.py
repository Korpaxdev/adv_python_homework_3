from json import dump
from re import compile, IGNORECASE, Pattern
from time import sleep
from typing import AnyStr

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from fake_useragent import FakeUserAgent
from requests import get


class ParserHH:
    def __init__(self, url: str, keywords: list[str]):
        self.url = url
        user_agent = FakeUserAgent().chrome
        self.__headers = {'User-Agent': user_agent}
        self.__pattern = self.__create_pattern(keywords)
        self.posts = []

    def parse_all_pages(self):
        body = self.__get_bs4_body(self.url)
        total_pages = self.__get_total_pages(body)
        for page in range(total_pages):
            print('-' * 5, f'Страница № {page + 1}', '-' * 5, sep='\n')
            if page != 0:
                url = self.url + f'&page={page}'
                body = self.__get_bs4_body(url)
            jobs = self.__get_jobs(body)
            if jobs:
                self.__parse_jobs(jobs)
            else:
                break
        self.__create_json()

    def parse_first_page(self):
        body = self.__get_bs4_body(self.url)
        jobs = self.__get_jobs(body)
        if jobs:
            self.__parse_jobs(jobs)
        self.__create_json()

    def __parse_jobs(self, jobs: ResultSet):
        for job in jobs:
            url = self.__get_url(job)
            salary = self.__get_salary(job)
            company = self.__get_company(job)
            city = self.__get_city(job)
            description = self.__get_full_description(url)
            if self.__check_pattern(description):
                jobs_dict = dict(url=url, salary=salary, company=company, city=city)
                print(jobs_dict)
                self.posts.append(jobs_dict)

    def __get_bs4_body(self, url: str):
        sleep(0.5)
        response = get(url, headers=self.__headers)
        body = BeautifulSoup(response.content, 'lxml')
        return body

    def __get_full_description(self, url: str):
        description = ''
        bs4_body = self.__get_bs4_body(url)
        description_tag = bs4_body.find('div', class_='vacancy-description')
        if description_tag:
            description = description_tag.text
        return description

    def __check_pattern(self, text: str):
        return bool(self.__pattern.search(text))

    def __create_json(self):
        with open('jobs.json', 'w+', encoding='utf-8') as file:
            dump(self.posts, file, indent=4, ensure_ascii=False)

    @staticmethod
    def __get_jobs(body):
        posts = body.find_all('div', class_='serp-item')
        return posts

    @staticmethod
    def __get_url(job: Tag):
        url = ''
        url_tag = job.find('a', attrs={'data-qa': 'serp-item__title'})
        if url_tag:
            url = url_tag['href']
        return url

    @staticmethod
    def __get_city(job: Tag):
        city = ''
        address = job.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'})
        if address:
            city = address.text.split(',')[0].strip()
        return city

    @staticmethod
    def __get_company(job: Tag):
        company = ''
        company_tag = job.find('div', class_='vacancy-serp-item__meta-info-company')
        if company_tag:
            company = company_tag.text.replace('\xa0', ' ').strip()
        return company

    @staticmethod
    def __get_salary(job: Tag) -> str | None:
        salary = ''
        salary_tag = job.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if salary_tag:
            salary = salary_tag.text.replace('\u202f', ' ')
        return salary

    @staticmethod
    def __create_pattern(keywords: list[str]) -> Pattern[AnyStr]:
        return compile('|'.join(keywords), IGNORECASE)

    @staticmethod
    def __get_total_pages(body: BeautifulSoup) -> int:
        total_pages = 0
        total_pages_tag = body.find_all('a', attrs={'data-qa': 'pager-page'})
        if total_pages_tag:
            total_pages = int(total_pages_tag[-1].text)
        return total_pages
