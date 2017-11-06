from datasource import DataSource
import urllib3
from bs4 import BeautifulSoup
import newspaper
from organization import Organization
import json

http = urllib3.PoolManager()

URL = 'http://www.carenews.com/fr/organisations'

def json_serial(obj):
    return obj.__dict__

class DataSourceCareNews(DataSource):
    def findAll(self):
        all_organizations = []

        result = self.requestUrl(URL)
        organizations_list = BeautifulSoup(result, 'html.parser').select_one('.organizations-list-items')

        organization_urls = self.parseSearchResult(organizations_list)
        for url in organization_urls:
            result = self.requestUrl(url)
            description = self.parseOrganizationDescription(BeautifulSoup(result, 'html.parser'))
            title = self.parseOrganizationTitle(BeautifulSoup(result, 'html.parser'))
            all_organizations.append(Organization(title = title, description = description, url = url))

            self.writeOrganizationList(all_organizations, 'carenews.json')

    def parseSearchResult(self, rootElement):
        result_list = []
        for organization in rootElement.select('.post header .organization_data_link'):
            url = organization['href']
            result_list.append(url)

        return result_list

    def parseOrganizationDescription(self, page):
        span = page.select('.description span')
        return span[0].text.strip()

    def parseOrganizationTitle(self, page):
        title = page.select('.big h1')
        return title[0].text

    def requestUrl(self, url):
        return http.request('GET', url).data.decode('utf-8')

    def writeOrganizationList(self, organizations, filename):
        f = open(filename, 'w')
        f.write(json.dumps(organizations, default=json_serial))

DataSourceCareNews().findAll()
