
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
            raw_text='',
            extra={}):
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
        self.is_confirmed = None
        self.extra = extra

    def serialize(self):
        pass

    def set_extra(self, key, value):
        self.extra[key] = value

    def put_extras_to(self, dest):
        for key in self.extra:
            dest[key] = self.extra[key]
