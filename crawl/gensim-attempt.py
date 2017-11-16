import json
from gensim import models
from gensim.models.doc2vec import TaggedDocument
import gensim

class DocIterator(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list

    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            # print 'creating tagged document...%d' % idx
            yield TaggedDocument(words=doc.split(), tags=[self.labels_list[idx]])


class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
       self.labels_list = labels_list
       self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield LabeledSentence(words=doc.split(),labels=[self.labels_list[idx]])

data = json.load(open('lefigaro.json', 'r'))

docLabels = [article['title'] for article in data]
data = [article['text'] for article in data]

it = DocIterator(data, docLabels)
# use fixed learning rate
model = gensim.models.Doc2Vec(size=300, window=10, min_count=5, workers=11,alpha=0.025, min_alpha=0.025)
model.build_vocab(it)
for epoch in range(3):
    model.train(it, total_examples=len(data), epochs=model.iter)
    # decrease the learning rate
    model.alpha -= 0.002
    # fix the learning rate, no deca
    model.min_alpha = model.alpha
    model.train(it, total_examples=len(data), epochs=model.iter)

print(data[0])
ivec = model.infer_vector(doc_words=data[0], steps=20, alpha=0.025)
print(model.most_similar(positive=[ivec], topn=10))

model.save('doc2vec-lefigaro.model')
