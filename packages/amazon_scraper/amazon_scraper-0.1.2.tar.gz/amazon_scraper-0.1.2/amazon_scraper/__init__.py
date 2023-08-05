# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import urlparse
import urllib
from HTMLParser import HTMLParser
from amazon.api import AmazonAPI


_extract_asin_regexp = re.compile(r'/dp/(?P<asin>[^/]+)')
def extract_asin(url):
    match = _extract_asin_regexp.search(url)
    return str(match.group('asin'))

def product_url(asin):
    url = 'http://www.amazon.com/dp/{asin}'
    return url.format(asin=asin)

def add_affiliate(url, affiliate):
    return add_query(url, tag=affiliate)

def reviews_url(asin):
    url = 'http://www.amazon.com/product-reviews/{asin}/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending'
    return url.format(asin=asin)

def review_url(id):
    url = 'http://www.amazon.com/review/{id}'
    return url.format(id=id)

_process_rating_regexp = re.compile(r'([\d\.]+) out of [\d\.]+ stars', flags=re.I)
def process_rating(text):
    """The rating normalised to 1.0
    """
    rating_match = _process_rating_regexp.search(text)
    return float(rating_match.group(1)) / 5.0

_extract_review_id_regexp = re.compile(r'/review/(?P<id>[^/]+)', flags=re.I)
def extract_review_id(url):
    match = _extract_review_id_regexp.search(url)
    return str(match.group('id'))

_price_regexp = re.compile(ur'(?P<price>[$£][\d,\.]+)', flags=re.I)
def extract_price(text):
    match = _price_regexp.search(text)
    price = match.group('price')
    price = re.sub(ur'[$£,]', u'', price)
    price = float(price)
    return price

def add_query(url, **kwargs):
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    query_params = urlparse.parse_qs(query_string)
    # remove any existing value of 'key'
    keys = kwargs.keys()
    query_params = dict(filter(lambda x: x[0] not in keys, query_params.iteritems()))
    query_params.update(kwargs)
    query_string = urllib.urlencode(query_params, doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query_string, fragment))

def strip_html_tags(html):
    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []
            
        def handle_starttag(self, tag, attrs):
            if tag == 'br':
                self.fed.append('\n')
            HTMLParser.handle_starttag(self, tag, attrs)

        def handle_startendtag(self, tag, attrs):
            if tag == 'br':
                self.fed.append('\n')
            HTMLParser.handle_startendtag(self, tag, attrs)

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            data = ' '.join(self.fed)
            return data.replace('  ', ' ')

    s = MLStripper()
    # unescape any html chars
    # ie: in the blurb for http://www.amazon.com/dp/1491268727
    # the word unicode ' in R'lyeh (R&#x2019;lyeh) gets stripped unless we escape it first
    html = s.unescape(html)
    s.feed(html)
    #Shrink multiple \n into paragraph spacing.
    data = s.get_data().split(u'\n')
    data = map(lambda d: d.strip(), data)
    data = filter(bool, data)
    return u'\n\n'.join(data).strip()

def is_property(obj, k):
    # only accept @property decorated functions
    # these can only be detected via the __class__ object
    if hasattr(obj.__class__, k):
        if isinstance(getattr(obj.__class__, k), property):
            return True
    return False

def dict_acceptable(obj, k, blacklist=None):
    if blacklist and k in blacklist:
        return False
    return is_property(obj, k)


from amazon_scraper.product import Product
from amazon_scraper.reviews import Reviews
from amazon_scraper.review import Review


class AmazonScraper(object):
    def __init__(self, access_key, secret_key, associate_tag, *args, **kwargs):
        self.api = AmazonAPI(access_key, secret_key, associate_tag, *args)

    def reviews(self, ItemId=None, URL=None):
        return Reviews(ItemId, URL)

    def review(self, Id=None, URL=None):
        return Review(Id, URL)

    def lookup(self, URL=None, **kwargs):
        if URL:
            kwargs['ItemId'] = extract_asin(URL)

        result = self.api.lookup(**kwargs)
        if isinstance(result, (list, tuple)):
            result = [Product(p) for p in result]
        else:
            result = Product(result)
        return result

    def similarity_lookup(self, **kwargs):
        for p in self.api.similarity_lookup(**kwargs):
            yield Product(p)

    def browse_node_lookup(self, **kwargs):
        return self.api.browse_node_lookup(**kwargs)

    def search(self, **kwargs):
        for p in self.api.search(**kwargs):
            yield Product(p)

    def search_n(self, n, **kwargs):
        for p in self.api.search_n(n, **kwargs):
            yield Product(p)

