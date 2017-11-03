/orgranization.py
class Organization():

    def __init__(self,
            title, 
            description='',
            articles=[]):
        self.title = title
        self.description = description
        self.articles = articles
