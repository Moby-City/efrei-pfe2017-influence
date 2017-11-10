import nltk
import sys
import json


stopwords = set(nltk.corpus.stopwords.words('french'))
stopwords.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '\'', '\'\'', '``', '`', '»', '«', '...'])

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

