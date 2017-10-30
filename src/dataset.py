
class DataSet():

    def __init__(self,
            text,
            url,
            crawled_date,
            datasource,
            author='',
            title='',
            media='',
            published_date='',
            keywords='',
            raw_text=''):
        self.text = text
        self.url = url
        self.crawled_date = crawled_date
        self.datasource = datasource
        self.title = title
        self.author = author
        self.media = media
        self.published_date = published_date
        self.keywords = keywords
        self.raw_text = raw_text

    def serialize():
        pass
