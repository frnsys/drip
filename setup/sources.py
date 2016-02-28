from drip.datastore import db
from drip.api import create_app
from drip.models.feed import Feed
from drip.models.source import Source


sources = {
    'The Atlantic': [
        'http://feeds.feedburner.com/AtlanticPoliticsChannel',
        'http://feeds.feedburner.com/AtlanticInternational',
        'http://feeds.feedburner.com/AtlanticNational'
    ],
    'The New York Times': [
        'http://www.nytimes.com/services/xml/rss/nyt/World.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Politics.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/US.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Africa.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Americas.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Europe.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/MiddleEast.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Education.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/Economy.xml'
    ],
    'Spiegel': [
        'http://www.spiegel.de/international/world/index.rss',
        'http://www.spiegel.de/international/europe/index.rss'
    ],
    'Foreign Policy': [
        'http://www.foreignpolicy.com/node/feed'
    ],
    'Christian Science Monitor': [
        'http://rss.csmonitor.com/feeds/politics',
        'http://rss.csmonitor.com/feeds/world',
        'http://rss.csmonitor.com/csmonitor/globalnews',
        'http://rss.csmonitor.com/feeds/usa'
    ],
    'The Guardian': [
        'http://feeds.theguardian.com/theguardian/us/rss',
        'http://feeds.theguardian.com/theguardian/world/rss'
    ],
    'The Independent': [
        'http://www.independent.co.uk/news/world/rss'
    ],
    'The Washington Post': [
        'http://feeds.washingtonpost.com/rss/politics',
        'http://feeds.washingtonpost.com/rss/world',
        'http://feeds.washingtonpost.com/rss/world/africa',
        'http://feeds.washingtonpost.com/rss/world/middle-east',
        'http://feeds.washingtonpost.com/rss/politics/federal-government',
        'http://feeds.washingtonpost.com/rss/world/europe',
        'http://feeds.washingtonpost.com/rss/world/americas',
        'http://feeds.washingtonpost.com/rss/world/war-zones',
        'http://feeds.washingtonpost.com/rss/national',
        'http://feeds.washingtonpost.com/rss/world/asia-pacific'
    ],
    'The Wall Street Journal': [
        'http://blogs.wsj.com/capitaljournal/feed/',
        'http://online.wsj.com/xml/rss/3_7085.xml',
        'http://blogs.wsj.com/emergingeurope/feed/'
    ],
    'BBC': [
        'http://feeds.bbci.co.uk/news/world/rss.xml',
        'http://feeds.bbci.co.uk/news/politics/rss.xml',
        'http://feeds.bbci.co.uk/news/world/africa/rss.xml',
        'http://feeds.bbci.co.uk/news/world/asia/rss.xml',
        'http://feeds.bbci.co.uk/news/world/europe/rss.xml',
        'http://feeds.bbci.co.uk/news/world/latin_america/rss.xml',
        'http://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
        'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml'
    ],
    'The Economist': [
        'http://www.economist.com/rss/international_rss.xml',
        'http://www.economist.com/rss/united_states_rss.xml',
        'http://www.economist.com/rss/china_rss.xml',
        'http://www.economist.com/rss/asia_rss.xml',
        'http://www.economist.com/rss/middle_east_and_africa_rss.xml',
        'http://www.economist.com/rss/the_americas_rss.xml',
        'http://www.economist.com/rss/europe_rss.xml',
        'http://www.economist.com/rss/britain_rss.xml'
    ],
    'Reuters': [
        'http://feeds.reuters.com/news/economy',
        'http://feeds.reuters.com/Reuters/PoliticsNews'
    ],
    'Al Jazeera': [
        'http://www.aljazeera.com/Services/Rss/?PostingId=2007731105943979989',
        'http://www.aljazeera.com/Services/Rss/?PostingId=2007721151816881407',
        'http://www.aljazeera.com/Services/Rss/?PostingId=200772115196613309',
        'http://www.aljazeera.com/Services/Rss/?PostingId=2007722144444234906',
        'http://www.aljazeera.com/Services/Rss/?PostingId=2007721155716791636',
        'http://www.aljazeera.com/Services/Rss/?PostingId=2007721152443657412',
        'http://www.aljazeera.com/Services/Rss/?PostingId=20121120141543822755',
        'http://www.aljazeera.com/Services/Rss/?PostingId=200861163157760548',
        'http://www.aljazeera.com/Services/Rss/?PostingId=201082875028851478'
    ],
    'NPR': [
        'http://www.npr.org/rss/rss.php?id=1012',
        'http://www.npr.org/rss/rss.php?id=1003',
        'http://www.npr.org/rss/rss.php?id=1004'
    ]
}


app = create_app()
with app.app_context():
    print('adding sources...')
    for source, feeds in sources.items():
        print('>', source)
        src = Source(source)
        db.session.add(src)

        for f in feeds:
            print('\t', f)
            fd = Feed(f, src)
            db.session.add(fd)

        db.session.commit()
