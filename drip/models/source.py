from drip.datastore import db


class Source(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(255), unique=True)

    # Keep articles on the Source so if an
    # article's feed dies, we still know where the Article came from.
    articles    = db.relationship('Article', backref='source', lazy='dynamic')
    feeds       = db.relationship('Feed', backref='source')

    def __init__(self, name):
        self.name = name
