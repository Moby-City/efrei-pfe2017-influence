#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from crawl.datasources.lefigaro import DataSourceLeFigaro
from crawl.datasources.carenews import DataSourceCareNews
from crawl.datasources.ulule import DataSourceUlule
from crawl.datasources.facebook import DataSourceFacebook
from crawl.datasources.twitter import DataSourceTwitter
from crawl.datasources.cnews_matin import DataSourceCNewsMatin

datasources = [
    DataSourceLeFigaro,
    DataSourceUlule,
    DataSourceCNewsMatin,
    DataSourceFacebook,
    DataSourceTwitter,
    DataSourceCareNews
]

if len(sys.argv) < 2:
    print('Usage: run-crawler.py DATASOURCE_IDENTIFIER [optional search term]')
    sys.exit(1)

to_be_run = sys.argv[1]
datasource = next(d for d in datasources if d.identifier() == to_be_run)

if len(sys.argv) == 3:
    datasource().find_all_for(sys.argv[2])
else:
    datasource().find_all()

