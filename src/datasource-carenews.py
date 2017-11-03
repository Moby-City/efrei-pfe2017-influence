from datasource import DataSource
import urllib3
from bs4 import BeautifulSoup
import newspaper
from organization import Organization

http = urllib3.PoolManager()

URL = 'http://www.carenews.com/fr/organisations'

class DataSourceCareNews(DataSource):
    def findAll(self):
        all_organizations = []

        result = self.requestUrl(URL)
        organisations_list = BeautifulSoup(result, 'html.parser').select_one('.organizations-list-items')

        organization_urls = self.parseSearchResult(organisations_list)
        for url in organization_urls:
            result = self.requestUrl(url)
            self.parseOrganizationPage(BeautifulSoup(result, 'html.parser'))


    def parseSearchResult(self, rootElement):
        result_list = []
        for organisation in rootElement.select('.post header .organization_data_link'):
            url = organisation['href']
            result_list.append(url)

        return result_list

    def parseOrganizationPage(self, page):
        description = page.select('.description span')
        print(description)

    def requestUrl(self, url):
        return http.request('GET', url).data.decode('utf-8')

DataSourceCareNews().findAll()
