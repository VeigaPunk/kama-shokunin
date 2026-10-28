#!/usr/bin/env python3
"""L02LogTail cross-check: for every receipt produced in this audit, does the
server.log its receipt names (a) exist at the recorded path, (b) record the port
bind line matching the receipt's port, (c) record the model-load lines for the
receipt's model path, (d) record a shutdown line, (e) end in a newline (complete),
(f) carry no sentinel credential material?"""
import glob
import hashlib
import json
import os
import re

ROOT = '/fast/scratch/hyaku/kama-r62/w/L02LogTail'
SENTINELS = ('SENTINEL', 'sk-SENTINEL', 'hf_SENTINEL', 'ghp_SENTINEL')
KEY_PATTERNS = [
    r'sk-[A-Za-z0-9_\-]{16,}',
    r'hf_[A-Za-z0-9]{16,}',
    r'ghp_[A-Za-z0-9]{16,}',
    r'github_pat_[A-Za-z0-9_]{16,}',
    r'xox[abps]-[A-Za-z0-9\-]{10,}',
    r'AKIA[0-9A-Z]{12,}',
    r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    r'(?i)authorization:\s*\S+',
    r'(?i)bearer\s+[A-Za-z0-9._\-]{10,}',
]
rows = []
for path in sorted(glob.glob(os.path.join(ROOT, 'run*', 'receipt*.json'))):
    try:
        rec = json.load(open(path))
    except ValueError:
        rows.append((path, 'UNPARSEABLE-RECEIPT'))
        continue
    log = rec.get('server_log')
    run = os.path.basename(os.path.dirname(path))
    tag = os.path.basename(path)
    if not log:
        rows.append((f'{run}/{tag}', f"no server_log key (verdict={rec.get('verdict')}, "
                                     f"setup_error={'yes' if rec.get('setup_error') else 'no'})"))
        continue
    if not os.path.isfile(log):
        rows.append((f'{run}/{tag}', f'MISSING LOG {log}'))
        continue
    raw = open(log, 'rb').read()
    text = raw.decode('utf-8', 'replace')
    port = rec.get('port')
    model = (rec.get('model') or {}).get('path')
    bind = f'listening on http://127.0.0.1:{port}' in text
    load = bool(model) and f"loading model '{model}'" in text
    loaded = 'model loaded' in text
    shutdown = 'cleaning up before exit' in text
    complete = raw.endswith(b'\n')
    sentinel = [s for s in SENTINELS if s in text]
    keys = [p for p in KEY_PATTERNS if re.search(p, text)]
    rows.append((
        f'{run}/{tag}',
        f'port={port} bind={bind} load={load} loaded={loaded} shutdown={shutdown} '
        f'complete={complete} bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()[:16]} '
        f'sentinels={sentinel or "none"} keypatterns={keys or "none"} '
        f'accesslog={"/v1/completions" in text} mode={oct(os.stat(log).st_mode & 0o777)}'))
width = max(len(r[0]) for r in rows)
for name, detail in rows:
    print(f'{name:<{width}}  {detail}')
