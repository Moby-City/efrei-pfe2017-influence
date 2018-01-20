#!/usr/bin/env python3

import sys
import json
import deepl

if len(sys.argv) < 3 or not sys.argv[-2].isdigit():
    print('Usage: translate.py NUM_TO_TRANSLATE IN_FILE.json')
    sys.exit(1)

articles = []

with open(sys.argv[-1], 'r') as f:
    articles = json.load(f)
    todo = [article for article in articles if not 'translated_text' in article and article['is_confirmed'] is None]
    num = int(sys.argv[-2])
    for i in range(0, num):
        print('%s (%s/%s)' % (todo[i]['title'], i + 1, num))
        try:
            todo[i]['translated_text'] = deepl.translate(todo[i]['text'], target='DE')[0]
            todo[i]['translated_title'] = deepl.translate(todo[i]['title'], target='DE')[0]
            print('\t=> %s' % (todo[i]['translated_title']))
        except KeyError:
            print('Likely ran out of request quota! Aborting and saving all results thus far.')
            break

with open(sys.argv[-1], 'w') as f:
    f.write(json.dumps(articles, indent=2))

