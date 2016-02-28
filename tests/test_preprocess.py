import unittest
from drip.preprocess import clean, lemma_tokenize, IDF


class PreProcessTests(unittest.TestCase):
    def test_clean(self):
        doc = '''
        Goats are like mushrooms. If you shoot a duck, I'm scared of toasters. My site's are https://google.com.
        '''
        expected_doc = '''
        goats are like mushrooms if you shoot a duck im scared of toasters my site are
        '''
        self.assertEqual(clean(doc), expected_doc.strip())

    def test_html_clean(self):
        doc = '''
        <html>goats are like <b>mushrooms</b> if you shoot a duck <em>im scared of toasters</em> my site are<div></div></html>
        '''
        expected_doc = '''
        goats are like mushrooms if you shoot a duck im scared of toasters my site are
        '''
        self.assertEqual(clean(doc), expected_doc.strip())

    def test_lemma(self):
        docs = [
            'This cat dog is running happy.',
            'This cat dog runs sad.'
        ]
        expected_t_docs = [
            ['cat', 'dog', 'run', 'happy', '.'],
            ['cat', 'dog', 'run', 'sad', '.']
        ]
        t_docs = [lemma_tokenize(d) for d in docs]
        self.assertEqual(t_docs, expected_t_docs)

    def test_idf(self):
        token_docs = [
            ['cat', 'dog', 'run', 'happy', '.'],
            ['cat', 'dog', 'run', 'sad', '.']
        ]
        idf = IDF(token_docs)
        print(idf.idf)