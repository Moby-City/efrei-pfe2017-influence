#!/usr/bin/env python3

from langdetect import detect
import sys
import json

out = []
with open(sys.argv[-1], 'r') as f:
    out = [article for article in json.load(f) if detect(article['text']) == 'fr']

with open('out.json', 'w') as f:
    json.dump(out, f, indent=2)
