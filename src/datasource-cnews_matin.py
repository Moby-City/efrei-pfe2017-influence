import urllib3
from datasource import DataSource
from bs4 import BeautifulSoup
from datetime import datetime, date
from dataset import DataSet
import newspaper
import json

URL = 'http://cnewsmatin.fr'
SEARCH_URL = URL + '/rechercher/'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
http = urllib3.PoolManager()

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__

class DataSourceCNewsMatin(DataSource):
    def findAll(self):

        all_articles = []
        page = 0
        while page < 1:
            result = self.requestPage(page)
            articles = self.parseSearchResult(BeautifulSoup(result, 'html.parser').select_one('.search-results'))
            for a in articles:
                print(a.url)

            if len(articles) < 1:
                break
            
            all_articles = all_articles + articles
            page = page + 1

        for article in all_articles:
            print('Loading ' + article.url)
            na = newspaper.Article(article.url)
            na.download()
            na.parse()
            article.text = na.text
            article.title = na.title
            article.author = ', '.join(na.authors)
            article.published_date = na.publish_date
            article.media = na.top_image

        self.writeArticleList(all_articles, 'cnewsmatin.json')


    def writeArticleList(self, articles, filename):
        f = open(filename, 'w')
        f.write(json.dumps(articles, default=json_serial))

    def requestUrl(self, url):
        return http.request('GET',
                url,
                headers={'user-agent': USER_AGENT}
            ).data.decode('utf-8')

    def requestPage(self, page):
        return self.requestUrl(SEARCH_URL + 'ong' if page == 0 else SEARCH_URL + 'ong?page=' + str(page))

    def parseSearchResult(self, rootElement):
        result_list = []
        now = datetime.now()
        for article in rootElement.select('a'):
            url = URL + article['href'] 

            result_list.append(DataSet(text = '', url = url, title = '', datasource = self, crawled_date = now))
        return result_list

DataSourceCNewsMatin().findAll()
