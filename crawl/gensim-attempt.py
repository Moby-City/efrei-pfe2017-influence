import json
import sys
from gensim import models
from gensim.models.doc2vec import TaggedDocument
import gensim
import os

class DocIterator(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list

    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            # print 'creating tagged document...%d' % idx
            yield TaggedDocument(words=doc.split(), tags=[self.labels_list[idx]])

results = [json.load(open(name, 'r')) for name in sys.argv[1:]]
data = [article for result in results for article in result]

import nltk
import re
stopwords = set(nltk.corpus.stopwords.words('french'))
stopwords.update([w[0:-1] for w in open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'french-stopwords.txt'))][1:])
stopwords.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '\'', '\'\'', '``', '`', '»', '«', '...', "\""])
def preprocess_text(text):
    text = nltk.word_tokenize(text.replace('\n', ' '))

    text = [t.lower() for t in text if t.lower() not in stopwords]
    text = [re.sub(r"^(d|l|qu|c|s)'", '', w) for w in text if not re.match(r"^(\d+|\.)$", w)]

    stemmer = nltk.SnowballStemmer('french')
    text = [stemmer.stem(t) for t in text]

    wnl = nltk.WordNetLemmatizer()
    text = [wnl.lemmatize(t) for t in text]

    return ' '.join(text)

docLabels = [article['title'] for article in data]
docs = [preprocess_text(article['text']) for article in data if article['is_confirmed']]
print('Working with ' + str(len(docs)) + ' docs')

it = DocIterator(docs, docLabels)
# use fixed learning rate
model = gensim.models.Doc2Vec(size=300, window=10, min_count=5, workers=11, alpha=0.025, min_alpha=0.025)
model.build_vocab(it)
for epoch in range(3):
    model.train(it, total_examples=len(docs), epochs=model.iter)
    # decrease the learning rate
    model.alpha -= 0.002
    # fix the learning rate, no deca
    model.min_alpha = model.alpha
    model.train(it, total_examples=len(docs), epochs=model.iter)
model.save('all.model')

def compare_to(filename):
    #print('THIS IS THE TEXT TO BE SEARCHED:' + data[0]['text'])
    with open(filename, 'r') as f:
        ivec = model.infer_vector(doc_words=preprocess_text(f.read()), steps=20, alpha=0.025)
        # print('RESULT:' + str(model.most_similar(positive=[ivec], topn=400)))
        print('RESULT:' + str(model.most_similar(negative=[ivec], topn=400)))


ivec = model.infer_vector(doc_words=['Greepeace'], steps=20, alpha=0.025)
print('RESULT:' + str(model.most_similar(positive=[ivec], topn=400)))
#compare_to('./completely-unrelated')

# VISUALIZE
def visualize():
    import pandas as pd
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt

    vocab = list(model.wv.vocab)
    X = model[vocab]
    tsne = TSNE(n_components=2)
    X_tsne = tsne.fit_transform(X)
    df = pd.concat([pd.DataFrame(X_tsne),
                    pd.Series(vocab)],
                   axis=1)
    df.columns = ['x', 'y', 'word']


    fig = plt.figure(figsize=(25, 25))
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(df['x'], df['y'])
    for i, txt in enumerate(df['word']):
        ax.annotate(txt, (df['x'].iloc[i], df['y'].iloc[i]), fontsize=2)
    fig.savefig('pic.png', dpi=900)
#visualize()
