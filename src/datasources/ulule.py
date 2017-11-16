from datasource import DataSource
from dataset import DataSet
import re
import json
import urllib3
import newspaper
from bs4 import BeautifulSoup
from datetime import datetime, date
import sys

http = urllib3.PoolManager()

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj.__dict__

class DataSourceUlule():

  def __init__(self):
    self.URL           = 'https://www.ulule.com/discover/'
    self.SEARCH_URL    = self.URL+'?q='
    self.URL_BASE = 'https://fr.ulule.com'

  # Crawls webpage for every defined searchterm
  # @return: list of all crawled URLs
  def findAll(self):
    all_projects = []
    next_url = self.URL_BASE + '/discover/all/'

    # step 1: gather all project names and links
    page = 1
    while page < 5:
      print('Fetching page ' + str(page))
      page = page + 1
      s = http.request('GET', next_url).data.decode('utf-8')
      soup = BeautifulSoup(s, 'html.parser')

      projects = soup.select('a.b-blink__link')
      now = datetime.now()
      for project in projects:
        title = project.select_one('h2.b-blink__title').text.strip()
        author = project.select_one('.b-blink__author').text.strip()
        all_projects.append(DataSet(None, project['href'], now, self, author, title))

      # find next page url
      next_link = soup.select_one('#results-footer li.active + li a')
      if not next_link:
        break
      else:
        next_url = self.URL_BASE + next_link['href']

    # step 2: load each project description page and gather its description
    for project in all_projects:
      print('Download info for ' + project.url)
      na = newspaper.Article(project.url)
      na.download()
      na.parse()
      project.text = na.text
      project.media = na.top_image
      project.author = ', '.join(na.authors)
      project.published_date = na.publish_date

    self.writeProjectList(all_projects, sys.path[0] + '/../output/ulule.json')

  def writeProjectList(self, projects, filename):
    """writes the given array of organizations to filename in json format"""
    f = open(filename, 'w')
    f.write(json.dumps(projects, default=json_serial))


'''
Testing
'''
obj = DataSourceUlule()

obj.findAll()
