import logging
import numpy as np
from time import time
from scipy.spatial.distance import cdist
from drip.datastore import db
from drip.models import Story, Event

logger = logging.getLogger(__name__)


def cluster(articles, events):
    # TODO should there be a re-assignment pass?
    articles = list(articles)
    n = len(articles)
    logger.info('Clustering {}'.format(n))

    updated_events = set()
    for article in articles:
        vec = article.vec

        s = time()
        cands = candidates(vec, events)
        print('\tcomputing candidates took {:.2f}s'.format(time() - s))
        if cands:
            cands[0].add(article)
            updated_events.add(cands[0])
        else:
            s = time()
            event = Event(article)
            print('\tcreating new event took {:.2f}s'.format(time() - s))
            db.session.add(event)
            events.append(event)
            updated_events.add(event)

        # clusters could "soft expire" in which the threshold to join is placed
        # higher, or maybe the threshold to join is placed higher over time)

        # once a cluster has > 3 members, we can try to cluster it with other event
        # clusters

    for e in updated_events:
        e.update()
    db.session.commit()

    return events


def storify(events):
    updated_stories = set()
    for e in events:
        if e.story is None and e.articles.count() >= 2:
            candidates = Story.candidates(e)

            # Create as own story if no candidates
            if not candidates:
                story = Story(e)
                updated_stories.add(e)
                db.session.add(story)
            else:
                top_cand, score = candidates[0]

                # TODO adjust this score - determine a good cutoff
                if score >= 3.:
                    top_cand.add(e)
                    top_cand.update()
                    updated_stories.add(top_cand)
                # Create new story otherwise
                else:
                    story = Story(e)
                    updated_stories.add(e)
                    db.session.add(story)
    db.session.commit()
    return updated_stories


def similarity(vec, clus):
    """similarity of a vector to a cluster, using mean linkage"""
    if not clus:
        return 0
    # TODO my guess is the slowdown is constantly recomputing clus.vecs
    # the cluster objects should cache `clus._vecs` and only update when
    # a new article is added (and then it needs only to calculate the latest
    # article vector and vstack it)
    dist = np.mean(cdist(vec.todense(), clus.vecs.todense(), metric='cosine'))
    return 1 - np.square(dist)


def candidates(vec, clusters, min_sim=0.55):
    """
    Return candidate clusters, sorted by strongest similarity.

    This min similarity was determined by analyzing the distributions of
    non-cocluster article similarities and cocluster article similarities.
    """
    # TODO this is slow
    sims = []
    for c in clusters:
        sim = similarity(vec, c)
        if sim < min_sim:
            continue
        else:
            sims.append((c, sim))
    return [c for c, s in sorted(sims, key=lambda p: p[1], reverse=True)]
