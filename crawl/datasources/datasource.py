from datetime import datetime, date
import langdetect
import newspaper
import json
import urllib3
import os

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, DataSource):
        return obj.identifier()
    else:
        return obj.__dict__

class DataSource():
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.results = []

    ###################
    # to be implemented
    ###################

    @staticmethod
    def identifier():
        raise NotImplementedError()

    def find_all(self):
        raise NotImplementedError()

    def find_all_for(self, search_term):
        raise NotImplementedError()

    ##################
    # public utilities
    ##################

    def add_all_results(self, datasets):
        self.results = self.results + datasets

    def add_result(self, dataset):
        self.results.append(dataset)

    def save_results(self, suffix = None):
        """save results to /output/$identifier.json"""
        name = '%s-%s%s.json' % (
                datetime.now().strftime('%Y-%m-%d'),
                self.identifier(),
                ('-' + ''.join(filter(str.isalnum, suffix)) if suffix else ''))
        path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '..',
                '..',
                'output',
                name)
        with open(path, 'w') as f:
            f.write(json.dumps(self.results, default=json_serial, indent=2))
            print('Saved ' + name)

    def fetch_all_result_details(self):
        """iterates over all results and tries to add more detailed information"""
        progress = 0
        for article in self.results:
            print('Loading [%s/%s] %s' % (progress, len(self.results), article.url))
            self.fetch_details_for(article)
            progress = progress + 1

    def request_url(self, url, encoding='utf-8'):
        """fetches the html content at the given URL (while pretending to be a browser)"""
        return self.http.request('GET',
                url,
                headers={'user-agent': self.USER_AGENT}
            ).data.decode(encoding)

    def verify_language(self, text):
        """given a text, verify that it is in a relevant language"""
        return langdetect.detect(text) == 'fr'

    ######################
    # semi-private helpers
    ######################

    def fetch_details_for(self, dataset):
        """given a dataset whose url field is filled, fill more detail fields"""
        try:
            na = newspaper.Article(dataset.url)
            na.download()
            na.parse()
            if not dataset.title:
                dataset.title = na.title
            dataset.text = na.text
            dataset.author = ', '.join(na.authors)
            dataset.published_date = na.publish_date
            dataset.media = na.top_image
        except:
            print('Could not retrieve data for ' + dataset.url)
            pass
