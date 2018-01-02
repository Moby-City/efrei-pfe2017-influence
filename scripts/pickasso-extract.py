import sys
import os
import re
import csv

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from crawl.datasources.twitter import DataSourceTwitter

with open(sys.argv[-1], 'r') as f:
    reader = csv.DictReader(f)

    assos = [row['Twitter'] for row in reader if len(row['Twitter']) > 0]

    for asso in assos:
        match = re.search(r"twitter\.com/(?: ?#!/)?([^\?\n/]+)", asso)
        if match:
            a = match.groups()[0]
            datasource = DataSourceTwitter()
            if os.path.exists(datasource.out_filepath(a)):
                print('Skipping existing ' + a)
                continue
            print('START SEARCH FOR ' + a)
            datasource.find_all_for(a)
            print('FINISHED SEARCH FOR ' + a)

