from drip.preprocess import clean
from drip.nlp.shared import vectorizer
from drip.datastore import db, join_table
from drip.models.keywordable import Keywordable, Keyword

articles_authors = join_table('articles_authors', 'article', 'author')


class Article(Keywordable):
    article_id    = db.Column('id', db.Integer, db.ForeignKey('keywordable.id'), primary_key=True)
    url         = db.Column(db.Unicode)
    title       = db.Column(db.Unicode)
    text        = db.Column(db.UnicodeText)
    html        = db.Column(db.UnicodeText)
    image       = db.Column(db.String)
    score       = db.Column(db.Float, default=0.0)
    published   = db.Column(db.DateTime)
    source_id   = db.Column(db.Integer, db.ForeignKey('source.id'))
    feed_id     = db.Column(db.Integer, db.ForeignKey('feed.id'))
    event_id    = db.Column(db.Integer, db.ForeignKey('event.id'))
    authors     = db.relationship('Author',
                    secondary=articles_authors,
                    backref=db.backref('articles', lazy='dynamic'))

    def __init__(self, url, title, text, html, image, published, authors, keywords, feed):
        self.url = url
        self.text = text
        self.html = html
        self.title = title
        self.image = image
        self.published = published
        self.authors = [Author.find_or_create(name=name) for name in authors]
        self.keywords = [Keyword.find_or_create(name=kw) for kw in set(keywords)]
        self.feed = feed
        self.source = feed.source

    @property
    def vec(self):
        # TODO for now, not storing vec - need to setup pytables or something similar
        cleaned = clean('\n'.join([self.title, self.text]))
        return vectorizer.vectorize([cleaned])[0]


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)

    def __init__(self, name):
        self.name = name

    @classmethod
    def find_or_create(cls, **kwargs):
        obj = cls.query.filter_by(**kwargs).first()
        if obj is None:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        return obj
