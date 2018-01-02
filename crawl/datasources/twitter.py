import tweepy
import dateutil.parser
from datetime import datetime, date

from .datasource import DataSource
from ..dataset import DataSet
from ..config import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_SECRET, TWITTER_ACCESS_TOKEN

class DataSourceTwitter(DataSource):

    @staticmethod
    def identifier():
        return 'twitter'

    def _twitter_api(self):
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        return tweepy.API(auth)

    def find_users(self, query):
        api = self._twitter_api()
        for user in tweepy.Cursor(api.search_users, q=query, lang='fr').items():
            print(user)

    def find_all_for(self, twitter_handle):
        api = self._twitter_api()
        now = datetime.now()

        tweets = []
        try:
            for status in tweepy.Cursor(api.user_timeline, screen_name=twitter_handle).items():
                data = status._json
                media = (data['extended_entities']['media'][0]['media_url_https']
                    if 'extended_entities' in data and
                        'media' in data['extended_entities'] and
                        len(data['extended_entities']['media']) > 0
                        else '')

                self.add_result(DataSet(
                    data['text'],
                    'https://twitter.com/statuses/' + data['id_str'],
                    now,
                    self,
                    author=twitter_handle,
                    media=media,
                    published_date=dateutil.parser.parse(data["created_at"]),
                    extra={
                        'favorites': data['favorite_count'],
                        'retweets': data['retweet_count']
                    }))

            self.save_results(twitter_handle)
        except tweepy.error.TweepError as err:
            if err.response.status_code != 404 and err.response.status_code != 401:
                raise err
            else:
                print("SKIPPING INVALID " + twitter_handle)
            
