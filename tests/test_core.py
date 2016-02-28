import json
from datetime import datetime
from drip.datastore import db
from drip.cluster import cluster
from drip.nlp import title, multisummarize
from drip.models import Event, Story, Article, Feed, Source, Keyword
from tests import TestCase


class CoreTest(TestCase):
    def setUp(self):
        self.events = json.load(open('tests/data/events.json', 'r'))
        self.source = Source('test source')
        self.feed = Feed('http://nytimes.com', self.source)
        db.session.add(self.source)
        db.session.add(self.feed)
        db.session.commit()

    def article_factory(self, **kwargs):
        defaults = {
            'url': 'http://nytimes.com/sup',
            'text': 'sup',
            'html': '<h1>sup</h1>',
            'title': 'Sup',
            'image': 'http:://nytimes.com/sup.jpg',
            'published': datetime(day=1, month=1, year=2015),
            'authors': ['Yo Go'],
            'keywords': ['sup', 'yo'],
            'feed': self.feed
        }
        defaults.update(kwargs)
        return Article(**defaults)

    def test_title(self):
        expected = [
            'Jeremy Thorpe, former Liberal party leader, dies aged 85',
            'Woman Arrested in U.S. Teacher\'s Stabbing Death in Abu Dhabi',
            'Faces keyboardist Ian McLagan dies',
            'China to stop using executed prisoners as source of organs for transplant',
            'James Bond movie to be called Spectre'
        ]

        for e, expected in zip(self.events, expected):
            articles = [self.article_factory(title=a['title'], text=a['text']) for a in e]
            t = title(articles)
            self.assertEqual(t, expected)

    def test_cluster(self):
        articles = []
        true_events = []

        for e in self.events:
            arts = [self.article_factory(title=a['title'], text=a['text']) for a in e]
            true_events.append(arts)
            articles += arts

        clusters = cluster(articles, [])

        # Clusters might not be in the same order as the true events
        for clus in clusters:
            for evs in true_events:
                if set(clus.articles) == set(evs):
                    break
            else:
                self.fail('Cluster:\n\t{}\ndid not match any expected cluster'.format(
                    [a.title for a in clus.articles]
                ))

    def test_summarize(self):
        articles = []

        for e in self.events:
            articles = [self.article_factory(title=a['title'], text=a['text']) for a in e]
            summary = multisummarize(articles)

            # This is more of a placeholder test atm
            self.assertTrue(isinstance(summary, list))

    def test_keywords(self):
        data = [
            ('This is a title: Spectre', 'The story is about Spectre'),
            ('A really cool title', 'Spectre is the new film'),
            ('Yet another title', 'The new title is Spectre')
        ]
        events = []
        articles = []
        for _ in range(2):
            arts = [self.article_factory(title=title, text=text, keywords=['spectre']) for title, text in data]
            event = Event(arts[0])
            for a in arts[1:]:
                event.add(a)
            event.update()
            articles += arts
            events.append(event)
            db.session.add(event)

        story = Story(events[0])
        story.add(events[1])
        story.update()
        db.session.add(story)
        db.session.commit()

        keyword = Keyword.query.filter_by(name='spectre').first()
        self.assertEqual(set(keyword.subjects.all()), set(articles + events + [story]))

    def test_story_candidates(self):
        data = [
            ('This is a title: Spectre', 'The story is about Spectre'),
            ('A really cool title', 'Spectre is the new film'),
            ('Yet another title', 'The new title is Spectre')
        ]
        events = []
        articles = []
        for _ in range(3):
            arts = [self.article_factory(title=title, text=text, keywords=['spectre']) for title, text in data]
            event = Event(arts[0])
            for a in arts[1:]:
                event.add(a)
            event.update()
            articles += arts
            events.append(event)
            db.session.add(event)

        story = Story(events[0])
        story.add(events[1])
        story.update()
        db.session.add(story)
        db.session.commit()

        event = events[-1]
        candidates = Story.candidates(event)
        self.assertEqual(candidates[0][0], story)
