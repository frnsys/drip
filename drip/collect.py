import logging
from itertools import groupby
from drip.datastore import db
from drip.models import Feed, Event
from drip.cluster import cluster, storify
from xml.sax._exceptions import SAXException

logger = logging.getLogger(__name__)


def collect():
    """
    Fetch articles from the feeds.
    """
    new_articles = []
    for feed in Feed.query.all():
        try:
            logger.info('Fetching from {0}...'.format(feed.url))
            for article in feed.get_articles():
                db.session.add(article)
                db.session.commit()
                new_articles.append(article)

        except SAXException:
            # Error with the feed, make a note.
            logger.error('Error fetching from {0}.'.format(feed.url))
            feed.errors += 1
            db.session.commit()

    logger.info('Clustering {} new articles...'.format(len(new_articles)))

    # Group articles by day
    events = []
    for dt, group in groupby(new_articles, key=lambda a: a.published.date()):
        new_events = cluster(group, Event.candidates(dt))
        events += new_events
    storify(events)
