#!/usr/bin/env python3
"""Build the page from src/page.html (code) + src/data.json (all content).

Writes:
  index.html                          the GitHub Pages page (full HTML document)
  dist/politics-through-time.html     the same page without the <html>/<head>/<body> skeleton, for the Claude artifact host

Refuses to write anything if the data has a problem: missing fields, unknown families, duplicate ids, relationships to
entries that don't exist or that run backwards in time, compass values out of range, or malformed links.

Usage: python3 build.py          (then python3 check_links.py to confirm every link still loads)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PAGE = ROOT / 'src' / 'page.html'
DATA = ROOT / 'src' / 'data.json'
OUT_PAGES = ROOT / 'index.html'
OUT_ARTIFACT = ROOT / 'dist' / 'politics-through-time.html'
DESCRIPTION = ('Political systems and ideologies on one timeline, from tribal councils to national conservatism: how each '
               'began, key people and moments, core ideas, critics, a political compass and sources.')
RESET = (':root{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
         'html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0}img{max-width:100%}'
         '[hidden]:not([hidden=until-found i]){display:none!important}')
REQUIRED = ('id', 'label', 'name', 'fam', 'ds', 'date', 'how', 'size', 'status', 'story', 'ideas', 'texts', 'critique',
            'today', 'parents', 'wiki', 'people', 'moments', 'compass', 'refs', 'primary')


def check(data):
    problems = []
    fams = {f[0] for f in data['families']}
    entries = data['entries']
    ids = [e.get('id') for e in entries]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append('duplicate ids: ' + ', '.join(dupes))
    by = {e['id']: e for e in entries}
    year = lambda e: e['y'] if 'y' in e else -10**6
    for e in entries:
        eid = e.get('id', '?')
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            problems.append(f'{eid}: missing {", ".join(missing)}')
            continue
        if ('y' in e) == ('pre' in e):
            problems.append(f'{eid}: needs exactly one of y or pre')
        if e['fam'] not in fams:
            problems.append(f'{eid}: unknown family {e["fam"]}')
        if e['how'] not in ('founded', 'grew'):
            problems.append(f'{eid}: how must be founded or grew')
        if e['size'] not in ('xl', 'l', 'm', 's', 'none'):
            problems.append(f'{eid}: unknown size {e["size"]}')
        if ('end' in e) != ('endLabel' in e) or ('range' in e) != ('rangeLabel' in e):
            problems.append(f'{eid}: end/range need their labels')
        for parent, kind in e['parents']:
            if parent not in by:
                problems.append(f'{eid}: unknown parent {parent}')
            elif year(by[parent]) > year(e):
                problems.append(f'{eid} ({year(e)}) is earlier than its parent {parent} ({year(by[parent])})')
            if kind not in ('grew', 'drew', 'against'):
                problems.append(f'{eid}: unknown relationship {kind}')
        x, y = e['compass']
        if not (-10 <= x <= 10 and -10 <= y <= 10):
            problems.append(f'{eid}: compass out of range')
        if any(len(p) != 3 for p in e['people']) or any(len(m) != 2 for m in e['moments']):
            problems.append(f'{eid}: people need [name, years, role] and moments [when, what]')
        links = list(e['refs']) + ([e['primary']] if e['primary'] else [])
        if any(len(r) != 2 or not str(r[1]).startswith('https://') for r in links):
            problems.append(f'{eid}: refs/primary must be [label, https URL]')
    for m in data['milestones']:
        if not {'y', 'label', 'when', 'note'} <= set(m):
            problems.append(f'milestone {m.get("label", "?")}: missing fields')
    return problems


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    problems = check(data)
    if problems:
        sys.exit('Data problems, nothing written:\n  ' + '\n  '.join(problems))
    page = PAGE.read_text(encoding='utf-8')
    marker = '/*__DATA__*/null'
    if page.count(marker) != 1:
        sys.exit('src/page.html must contain the data marker exactly once')
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    body = page.replace(marker, payload)
    OUT_ARTIFACT.parent.mkdir(exist_ok=True)
    OUT_ARTIFACT.write_text(body, encoding='utf-8')
    head, rest = body.split('</style>', 1)
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta name="description" content="{DESCRIPTION}">\n<style>{RESET}</style>\n'
            f'{head.strip()}\n</style>\n</head>\n<body>\n{rest.strip()}\n</body>\n</html>\n')
    OUT_PAGES.write_text(full, encoding='utf-8')
    n = len(data['entries'])
    print(f'Wrote {OUT_PAGES.name} ({len(full):,} bytes) and {OUT_ARTIFACT.relative_to(ROOT)}: '
          f'{n} entries, {len(data["milestones"])} turning points.')


if __name__ == '__main__':
    main()
