from .shared import spacy
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

stopwords = stopwords.words('english')
lemmatizer = WordNetLemmatizer()


def lemma_tokenize(doc):
    toks = []

    for t in spacy(doc, tag=True, parse=False, entity=False):
        token = t.lower_.strip()
        tag = t.tag_

        # Ignore stopwords
        if token in stopwords:
            continue

        # Lemmatize
        wn_tag = penn_to_wordnet(tag)
        if wn_tag is not None:
            lemma = lemmatizer.lemmatize(token, wn_tag)
            toks.append(lemma)
        else:
            toks.append(token)
    return toks


def penn_to_wordnet(tag):
    """
    Convert a Penn Treebank PoS tag to WordNet PoS tag.
    """
    if tag in ['NN', 'NNS', 'NNP', 'NNPS']:
        return 'n' #wordnet.NOUN
    elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
        return 'v' #wordnet.VERB
    elif tag in ['RB', 'RBR', 'RBS']:
        return 'r' #wordnet.ADV
    elif tag in ['JJ', 'JJR', 'JJS']:
        return 'a' #wordnet.ADJ
    return None
