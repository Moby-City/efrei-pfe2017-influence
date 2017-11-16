from bs4 import BeautifulSoup
from datetime import datetime

from .datasource import DataSource
from ..dataset import DataSet

class DataSourceUlule(DataSource):

  @staticmethod
  def identifier():
    return 'ulule'

  def __init__(self):
    super().__init__()
    self.URL           = 'https://www.ulule.com/discover/'
    self.SEARCH_URL    = self.URL + '?q='
    self.URL_BASE      = 'https://fr.ulule.com'

  def find_all(self):
    next_url = self.URL_BASE + '/discover/all/'

    page = 1
    while True:
      print('Fetching page ' + str(page))
      page = page + 1
      s = self.request_url(next_url)
      soup = BeautifulSoup(s, 'html.parser')

      projects = soup.select('a.b-blink__link')
      now = datetime.now()
      for project in projects:
        title = project.select_one('h2.b-blink__title').text.strip()
        author = project.select_one('.b-blink__author').text.strip()
        self.add_result(DataSet(None, project['href'], now, self, author, title))

      # find next page url
      next_link = soup.select_one('#results-footer li.active + li a')
      if not next_link:
        break
      else:
        next_url = self.URL_BASE + next_link['href']

    self.fetch_all_result_details()
    self.save_results()
