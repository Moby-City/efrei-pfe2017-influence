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

    def find_all_for(self, twitter_handle):
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        now = datetime.now()

        tweets = []
        for status in tweepy.Cursor(api.user_timeline, screen_name=twitter_handle).items():
            data = status._json
            url = data['urls'][0]['url'] if 'urls' in data and len(data['url']) > 0 else ''
            media = data['media'][0]['media_url_https'] if 'media' in data and len(data['media']) > 0 else ''
            if self.verify_language(data['text']):
                self.add_result(DataSet(
                    data['text'],
                    url,
                    now,
                    self,
                    author=twitter_handle,
                    media=media,
                    published_date=dateutil.parser.parse(data["created_at"])))

        self.save_results(twitter_handle)
