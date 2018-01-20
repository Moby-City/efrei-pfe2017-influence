#!/usr/bin/env python3

import json
from datetime import datetime
from glob import glob

data = {}

for name in sorted(glob('drive-copy/*/*.json'), reverse=True):
    with open(name, 'r') as f:
        print('Reading %s' % name)
        for a in json.load(f):
            if not 'is_confirmed' in a or a['is_confirmed'] is None:
                continue

            if 'translated_text' in a:
                del a['translated_text']
            if 'translated_title' in a:
                del a['translated_title']

            if not a['url'] in data:
                data[a['url']] = a
            else:
                pass
                #if name == 'drive-copy/2017-11-23/2017-11-23-carenews.json':
                #    print('Skip dupl %s (%s)' % (a['title'], data[a['url']]['title']))

filename = '%s-all-classified.json' % datetime.now().strftime('%Y-%m-%d')
with open(filename, "w") as outfile:
    print('Writing %s results to %s' % (len(data), filename))
    outfile.write(json.dumps(list(data.values()), indent=2))
