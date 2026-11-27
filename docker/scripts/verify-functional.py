#!/usr/bin/env python3
"""Run the supplied REST scenarios against a fresh stack, failing on mismatches."""
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BASE = 'http://127.0.0.1:8080'


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        return json.load(response)


def script(name):
    # Preserve the scripts while making their curl calls reject HTTP failures.
    subprocess.run(['bash', '-c', '''
set -euo pipefail
curl() { command curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 30 "$@"; }
export -f curl
source "$1"
''', 'bash', name], cwd=ROOT, check=True)


def counts(expected):
    actual = [len(get('/recensioni-seguite/recensioniseguite/' + u)) for u in ('Alice', 'Bob', 'Carlo')]
    assert actual == expected, (actual, expected)
    print('PASS: Alice/Bob/Carlo =', actual, flush=True)


if __name__ == '__main__':
    assert get('/actuator/health')['status'] == 'UP'
    for path in ('/album/album', '/recensioni/recensioni', '/connessioni/connessioni'):
        assert get(path) == [], 'Use a fresh stack: this script inserts the supplied demo data'
    script('do-init-bettermusic-db.sh')
    script('run-sample-queries.sh')
    counts([5, 6, 5])
    albums, reviews, links = (get(p) for p in ('/album/album', '/recensioni/recensioni', '/connessioni/connessioni'))
    assert get('/album/album/' + str(albums[0]['id'])) == albums[0]
    assert 'testo' in get('/recensioni/recensioni/' + str(reviews[0]['id']))
    assert links and get('/connessioni/connessioni/Alice')
    script('do-update-albums.sh')
    script('run-sample-queries.sh')
    counts([5, 6, 5])
    script('do-update-recensioni.sh')
    script('run-sample-queries.sh')
    counts([6, 8, 7])
    script('do-update-connessioni.sh')
    script('run-sample-queries.sh')
    counts([7, 5, 8])
    assert not any(c['seguito'] == 'OndaRock' and c['ruolo'] == 'RECENSORE'
                   for c in get('/connessioni/connessioni/Bob')), 'DELETE failed'
    print('PASS: existing create/read/delete operations, four Gateway routes and backend REST aggregation')
