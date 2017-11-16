class Organization():

    def __init__(self,
            title, 
            url,
            description='',
            articles=[]):
        self.title = title
        self.url = url
        self.description = description
        self.articles = articles
