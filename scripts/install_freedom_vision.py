#!/usr/bin/env python3
"""Safely attach the Freedom Vision static gateway to a verified Green Tank mirror.

Runs *after* scripts/mirror_dev.py and the existing Ghostbusters install step.
Never changes the source backup, historical releases or pre-existing routes.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'freedom_vision_source'
SITE = ROOT / 'site'
DEST = SITE / 'freedom-vision'
ASSETS = ('index.html', 'styles.css', 'app.js')
PREFIX = '/Thegreentank-deployment-2'


def sha_and_length(path: Path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def install():
    homepage = SITE / 'index.html'
    manifest_path = SITE / 'mirror-manifest.json'
    for needed in (*[SRC / x for x in ASSETS], homepage, manifest_path):
        if not needed.is_file():
            raise RuntimeError(f'Freedom Vision install: required file missing: {needed}')

    if DEST.exists():
        for name in ASSETS:
            candidate = DEST / name
            if not candidate.exists() or candidate.read_bytes() != (SRC / name).read_bytes():
                raise RuntimeError('The development mirror has its own Freedom Vision page; refusing to overwrite it.')
    else:
        DEST.mkdir(parents=True)
        for name in ASSETS:
            shutil.copy2(SRC / name, DEST / name)

    home = homepage.read_text(encoding='utf-8')
    link = f'{PREFIX}/freedom-vision/'
    if link not in home:
        # Clone precisely the known navigation link added by the separate Ghostbusters step.
        # Avoid guessing at the development site's DOM or rewriting unrelated navigation.
        pattern = re.compile(r'(<a\b[^>]*href=["\'][^"\']*/ghostbusters/?["\'][^>]*>.*?</a>)', re.I | re.S)
        found = pattern.search(home)
        if not found:
            raise RuntimeError('Freedom Vision install: verified Ghostbusters navigation anchor not found; refusing to guess placement.')
        clone = found.group(1)
        clone = re.sub(r'href=(["\']).*?\1', lambda match: f'href="{link}"', clone, count=1, flags=re.S)
        clone = re.sub(r'>.*?</a>', '>Freedom Vision</a>', clone, count=1, flags=re.S)
        if 'Freedom Vision' not in clone or link not in clone:
            raise RuntimeError('Freedom Vision install: could not safely construct navigation link.')
        home = home[:found.end()] + '\n' + clone + home[found.end():]
        homepage.write_text(home, encoding='utf-8')

    if home.count(link) != 1:
        raise RuntimeError('Freedom Vision install: navigation link is missing or duplicated.')

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    files = manifest.setdefault('files', {})
    for name in ASSETS:
        files[f'freedom-vision/{name}'] = sha_and_length(DEST / name)
    files['index.html'] = sha_and_length(homepage)
    manifest['freedom_vision_entry'] = 'freedom-vision/index.html'
    manifest['freedom_vision_version'] = '0.9'
    manifest['freedom_vision_files'] = len(ASSETS)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Freedom Vision gateway installed on verified mirror: 3 static assets and one navigation link.')


if __name__ == '__main__':
    install()