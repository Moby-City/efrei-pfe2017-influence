from datasource import DataSource
from dataset import DataSet
from datetime import datetime, date
import dateutil.parser
import config
import json
import tweepy

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__

class DataSourceLeFigaro(DataSource):
    def __init__(self, twitterHandle):
        self.twitterHandle = twitterHandle

    def findAll(self):
        auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(config.TWITTER_ACCESS_TOKEN, config.TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        now = datetime.now()
        tweets = []
        for status in tweepy.Cursor(api.user_timeline, screen_name=self.twitterHandle).items():
            data = status._json
            url = data['urls'][0]['url'] if 'urls' in data and len(data['url']) > 0 else ''
            media = data['media'][0]['media_url_https'] if 'media' in data and len(data['media']) > 0 else ''
            tweets.append(DataSet(
                data['text'],
                url,
                now,
                self,
                author=self.twitterHandle,
                media=media,
                published_date=dateutil.parser.parse(data["created_at"])))
        self.writeArticleList(tweets, 'twitter-who.json')

    def writeArticleList(self, articles, filename):
        """writes the given array of datasets to filename in json format"""
        f = open(filename, 'w')
        f.write(json.dumps(articles, default=json_serial, indent=2))

if __name__ == '__main__':
    DataSourceLeFigaro('@WHO').findAll()
