import re
import string
from html.parser import HTMLParser

# Don't replace dashes.
# Everything else is replaced with a space in case no space is around the
# punctuation (which would cause unwanted term merging)
punct = (string.punctuation + '“”–').replace('-', '')
strip_map = {ord(p): '' for p in '\''}
punct_map = {ord(p): ' ' for p in punct}
url_re = re.compile(r'https?:\/\/.*[\r\n]*', flags=re.MULTILINE)
whs_re = re.compile(r'\s{2,}')


def clean(doc, remove_html=True, remove_urls=True, lowercase=True, remove_possessors=True, remove_punctuation=True):
    if lowercase:
        doc = doc.lower()

    if remove_html:
        doc = strip_html(doc)

    if remove_urls:
        # Remove URLs
        doc = url_re.sub('', doc)

    if remove_possessors:
        doc = doc.replace('\'s ', ' ')

    if remove_punctuation:
        doc = strip_punct(doc)

    return doc.strip()


def strip_punct(doc):
    doc = doc.translate(strip_map).translate(punct_map)

    # Collapse whitespace to single whitespace
    return whs_re.sub(' ', doc)


def decode_html(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    from: <http://stackoverflow.com/a/275246/1097920>
    """
    for code in (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        ):
        s = s.replace(code[1], code[0])
    return s


def strip_html(html):
    # Any unwrapped text is ignored,
    # so wrap html tags just in case.
    # Looking for a more reliable way of stripping HTML...
    html = '<div>{0}</div>'.format(html)
    s = HTMLStripper()
    s.feed(html)

    # Stripping HTML adds additional whitespace, clean it up
    cleaned = s.get_data().strip()
    return whs_re.sub(' ', cleaned)


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)
