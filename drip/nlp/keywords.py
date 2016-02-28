import re
from collections import defaultdict
from .shared import global_term_idf
from drip.preprocess import clean, lemma_tokenize, IDF


def extract_phrases(tdocs, docs, idf):
    """learn novel phrases by looking at co-occurrence of candidate term pairings;
    docs should be input in tokenized (`tdocs`) and untokenized (`docs`) form"""
    # Gather existing keyphrases
    keyphrases = set()
    for doc in tdocs:
        for t in doc:
            if len(t.split(' ')) > 1:
                keyphrases.add(t)

    # Count document co-occurrences
    t_counts = defaultdict(int)
    pair_docs = defaultdict(list)
    for i, terms in enumerate(tdocs):
        # We dont convert the doc to a set b/c we want to preserve order
        # Iterate over terms as pairs
        for pair in zip(terms, terms[1:]):
            t_counts[pair] += 1
            pair_docs[pair].append(i)

    # There are a lot of co-occurrences, filter down to those which could
    # potentially be phrases.
    t_counts = {kw: count for kw, count in t_counts.items() if count >= 2}

    # Identify novel phrases by looking at
    # keywords which co-occur some percentage of the time.
    # This could probably be more efficient/cleaned up
    for (kw, kw_), count in t_counts.items():
        # Only consider terms above a certain avg global IDF (to reduce noise)
        if (idf[kw]+idf[kw_])/2 <= 0.4:
            continue

        # Look for phrases that are space-delimited or joined by 'and' or '-'
        ph_reg = re.compile('({0}|{1})( |-)(and )?({0}|{1})'.format(kw, kw_))

        # Extract candidate phrases and keep track of their counts
        phrases = defaultdict(int)
        phrase_docs = defaultdict(set)
        for i in pair_docs[(kw, kw_)]:
            for m in ph_reg.findall(docs[i].lower()):
                phrases[''.join(m)] += 1
                phrase_docs[''.join(m)].add(i)

        if not phrases:
            continue

        # Get the phrase encountered the most
        top_phrase = max(phrases.keys(), key=lambda k: phrases[k])
        top_count = phrases[top_phrase]

        # Only count phrases that appear in _every_ document
        if top_count/count == 1:
            # Check if this new phrase is contained by an existing keyphrase.
            if any(top_phrase in ph for ph in keyphrases):
                continue
            keyphrases.add(top_phrase)

            # Add the new phrase to each doc it's found in
            for i in phrase_docs[top_phrase]:
                tdocs[i].append(top_phrase)

    return tdocs, keyphrases


def keywords(articles, top_n=25):
    """returns `top_n` keywords for a list of articles.
    keywords are returned as (keyword, score) tuples.
    """

    # compute term idfs
    token_docs = [lemma_tokenize(clean(a.text)) for a in articles]
    local_term_idf = IDF(token_docs)

    token_docs, phrases = extract_phrases(token_docs, [a.text for a in articles], global_term_idf)

    titles = [a.title for a in articles]
    title_tokens = [lemma_tokenize(clean(t)) for t in titles]
    term_counts = defaultdict(int)
    for doc in token_docs:
        for t in set(doc):
            if t:
                term_counts[t] += 1

    title_terms = set()
    for title_tks in title_tokens:
        title_terms = title_terms | set(title_tks)
    for ph in phrases:
        if any(ph in title.lower() for title in titles):
            title_terms.add(ph)

    # Score terms
    term_scores = []
    for t, count in term_counts.items():
        # Ignore numbers, they are very specific to a particular event and
        # introduce noise
        try:
            float(t)
            continue
        except ValueError:
            # TODO This is a troublesome token, not sure why it's not filtered out by
            # IDF. needs more investigation
            if t == 'n\'t':
                continue
            score = count * (global_term_idf[t] - local_term_idf[t])
            if t in title_terms:
                score *= 1.5
            term_scores.append((t, score))

    return sorted(term_scores, key=lambda t: t[1], reverse=True)[:top_n]
