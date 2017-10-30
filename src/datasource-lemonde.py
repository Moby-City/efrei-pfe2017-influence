from datasource import DataSource
from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()

class DataSourceLeMonde(DataSource):

    def isArticlePage(self, html):
        pass

    def findAll(self):
        html = http.request('GET', 'http://www.lemonde.fr/recherche/?keywords=ong').data
        print(html)

        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        print(soup.find_all('article'))

        for article in soup.find_all('article'):
            title = article.select('h3 a')[0].text
            print(title)

DataSourceLeMonde().findAll()

