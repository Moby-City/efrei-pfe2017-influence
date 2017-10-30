from datasource import DataSource
import json
import urllib3
import config

http = urllib3.PoolManager()

FIELDS = 'category_list'
QUERY = 'who'
BASE_URL = 'https://graph.facebook.com/v2.10'
LIMIT = 99999

class DataSourceFacebook(DataSource):

    def findAll(self):
        data = self.getPageOfPages()
        print(data)
        all_pages = data['data']
        count = 0
        while True:
            if not 'paging' in data:
                break
            afterToken = data['paging']['cursors']['after']
            data = self.getPageOfPages(afterToken)
            all_pages = all_pages + data['data']
            count = count + 1
        print(all_pages)
        print(str(len(all_pages)))

    def getPageOfPages(self, afterToken=None):
        """returns the json of a single response page of querying the facebook pages search"""
        return self.getApiCall('/search', {
            'q': QUERY,
            'type': 'page',
            'limit': LIMIT,
            'fields': FIELDS,
            'access_token': config.FACEBOOK_TOKEN,
            'after': afterToken
        })

    def getApiCall(self, path, queryParams={}):
        query = '?'
        for param, value in queryParams.items():
            if value:
                query += param + '=' + str(value) + '&'
        result = json.loads(http.request('GET', BASE_URL + path + query).data.decode('utf-8'))
        if 'error' in result:
            raise IOError(result['error']['message'])
        return result

    def getPageInfo(self, pageId):
        pass

DataSourceFacebook().findAll()


