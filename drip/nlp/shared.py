# Load these once and share to reduce memory usage
import json
import joblib
from drip.preprocess import IDF

idf_path = 'data/nyt_idf_lemma.json'
idf = json.load(open(idf_path, 'r'))
global_term_idf = IDF(idf, split_phrases=True, pretrained=True)

# BoW Vectorizer trained on NYT corpus
vectr_path = 'data/nyt_bow_vectorizer.pkl'
vectorizer = joblib.load(vectr_path)
