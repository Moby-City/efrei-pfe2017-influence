from datetime import datetime, date
import json
import urllib3

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__

class DataSource():
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

    def __init__(self):
        self.http = urllib3.PoolManager()

    ###################
    # to be implemented
    ###################

    def identifier(self):
        pass

    def find_all(self):
        pass

    def find_all_for(self, search_term):
        pass

    ##################
    # public utilities
    ##################

    def save_results(self, datasets):
        self.write_dataset_list(datasets, sys.path[0] + '/../output/lefigaro.json')

    def request_url(self, url):
        """fetches the html content at the given URL (while pretending to be a browser)"""
        return http.request('GET',
                url,
                headers={'user-agent': self.USER_AGENT}
            ).data.decode('utf-8')

    #################
    # private helpers
    #################

    def write_dataset_list(self, datasets, filename):
        """writes the given array of datasets to filename in json format"""
        f = open(filename, 'w')
        f.write(json.dumps(datasets, default=json_serial))



