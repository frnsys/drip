from .tokenize import lemma_tokenize
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer, HashingVectorizer


class BoWVectorizer():
    def __init__(self, min_df=1, max_df=0.9, tokenizer=lemma_tokenize, hash=False):
        """
        `min_df` is set to filter out extremely rare words,
        since we don't want those to dominate the distance metric.

        `max_df` is set to filter out extremely common words,
        since they don't convey much information.
        """

        kwargs = {
            'input': 'content',
            'stop_words': 'english',
            'lowercase': True,
            'tokenizer': tokenizer
        }
        if hash:
            vectr = HashingVectorizer(**kwargs)
        else:
            vectr = CountVectorizer(min_df=min_df, max_df=max_df, **kwargs)

        args = [
            ('vectorizer', vectr),
            ('tfidf', TfidfTransformer(norm=None, use_idf=True, smooth_idf=True)),
            ('normalizer', Normalizer(copy=False))
        ]

        self.pipeline = Pipeline(args)
        self.trained = False

    def vectorize(self, docs):
        if not self.trained:
            return self.train(docs)
        return self.pipeline.transform(docs)

    def train(self, docs):
        self.trained = True
        return self.pipeline.fit_transform(docs)

    @property
    def vocabulary(self):
        return self.pipeline.named_steps['vectorizer'].get_feature_names()
