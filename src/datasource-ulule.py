from datasource import DataSource
import re
import httplib
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup


"""
DataSource Class for Ulule.com
Update:
- Ulule API only works for own projects

"""
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class DataSourceUlule():

    def __init__(self,searchterms):
        self.URL           = 'https://www.ulule.com/discover/'
        self.SEARCH_URL    = self.URL+'?q='
        self.apikey        = '0c7364d43e84e99fccdefac66405e0480ac06900'
        self.searchterms   = searchterms
        self.crawled_hrefs = []

    # Check if URL matches all requirements for being a real URL
    # @return: TRUE if url meets regex requirements
    def isValidUrl(self,url):
        if regex.match(url) is not None:
            return True;
        return False

    # Crawls webpage for every defined searchterm
    # @return: list of all crawled URLs
    def crawler(self):

        crawled = []

        for term in self.searchterms:

            tocrawl = [self.SEARCH_URL + term]

            while tocrawl:

                page = tocrawl.pop()

                print 'Crawled:' + page

                pagesource = urllib2.urlopen(page)
                s = pagesource.read()

                soup = BeautifulSoup(s, "html5lib")

                # find all ulule project hrefs
                # b-blink__link html class for projects
                #rawLinks = soup.findAll('a', href=True, class_="b-blink__link")


                # find next page in search results
                #nextPage = soup.findAll('a', href=True, class_="page")[0]

                links = soup.findAll('a', href=True)

                # Crawling deeper with found hrefs
                if page not in crawled:
                    for l in links:
                        if self.isValidUrl(l['href']):
                            tocrawl.append(l['href'])

                    crawled.append(page)

        return crawled

'''
Testing
'''
searchterms = ['ngo']

obj = DataSourceUlule(searchterms)

obj.crawler()

print "done."





