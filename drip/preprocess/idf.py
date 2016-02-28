import math
from collections import Counter
from toolz.itertoolz import concat


class IDF():
    def __init__(self, input, split_phrases=False, pretrained=False):
        """`input` should be a list of token documents.
        If `pretrained=True`, then `input` should be a pre-trained IDF dictionary"""
        self.idf = input if pretrained else train_idf(input)
        self.mxm = max([v for k, v in self.idf.items() if k != '_n_docs'])
        self.split_phrases = split_phrases

        # TODO It's possible that the maximum is 0 if we are working with
        # a set of identical articles. This is a temporary fix; there should
        # be something upstream to discard duplicate articles
        if self.mxm == 0:
            self.mxm = 1

    def __getitem__(self, key):
        try:
            return self.idf[key]/self.mxm
        except KeyError:
            if self.split_phrases:
                parts = key.split(' ')
                if len(parts) > 1:
                    return sum(self[p] for p in parts)/len(parts)
            N = self.idf['_n_docs'] + 1
            return math.log(N/1)/self.mxm


def train_idf(tokens_stream, **kwargs):
    """train a IDF model on a list of files"""

    # we don't care about frequency, just unique tokens
    idfs = [set(tokens) for tokens in tokens_stream]
    N = len(idfs) # n docs
    idf = Counter(concat(idfs))

    for k, v in idf.items():
        idf[k] = math.log(N/v)
        # v ~= N/(math.e ** idf[k])

    # Keep track of N to update IDFs
    idf['_n_docs'] = N
    return idf
