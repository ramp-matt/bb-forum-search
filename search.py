import os
import urllib2
import codecs
import re
import time

import requests
from bs4 import BeautifulSoup


URL_DEFAULT = 'http://www.teambeachbody.com/connect/message-boards/-/message_boards/search?_19_keywords=%(q)s'

COLUMN_MAP = {"#" : "Result Number"}

RATINGS_RE = re.compile(r'rating:([^}]+)}')
TOT_RESULTS_RE = re.compile(r'of (\d+,*\d*) results')

class SearchError(Exception):
    def __init__(self, message, code=500):
        super(SearchError, self).__init__(message)
        self.code = code

def normalize_column_name(s):
    if not s:
        return ''
    s = s.strip()
    s = COLUMN_MAP.get(s, s)
    s = s.replace(' ', '_')
    return s

def bb_search(q, url=None):
    started = time.time()

    if not url:
        url = URL_DEFAULT
    if os.path.isfile(url):
        data = codecs.open(url, 'r', 'utf-8').read()
    else:
        url = url % { 'q': urllib2.quote(q) }
        r = requests.get(url)
        data = r.text
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find('table', class_="taglib-search-iterator")
    if not table:
        raise SearchError('table.taglib-search-iterator not found')

    total_results = 0
    div_results = soup.find('div', class_='search-results')
    if div_results:
        m = TOT_RESULTS_RE.search(div_results.text)
        if m:
            value = m.group(1).replace(',', '')
            try:
                total_results = int(value)
            except ValueError:
                pass

    results = []
    is_first = True
    columns = None
    for rowidx, row in enumerate(table.find_all('tr')):
        if is_first:
            columns = map(lambda x: normalize_column_name(x.text), row.find_all('th'))
            is_first = None
            continue
        if columns is None:
            raise SearchError('No headers found')

        found_links = set()
        hit = {}
        for idx, td in enumerate(row.find_all('td')):
            value = td.text.strip()
            if value.startswith('/*'):
                m = RATINGS_RE.search(value)
                if m:
                    value = m.group(1)
            hit[columns[idx]] = value
            link = td.find('a')
            if link:
                href = link['href']
                if href not in found_links:
                    hit[columns[idx]+'_Link'] = href
                    found_links.add(href)
        # there's a blank line after the headers
        if not hit[columns[0]]: continue
        results.append(hit)

    now = time.time()
    elapsed = now - started
    elapsed = int(elapsed*1000)
    return { 'data': results, 'elapsed': elapsed, 'total_results': total_results, 'url': url }


if __name__ == '__main__':
    import sys
    url = None
    q = sys.argv[1]
    if sys.argv[2:]:
        url = sys.argv[2]

    import json
    print json.dumps(bb_search(q, url), indent=4)

