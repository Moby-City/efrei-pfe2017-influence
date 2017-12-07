#!/usr/bin/env python3
import nltk
import os
import sys
import json
import csv

if len(sys.argv) < 2:
    print('Usage: preprocess.py IN_FILE.json (--> produces IN_FILE.csv)')
    sys.exit(1)

stopwords = set(nltk.corpus.stopwords.words('french'))
stopwords.update([w[0:-1] for w in open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'french-stopwords.txt'))][1:])
stopwords.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '\'', '\'\'', '``', '`', '»', '«', '...'])

with open(sys.argv[-1][0:-4] + 'csv', 'w') as f:
    writer = csv.writer(f, delimiter=',', quotechar="|")

    # out = 'text,ngo\n'

    for article in json.load(open(sys.argv[-1], 'r')):
        data = nltk.word_tokenize(article['text'].replace('\n', ' '))

        data = [t.lower() for t in data if t.lower() not in stopwords]

        #stemmer = nltk.SnowballStemmer('french')
        #data = [stemmer.stem(t) for t in data]

        #wnl = nltk.WordNetLemmatizer()
        #data = [wnl.lemmatize(t) for t in data]

        writer.writerow([' '.join(data), 'NGO' if article['is_confirmed'] else ( 'X' if article['is_confirmed'] is None else 'non-NGO')])

