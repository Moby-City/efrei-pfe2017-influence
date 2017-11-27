import datetime
import newspaper

from .datasource import DataSource
from ..dataset import DataSet

class DataSourceAFP(DataSource):

    @staticmethod
    def identifier():
        return 'afp'

    def find_all(self):
        afp = newspaper.build('https://www.afp.com/fr', memoize_articles=False)
        
        now = datetime.datetime.now()

        self.add_all_results([DataSet(None, a.url, now, self) for a in afp.articles if '/fr/' in a.url])

        self.fetch_all_result_details()
        self.save_results()
