import json
from ..config import FACEBOOK_APP_TOKEN, FACEBOOK_TOKEN
import sys

from .datasource import DataSource

FIELDS = 'category_list'
QUERY = 'who'
BASE_URL = 'https://graph.facebook.com/v2.10'
LIMIT = 99999

class DataSourceFacebook(DataSource):

    @staticmethod
    def identifier():
        return 'facebook'

    def find_all(self):
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
            'access_token': FACEBOOK_TOKEN,
            'after': afterToken
        })

    def getApiCall(self, path, queryParams={}):
        query = '?'
        for param, value in queryParams.items():
            if value:
                query += param + '=' + str(value) + '&'
        result = json.loads(self.request_url(BASE_URL + path + query))
        if 'error' in result:
            raise IOError(result['error']['message'])
        return result

    def getPageInfo(self, pageId):
        pass

    def findPostsForPage(self, pageId):
        query_url = BASE_URL + '/' + pageId + '?fields=posts.limit(' + str(LIMIT) + '){message,full_picture,link}&access_token=' + FACEBOOK_TOKEN
        result = json.loads(self.request_url(query_url))

        filename = sys.path[0] + '/../output/facebook/' + pageId + '.json'
        f = open(filename, 'w')
        f.write(json.dumps(result))

# selected_ngos = ['TousBenevoles', 'EntourageReseauCivique', 'haitiski', 'FVolontaires', 'urbanrefugees', '100000rencontressolidaires', 'lionsclubs', 'AideEtActionInternational']
