from bs4 import BeautifulSoup

from ..organization import Organization
from .datasource import DataSource

URL = 'http://www.carenews.com/fr/organisations'

class DataSourceCareNews(DataSource):

    @staticmethod
    def identifier():
        return 'carenews'

    def find_all(self):
        all_organizations = []

        # page 1
        result = self.request_url(URL)
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
