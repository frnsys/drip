import re
from .keywords import keywords
from .shared import global_term_idf
from drip.preprocess import clean, lemma_tokenize, IDF

sanitize_re = re.compile(r'(^.+:\s?)?(.+)(\(.+\)$)?')


def sanitize_title(title):
    """
    Titles often include the blog name in a pattern like so:

        Blog Name: The title

    Or, for videos, they often include '(video)' or something similar
    at the end:

        The title (video)

    This function cleans those up.
    """
    title = sanitize_re.sub(r'\2', title).strip()
    title = title[0].upper() + title[1:]
    return title


def title(articles):
    # Just return the title if there's only one article
    if (isinstance(articles, list) and len(articles) == 1) or \
            (not isinstance(articles, list) and articles.count() == 1):
        return sanitize_title(articles[0].title)

    # compute term idfs
    token_docs = [lemma_tokenize(clean(a.text)) for a in articles]
    local_term_idf = IDF(token_docs)

    titles = [sanitize_title(a.title) for a in articles]
    title_tokens = [lemma_tokenize(clean(t)) for t in titles]
    kws = {kw: score for kw, score in keywords(articles)}
    mxm = max(kws.values())
    for kw in kws.keys():
        kws[kw] = kws[kw]/mxm

    title_scores = []
    for i, t in enumerate(title_tokens):
        score = sum(global_term_idf[tok] - local_term_idf[tok] for tok in t)
        for tok in t:
            if tok in kws:
                score += kws[tok]
        ideal = 8
        length_penalty = (ideal - abs(ideal-len(t)))/ideal
        title_scores.append((titles[i], score/len(t) * length_penalty))

    return sorted(title_scores, key=lambda t: t[1], reverse=True)[0][0]
