from datasource import DataSource
import newspaper
from dataset import DataSet
from bs4 import BeautifulSoup
import json
import urllib3
from datetime import datetime, date

http = urllib3.PoolManager()

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
URL = 'http://recherche.lefigaro.fr/recherche/'

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__

class DataSourceLeFigaro(DataSource):
    def findAll(self):
        all_articles = []
        page = 1

        # step 1: query the search to get all article urls
        while True:
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

        self.writeArticleList(all_articles, 'lefigaro.json')

    def writeArticleList(self, articles, filename):
        """writes the given array of datasets to filename in json format"""
        f = open(filename, 'w')
        f.write(json.dumps(articles, default=json_serial))

    def requestUrl(self, url):
        """fetches the html content at the given URL (while pretending to be a browser)"""
        return http.request('GET',
                url,
                headers={'user-agent': USER_AGENT}
            ).data.decode('utf-8')

    def requestPage(self, page):
        """fetches the html for one page of search results from lefigaro"""
        return self.requestUrl(URL + 'ong/' if page == 1 else URL + 'ong/?page=' + str(page))

    def parseSearchResult(self, rootElement):
        """given a root element, enumerate all section elements and created dataset objects filled with title and url"""
        result_list = []
        now = datetime.now()
        for article in rootElement.select('section'):
            url = article.select_one('h2 a')['href']
            title = article.select_one('h2 a').text.strip()
            result_list.append(DataSet(text = '', url = url, title = title, datasource=self, crawled_date=now))
        return result_list

DataSourceLeFigaro().findAll()
