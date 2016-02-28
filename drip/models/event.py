from drip.datastore import db
from scipy.sparse import vstack
from datetime import datetime, timedelta
from drip.nlp import multisummarize, title, keywords
from drip.models.keywordable import Keywordable, Keyword
from drip.models.article import Article


class Event(Keywordable):
    event_id    = db.Column('id', db.Integer, db.ForeignKey('keywordable.id'), primary_key=True)
    articles    = db.relationship('Article', backref='event', lazy='dynamic', foreign_keys=[Article.event_id])
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)
    story_id    = db.Column(db.Integer, db.ForeignKey('story.id'))
    title       = db.Column(db.Unicode)
    summary     = db.Column(db.UnicodeText)

    def __init__(self, article):
        self.articles = [article]
        self.created_at = article.published
        self.update()

    def add(self, article):
        self.articles.append(article)

    @property
    def vecs(self):
        return vstack([a.vec for a in self.articles])

    @property
    def age(self):
        return datetime.utcnow() - self.created_at

    @property
    def summary_pts(self):
        return self.summary.split('\n')

    @property
    def text(self):
        return '\n'.join([a.text for a in self.articles])

    def update(self):
        self.summary = '\n'.join(multisummarize(self.articles))
        self.title = title(self.articles)
        self.keywords = [Keyword.find_or_create(name=kw) for kw, score in keywords(self.articles)]

        # Set oldest published date as this event's date
        self.created_at = min([a.published for a in self.articles])

    @classmethod
    def candidates(cls, dt):
        """return "active" events - those that are not too old given a datetime `dt`"""
        return cls.query.filter(dt - Event.created_at < timedelta(hours=36)).all()

    def as_dict(self):
        whitelist = ['id', 'title', 'created_at', 'updated_at', 'story_id']
        data = {attr: getattr(self, attr) for attr in whitelist}
        data['summary'] = self.summary.split('\n')
        data['articles'] = [a.as_dict() for a in self.articles]
        data['keywords'] = [k.as_dict() for k in self.keywords]
        return data
