from bs4 import BeautifulSoup
from datetime import datetime
import newspaper

from .datasource import DataSource
from ..dataset import DataSet

URL = 'http://cnewsmatin.fr'
SEARCH_URL = URL + '/rechercher/'
ARTICLES_URL = URL + '/le-direct'

class DataSourceCNewsMatin(DataSource):

    @staticmethod
    def identifier():
        return 'cnews_matin'

    def find_all(self):
        articles = newspaper.build(ARTICLES_URL, memoize_articles=False)
        now = datetime.now()

        self.add_all_results([DataSet(None, a.url, now, self) for a in articles.articles])
        self.fetch_all_result_details()
        self.save_results()

    def find_all_for(self, search_term):
        page = 0
        while page < 1:
            result = self.request_page(page, search_term)
            articles = self.parseSearchResult(BeautifulSoup(result, 'html.parser').select_one('.search-results'))
            if len(articles) < 1:
                break

            self.add_all_results(articles)
            page = page + 1

        self.fetch_all_result_details()
        self.save_results(search_term)

    def request_page(self, page, search_term):
        return self.request_url(SEARCH_URL + search_term if page == 0 else SEARCH_URL + search_term + '?page=' + str(page))

    def parseSearchResult(self, rootElement):
        result_list = []
        now = datetime.now()
        for article in rootElement.select('a'):
            url = URL + article['href'] 

            result_list.append(DataSet(None, url, now, self))
        return result_list
