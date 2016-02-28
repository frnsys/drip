import newspaper
import feedparser
from dateutil import parser
from datetime import datetime
from drip.models import Article
from drip.datastore import db
from nltk.tokenize import word_tokenize


class Feed(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    url         = db.Column(db.Unicode)
    errors      = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)
    articles    = db.relationship('Article', backref='feed', lazy='dynamic')
    source_id   = db.Column(db.Integer, db.ForeignKey('source.id'))

    def __init__(self, url, source):
        self.url = url
        self.source = source
        self.errors = 0

    def get_articles(self):
        data = feedparser.parse(self.url)

        # If the `bozo` value is anything
        # but 0, there was an error parsing (or connecting) to the feed.
        if data.bozo:
            # Some errors are ok.
            if not isinstance(data.bozo_exception, feedparser.CharacterEncodingOverride) \
                    and not isinstance(data.bozo_exception, feedparser.NonXMLContentType):
                raise data.bozo_exception

        for entry in data.entries:
            url = entry['links'][0]['href']

            # Check for an existing Article.
            # If one exists, skip.
            if Article.query.filter_by(url=url).count() or Article.query.filter_by(source=self.source, title=entry['title']).count():
                continue

            a_data = fetch(url)
            if a_data is None:
                continue
            a_data['feed'] = self

            # Although `newspaper` can extract published datetimes using metadata,
            # generally the published datetime included with the RSS entry will
            # be more precise (and sometimes `newspaper` does not successfully
            # extract a published datetime).
            # (see https://github.com/codelucas/newspaper/blob/41b930b467979577710b86ecb93c2a952e5c9a0d/newspaper/extractors.py#L166)
            if 'published' in entry:
                a_data['published'] = parser.parse(entry['published'])

            # Skip empty or short articles (which may be 404 pages)
            if a_data is None \
                or len(word_tokenize(a_data['text'])) <= 150:
                continue

            yield Article(**a_data)


def fetch(url):
    """fetch article data for a given url"""
    a = newspaper.Article(url, keep_article_html=True)
    a.download()

    # Was unable to download, skip
    if not a.is_downloaded:
        return

    a.parse()

    data = {
        'url': a.url,
        'title': a.title,
        'text': a.text,
        'html': a.article_html,
        'image': a.top_image,
        'published': a.publish_date,
        'authors': a.authors,
        'keywords': a.keywords + a.meta_keywords
    }

    return data
