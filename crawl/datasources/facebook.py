import json
import sys
from datetime import datetime

from .datasource import DataSource
from ..dataset import DataSet
from ..config import FACEBOOK_APP_TOKEN, FACEBOOK_TOKEN

FIELDS = 'category_list'
QUERY = 'who'
BASE_URL = 'https://graph.facebook.com/v2.10'
LIMIT = 999

class DataSourceFacebook(DataSource):

    @staticmethod
    def identifier():
        return 'facebook'

    def find_organizations(self):
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

    def getIdentifier(self, post):
        if 'permalink_url' in post:
            return post['permalink_url']
        elif 'link' in post:
            return 'external:' + post['link']
        else:
            return pageId + '/' + post['id']

    def find_all_for(self, pageId):
        query_url = BASE_URL +\
                '/' +\
                pageId +\
                '?fields=posts.limit(' +\
                str(LIMIT) +\
                '){message,full_picture,link,permalink_url}&access_token=' +\
                FACEBOOK_TOKEN
        
        result = json.loads(self.request_url(query_url))
            
        if 'error' in result:
            print(result['error']['message'])
            sys.exit(1)
        else:
            now = datetime.now()
            for post in result['posts']['data']:
                if 'message' in post:
                    self.add_result(DataSet(
                        post['message'],
                        self.getIdentifier(post),
                        now,
                        self,
                        media=post['full_picture'] if 'full_picture' in post else None))
        
            self.save_results(pageId)
