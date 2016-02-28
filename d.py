import click
import logging
from functools import wraps
# from logging import handlers
from drip.datastore import db
from drip.api import create_app
from drip.models import Article, Story, Event
from drip.collect import collect

# email = {}
# mailHandler = handlers.SMTPHandler(
    # (email['host'], email['port']),
    # email['user'], email['admins'], 'drip error',
    # credentials=(email['user'], email['pass']),
    # secure=()
# )
# mailHandler.setLevel(logging.ERROR)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/drip.log'),
        # handlers.RotatingFileHandler('/tmp/drip.log', maxBytes=500000, backupCount=5)
    ])
# logging is hierarchical, so this sets the level
# for all loggers named 'drip.<something>'
logging.getLogger('drip').setLevel(logging.INFO)


def requires_app(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        app = create_app()
        with app.app_context():
            f(*args, **kwargs)
    return wrapper


@click.group()
def cli():
    pass


@cli.command()
@requires_app
def update():
    """collects latest articles from all feeds"""
    collect()


@cli.command()
@requires_app
def remove_duplicates():
    """removes duplicate articles (by title)"""
    titles = set()
    click.echo('articles (before): {}'.format(Article.query.count()))
    for a in Article.query.all():
        if a.title in titles:
            db.session.delete(a)
        titles.add(a.title)
    db.session.commit()
    click.echo('articles (after): {}'.format(Article.query.count()))


@cli.command()
@requires_app
def count():
    """count articles, events, and stories"""
    click.echo('articles: {}'.format(Article.query.count()))
    click.echo('events: {}'.format(Event.query.count()))
    click.echo('stories: {}'.format(Story.query.count()))


@cli.command()
@requires_app
def preview():
    """preview stories and events"""
    for s in Story.query.all():
        if s.events.count() > 1:
            click.echo('--STORY----------')
            for e in s.events:
                click.echo('\t{}'.format(e.title))
                for a in e.articles:
                    click.echo('\t\t{}'.format(a.title))
    click.echo('\n-------------\n')
    for e in Event.query.all():
        if e.articles.count() > 1:
            click.echo('--EVENT----------')
            click.echo('\t{}'.format(e.title))
            for a in e.articles:
                click.echo('\t\t{}'.format(a.title))


@cli.command()
def api():
    """start the api server"""
    app = create_app()
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    cli()