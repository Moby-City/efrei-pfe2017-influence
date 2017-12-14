import re
import json
import sklearn.metrics

with open('2017-11-29-all-classified.json') as f: train = json.load(f)
with open('../tf-class/2017-11-29-test.json') as f2: test = [a for a in json.load(f2) if a['is_confirmed'] is not None]

def predict(text):
    return int('association' in text or 'ONG' in text)

print("Score: %s" % sklearn.metrics.accuracy_score(
        [int(a['is_confirmed']) for a in test],
        [predict(a['text']) for a in test]))

for a in test:
    if not predict(a['text']) and a['is_confirmed']:
        print(a)
