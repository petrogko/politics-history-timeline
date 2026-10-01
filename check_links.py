#!/usr/bin/env python3
"""Check that every link in src/data.json (or in a plain list of URLs) still loads.

Usage: python3 check_links.py            # all links in src/data.json
       python3 check_links.py urls.txt   # one URL per line
Prints each failure, plus the page title for book and archive links so a wrong book number is easy to spot.
"""
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
SHOW_TITLE = ('gutenberg.org', 'ctext.org', 'marxists.org', 'avalon.law.yale.edu', 'mkgandhi.org')


def urls_from_data(path):
    found = []

    def walk(node):
        if isinstance(node, str) and node.startswith('http'):
            found.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(json.loads(Path(path).read_text(encoding='utf-8')))
    return sorted(set(found))


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(200_000).decode('utf-8', 'replace')
            title = re.search(r'<title[^>]*>([^<]*)', body, re.I)
            return url, response.status, (title.group(1).strip() if title else '')
    except urllib.error.HTTPError as exc:
        return url, exc.code, ''
    except Exception as exc:  # timeouts, TLS and DNS errors
        return url, type(exc).__name__, ''


def main():
    if len(sys.argv) > 1:
        urls = [line.strip() for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
    else:
        urls = urls_from_data(Path(__file__).parent / 'src' / 'data.json')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, urls))
    # Some sites answer 200 for a placeholder page (e.g. the Stanford Encyclopedia's 'Not Yet Available')
    results = [(u, 'placeholder page', ti) if s == 200 and 'not yet available' in ti.lower() else (u, s, ti)
               for u, s, ti in results]
    bad = [r for r in results if r[1] != 200]
    for url, status, title in results:
        if status != 200:
            print(f'FAIL {status}  {url}')
        elif any(host in url for host in SHOW_TITLE):
            print(f'ok   {title[:70]!r:72} {url}')
    print(f'{len(results) - len(bad)} of {len(results)} links load.')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
