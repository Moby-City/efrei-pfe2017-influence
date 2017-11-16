#!/usr/bin/env python3
import nltk
import os
import sys
import json

if len(sys.argv) < 2:
    print('Usage: preprocess.py IN_FILE.json (--> produces IN_FILE.csv)')
    sys.exit(1)

stopwords = set(nltk.corpus.stopwords.words('french'))
stopwords.update([w[0:-1] for w in open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'french-stopwords.txt'))][1:])
stopwords.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '\'', '\'\'', '``', '`', '»', '«', '...'])

print(stopwords)
out = 'text,ngo\n'

for article in json.load(open(sys.argv[-1], 'r'))[0:100]:
    data = nltk.word_tokenize(article['text'])

    data = [t.lower() for t in data if t.lower() not in stopwords]

    stemmer = nltk.SnowballStemmer('french')
    data = [stemmer.stem(t) for t in data]

    wnl = nltk.WordNetLemmatizer()
    data = [wnl.lemmatize(t) for t in data]

    out = out + '"%s","%s"\n' % (' '.join(data), 'NGO' if article['is_confirmed'] else 'non-NGO')

open(sys.argv[-1][0:-4] + 'csv', 'w').write(out)
