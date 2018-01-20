import glob
import sys
import json

with open('concat', 'w') as outfile:
    for filename in sys.argv[1:]:
        with open(filename) as f:
            data = json.load(f)
            for d in data:
                outfile.write(d['text'].replace('\n', ' ') + '\n')
