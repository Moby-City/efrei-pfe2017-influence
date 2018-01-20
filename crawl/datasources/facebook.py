import json
import sys
from datetime import datetime

from .datasource import DataSource
from ..dataset import DataSet
from ..config import FACEBOOK_APP_TOKEN, FACEBOOK_TOKEN, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

FIELDS = 'category_list'
QUERY = 'who'
BASE_URL = 'https://graph.facebook.com/v2.10'
#LIMIT = 999
LIMIT = 10

cached_app_access_token = None

class DataSourceFacebook(DataSource):

    @staticmethod
    def identifier():
        return 'facebook'

    def exact_identifier(self):
        return identifier()

    def fetch_token(self):
        return self.getApiCall('/oauth/access_token', {
            'client_id': FACEBOOK_CLIENT_ID,
            'client_secret': FACEBOOK_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        })['access_token']


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
        global cached_app_access_token

        self.search_term = pageId

        if not cached_app_access_token:
            cached_app_access_token = self.fetch_token()

        FIELDS = 'message,full_picture,link,permalink_url,created_time,shares,reactions.limit(1).summary(true),likes.limit(1).summary(true),comments.limit(1).summary(true)'

        query_url = BASE_URL +\
                '/' +\
                pageId +\
                '?fields=posts.limit('+str(LIMIT)+'){' + FIELDS + '}&access_token=' +\
                cached_app_access_token

        result = json.loads(self.request_url(query_url))

        if 'error' in result:
            print(result['error']['message'])
            raise RuntimeError(result['error']['message'])
        else:
            now = datetime.now()
            for post in result['posts']['data']:
                print(post)
                if 'message' in post and self.safe_verify_language(post['message']):
                    self.add_result(DataSet(
                        post['message'],
                        self.getIdentifier(post),
                        now,
                        self,
                        published_date=post['created_time'],
                        media=post['full_picture'] if 'full_picture' in post else None,
                        extra={
                            'reactions': post['reactions']['summary']['total_count'],
                            'likes': post['likes']['summary']['total_count'],
                            'comments': post['comments']['summary']['total_count']
                        }))

            self.save_results(pageId)
