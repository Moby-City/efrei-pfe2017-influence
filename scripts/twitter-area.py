import sys
import os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from crawl.datasources.twitter import DataSourceTwitter

DataSourceTwitter().find_users('near:"Paris, France" within:15m')
