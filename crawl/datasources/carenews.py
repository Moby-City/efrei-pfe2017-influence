from bs4 import BeautifulSoup
from datetime import datetime

from ..organization import Organization
from ..dataset import DataSet
from .datasource import DataSource

BASE_URL = 'http://www.carenews.com/fr/'
ORGANIZATION_URL = BASE_URL + 'organisations'
ARTICLES_URL = BASE_URL + 'timeline'
SEARCH_URL = BASE_URL + 'search?q='

class DataSourceCareNews(DataSource):

    @staticmethod
    def identifier():
        return 'carenews'

    def find_all(self):
        page = 1

        while page < 25:

            print("Fetching page %s" % page)
            now = datetime.now()
            url = '%s?page=%s&search[content_types]=Article' % (ARTICLES_URL,
                    str(page))

            if self.add_all_results([DataSet(None, a['data-href'], now, self, None, None)
                    for a in self.request_node(url).select('.archive-holder article')]) < 1:
                break

            if len(self.results) > len(set(self.results)):
                print("DUPLICATES!")
                print(page)
                print(url)
                break

            page = page + 1

        self.fetch_all_result_details()
        self.save_results()

    def find_all_for(self, searchTerm):
        now = datetime.now()
        articles = [DataSet(None, article['data-href'], now, self)
            for article in self.request_node(SEARCH_URL + searchTerm)
                .select('#search-results-article .archive-holder article')]
        self.add_all_results(articles)
        self.fetch_all_result_details()
        self.save_results(searchTerm)

    def parse_article_list(self, rootElement):
        now = datetime.now()
        for article in rootElement.select('article'):
            url = article['data-href']
            self.add_result(DataSet(None, url, now, self, None, None))

    def find_all_organizations(self):
        all_organizations = []

        # page 1
        result = self.request_url(ORGANIZATION_URL)
        organizations_list = BeautifulSoup(result, 'html.parser').select_one('.organizations-list-items')
        organization_urls = self.parse_search_result(organizations_list)

        print('Parsing page 0')
        for url in organization_urls:
            result = self.request_url(url)
            description = self.parse_organization_description(BeautifulSoup(result, 'html.parser'))
            title = self.parse_organization_title(BeautifulSoup(result, 'html.parser'))
            all_organizations.append(Organization(title = title, description = description, url = url))

        # next pages
        ids = 10
        while True:
            urls = URL +\
                    '?duration=month&country=&cause=&after_ids[non_profit]=' +\
                    str(ids) +\
                    '&after_ids[enterprise]=' +\
                    str(ids) +\
                    '&q='
            result = self.request_url(urls)
            organizations_list = BeautifulSoup(result, 'html.parser').select_one('.organizations-list-items')
            organization_urls = self.parse_search_result(organizations_list)

            print('Parsing page ' + str(ids / 10))
            for url in organization_urls:
                result = self.request_url(url)
                description = self.parse_organization_description(BeautifulSoup(result, 'html.parser'))
                title = self.parse_organization_title(BeautifulSoup(result, 'html.parser'))
                self.add_result(Organization(title = title, description = description, url = url))
            ids = ids + 10
        
        self.save_results()

    def parse_search_result(self, rootElement):
        result_list = []
        for organization in rootElement.select('.post header .organization_data_link'):
            url = organization['href']
            result_list.append(url)

        return result_list

    def parse_organization_description(self, page):
        span = page.select('.description span')
        return span[0].text.strip()

    def parse_organization_title(self, page):
        title = page.select('.big h1')
        return title[0].text
