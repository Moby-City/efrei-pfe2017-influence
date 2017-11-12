import sys
import json
import deepl

articles = []

with open(sys.argv[-1], 'r') as f:
    articles = json.load(f)
    for i in range(0, 10):
        print('%s (%s/%s)' % (articles[i]['title'], i + 1, len(articles)))
        articles[i]['translated_text'] = deepl.translate(articles[i]['text'], target='DE')[0]
        articles[i]['translated_title'] = deepl.translate(articles[i]['title'], target='DE')[0]
        print('\t=> %s' % (articles[i]['translated_title']))

with open(sys.argv[-1], 'w') as f:
    f.write(json.dumps(articles))

