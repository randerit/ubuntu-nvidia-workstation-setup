#!/usr/bin/env python3
"""Verifica que los enlaces relativos y las anclas de los .md del repo resuelvan.

Uso (desde la raíz del repo):  python3 scripts/check_links.py
Sale con código 1 si algún enlace está roto. No toca la red: ignora http(s).
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)\)')


def slug(text):
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = text.replace('`', '').replace('**', '').replace('*', '').strip().lower()
    text = ''.join(c for c in text if c.isalnum() or c in ' -_')
    return text.replace(' ', '-')


def prose_lines(path):
    """Líneas fuera de bloques de código, con los `spans` inline vaciados."""
    in_fence = False
    for n, line in enumerate(path.read_text(encoding='utf-8').split('\n'), 1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, re.sub(r'`[^`]*`', '``', line)


def anchors(path, cache={}):
    if path not in cache:
        seen, found = Counter(), set()
        for _, line in prose_lines(path):
            m = re.match(r'#{1,6}\s+(.*)', line)
            if m:
                s = slug(m.group(1))
                found.add(s if seen[s] == 0 else f'{s}-{seen[s]}')
                seen[s] += 1
        cache[path] = found
    return cache[path]


def main():
    errors = checked = 0
    for md in sorted(ROOT.rglob('*.md')):
        if '.git' in md.parts:
            continue
        for n, line in prose_lines(md):
            for target in LINK.findall(line):
                if re.match(r'(https?:|mailto:)', target):
                    continue
                checked += 1
                file_part, _, frag = target.partition('#')
                dest = md if not file_part else (md.parent / file_part).resolve()
                rel = md.relative_to(ROOT)
                if not dest.exists():
                    print(f'{rel}:{n}: no existe {target}')
                    errors += 1
                elif frag and dest.suffix == '.md' and frag not in anchors(dest):
                    print(f'{rel}:{n}: ancla inexistente {target}')
                    errors += 1
    print(f'{checked} enlaces revisados, {errors} rotos')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
