#!/usr/bin/env python3
"""Build index.html (GitHub Pages) from src/politics-through-time.html (the page body, as published to claude.ai).

The source has no <html>/<head>/<body> skeleton because the Claude artifact host adds one. This script adds the same
skeleton for GitHub Pages, moves the title, font links and styles into <head>, and checks the data before writing:
unique ids, every relationship points at an entry that exists, and no line runs backwards in time.

Usage: python3 build.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'src' / 'politics-through-time.html'
OUT = ROOT / 'index.html'
DESCRIPTION = ('45 political systems and ideologies on one timeline, from tribal councils to national conservatism: '
               'how each began, its core ideas, its critics, and what grew out of it.')
RESET = (':root{color-scheme:dark;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);'
         'padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}'
         'body{margin:0;padding:0}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}')


def check(source):
    entries = re.findall(r'\{ id: "([a-z]+)".*?parents: (\[[^\n]*?\]), wiki:', source, re.S)
    ids = [e[0] for e in entries]
    years = {}
    for m in re.finditer(r'\{ id: "([a-z]+)".*?(?:\by: (-?\d+)|pre: (\d+))', source, re.S):
        years[m.group(1)] = int(m.group(2)) if m.group(2) else -10**6
    problems = []
    if len(ids) != len(set(ids)):
        problems.append('duplicate ids: ' + ', '.join(sorted({i for i in ids if ids.count(i) > 1})))
    known = set(ids)
    for child, parents in entries:
        for parent, kind in re.findall(r'\["([a-z]+)", "([a-z]+)"\]', parents):
            if parent not in known:
                problems.append(f'{child}: unknown parent "{parent}"')
            if kind not in ('grew', 'drew', 'against'):
                problems.append(f'{child}: unknown relationship "{kind}"')
            if parent in years and child in years and years[parent] > years[child]:
                problems.append(f'{child} ({years[child]}) is earlier than its parent {parent} ({years[parent]})')
    return ids, problems


def main():
    source = SRC.read_text(encoding='utf-8')
    ids, problems = check(source)
    if problems:
        sys.exit('Data problems, nothing written:\n  ' + '\n  '.join(problems))
    head, body = source.split('</style>', 1)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta name="description" content="{DESCRIPTION}">\n<style>{RESET}</style>\n'
            f'{head.strip()}\n</style>\n</head>\n<body>\n{body.strip()}\n</body>\n</html>\n')
    OUT.write_text(page, encoding='utf-8')
    print(f'Wrote {OUT.name}: {len(ids)} entries, {len(page):,} bytes.')


if __name__ == '__main__':
    main()
