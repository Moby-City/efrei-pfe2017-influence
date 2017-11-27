import datetime

from .datasource import DataSource
from ..dataset import DataSet

URL = 'http://recherche.lefigaro.fr/recherche/'

class DataSourceParisFR(DataSource):

    @staticmethod
    def identifier():
        return 'parisfr'

    def find_all(self):
        now = datetime.datetime.now()
        page = 1

        while True:
            print('Fetching page ' + str(page))
            
            page = page + 1
            articles = [DataSet(None, 'https://www.paris.fr/' + a['href'], now, self)
                    for a in self.request_node('https://www.paris.fr/actualites?page=' + str(page))
                        .select('.news-list-item a')]
            if len(articles) < 1:
                break
            self.add_all_results(articles)

        self.fetch_all_result_details()
        self.save_results()
