import sys
import os

from flask import Flask
from flask import jsonify

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

from crawl.datasources.twitter import DataSourceTwitter
from crawl.datasources.facebook import DataSourceFacebook

app = Flask(__name__)

def serializeDataset(dataset):
  s = {
    'text': dataset.text,
    'media': dataset.media,
    'url': dataset.url,
    'date': dataset.published_date,
  }
  dataset.put_extras_to(s)
  return s

@app.route("/facebook/<id>")
def facebook(id):
  return jsonify([serializeDataset(d) for d in DataSourceFacebook().get_all_for(id)])

@app.route("/twitter/<handle>")
def twitter(handle):
  if handle[0] != '@':
    handle = '@' + handle

  data = DataSourceTwitter().get_all_for(handle)
  return jsonify([serializeDataset(d) for d in data])

