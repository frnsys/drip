from datetime import datetime
from scipy.sparse import vstack
from collections import defaultdict
from drip.datastore import db
from drip.nlp import keywords
from drip.nlp.shared import global_term_idf
from drip.models.event import Event
from drip.models.keywordable import Keywordable, Keyword


class Story(Keywordable):
    story_id    = db.Column('id', db.Integer, db.ForeignKey('keywordable.id'), primary_key=True)
    events      = db.relationship('Event', backref='story', lazy='dynamic', foreign_keys=[Event.story_id])
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, event):
        self.events = [event]
        self.update()

    def add(self, event):
        self.events.append(event)

    @property
    def vecs(self):
        return vstack([e.vec for e in self.events])

    @property
    def age(self):
        return datetime.utcnow() - self.created_at

    def update(self):
        #self.summary = multisummarize(self.articles)
        #self.title = title(self.articles)
        self.keywords = [Keyword.find_or_create(name=kw) for kw, score in keywords(self.events)]

    @classmethod
    def candidates(cls, event):
        """search stories to find candidates for the event"""
        # TODO this could be made more efficient
        candidates = defaultdict(float)
        for kw in event.keywords:
            for s in kw.subjects:
                if not isinstance(s, cls):
                    continue
                candidates[s] += global_term_idf[kw.name]
        return sorted(candidates.items(), key=lambda t: t[1], reverse=True)

    def as_dict(self):
        whitelist = ['id', 'created_at', 'updated_at']
        data = {attr: getattr(self, attr) for attr in whitelist}
        data['events'] = [e.as_dict() for e in self.events]
        data['keywords'] = [k.as_dict() for k in self.keywords]
        return data
