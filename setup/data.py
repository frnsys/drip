import os
import json
import joblib
from time import time
from glob import glob
from joblib import Parallel, delayed
from drip.preprocess import BoWVectorizer, IDF, clean, lemma_tokenize


def prepare_documents():
    doc_dir = os.path.expanduser('~/data/nyt/articles/bodies/')
    print('preparing documents...')
    files = glob(os.path.join(doc_dir, '*.txt'))
    cleaned = Parallel(n_jobs=-1)(delayed(clean)(d) for d in files_stream(files))
    return cleaned


def train_vectorizer(docs):
    print('training vectorizer...')
    vectorizer = BoWVectorizer(min_df=1, max_df=1.)
    vectorizer.train(docs)
    joblib.dump(vectorizer, '../data/nyt_bow_vectorizer.pkl')


def train_idf(docs):
    print('training idf...')
    token_docs = [lemma_tokenize(doc) for doc in docs]
    idf = IDF(token_docs).idf
    with open('../data/nyt_idf_lemma.json', 'w') as f:
        json.dump(idf, f)


def doc_stream(path):
    """generator to feed tokenized documents (treating each line as a document)"""
    with open(path, 'r') as f:
        for line in f:
            if line.strip():
                yield line


def files_stream(files):
    """stream lines from multiple files"""
    for file in files:
        for line in doc_stream(file):
            yield line


if __name__ == '__main__':
    s = time()
    docs = prepare_documents()
    train_vectorizer(docs)
    train_idf(docs)
    print('took {:.2f}s'.format(time() - s))