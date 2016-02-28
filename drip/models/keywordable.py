from drip.datastore import db, join_table
from sqlalchemy.ext.declarative import declared_attr

keywordables_keywords = join_table('keywordables_keywords', 'keywordable', 'keyword')


class Keywordable(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    type        = db.Column('type', db.String(50))

    @declared_attr
    def keywords(cls):
        return db.relationship('Keyword',
                               secondary=keywordables_keywords,
                               backref=db.backref('subjects', lazy='dynamic'))
    @declared_attr
    def __mapper_args__(cls):
        if cls.__name__ == 'Keywordable':
            return {
                    'polymorphic_on': cls.type,
                    'polymorphic_identity': 'Keywordable'
            }
        else:
            return {
                'polymorphic_identity': cls.__name__
            }

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Keyword(db.Model):
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
