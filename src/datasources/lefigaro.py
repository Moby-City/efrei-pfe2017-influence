from datasource import DataSource
import newspaper
from dataset import DataSet
from bs4 import BeautifulSoup
from datetime import datetime
import signal
import sys

URL = 'http://recherche.lefigaro.fr/recherche/'

class DataSourceLeFigaro(DataSource):
    def identifier(self):
        return 'lefigaro'

    def find_all_for(self, search_term):
        all_articles = []
        page = 1

        # step 1: query the search to get all article urls
        while page < 2:
            result = self.requestPage(page)
            articles_list = BeautifulSoup(result, 'html.parser').select_one('#articles-list')
            if not articles_list:
                break
            articles = self.parseSearchResult(articles_list)
            print('Loaded page ' + str(page) + ' (' + str(len(articles)) + ' results)')
            if len(articles) < 1:
                break
            all_articles = all_articles + articles
            page = page + 1

        # step 2: fetch the content for each article and parse
        for article in all_articles:
            print('Loading ' + article.url)
            na = newspaper.Article(article.url)
            na.download()
            na.parse()
            article.text = na.text
            article.author = ', '.join(na.authors)
            article.published_date = na.publish_date
            article.media = na.top_image

        self.save_results(all_articles)

    def requestPage(self, page):
        """fetches the html for one page of search results from lefigaro"""
        return self.requestUrl(URL + search_term + '/' if page == 1 else URL + search_term + '/?page=' + str(page))

    def parseSearchResult(self, rootElement):
        """given a root element, enumerate all section elements and created dataset objects filled with title and url"""
        result_list = []
        now = datetime.now()
        for article in rootElement.select('section'):
            url = article.select_one('h2 a')['href']
            title = article.select_one('h2 a').text.strip()
            result_list.append(DataSet(text = '', url = url, title = title, datasource=self, crawled_date=now))
        return result_list

DataSourceLeFigaro().findAllFor('ong')
