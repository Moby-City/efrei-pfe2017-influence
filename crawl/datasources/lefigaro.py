from bs4 import BeautifulSoup
from datetime import datetime

from .datasource import DataSource
from ..dataset import DataSet

URL = 'http://recherche.lefigaro.fr/recherche/'

class DataSourceLeFigaro(DataSource):

    @staticmethod
    def identifier():
        return 'lefigaro'

    def find_all_for(self, search_term):
        page = 1

        while True:
            result = self.request_page(page, search_term)
            articles_list = BeautifulSoup(result, 'html.parser').select_one('#articles-list')
            if not articles_list:
                break

            articles = self.parse_search_result(articles_list)
            print('Loaded page ' + str(page) + ' (' + str(len(articles)) + ' results)')
            if len(articles) < 1:
                break
            self.add_all_results(articles)
            page = page + 1

        self.fetch_all_result_details()
        self.save_results(search_term)

    def request_page(self, page, search_term):
        """fetches the html for one page of search results from lefigaro"""
        return self.request_url(URL + search_term + '/' if page == 1 else URL + search_term + '/?page=' + str(page))

    def parse_search_result(self, rootElement):
        """given a root element, enumerate all section elements and created dataset objects filled with title and url"""
        result_list = []
        now = datetime.now()
        for article in rootElement.select('section'):
            url = article.select_one('h2 a')['href']
            title = article.select_one('h2 a').text.strip()
            result_list.append(DataSet(None, url, now, self, None, title))
        return result_list
