#!/usr/bin/env python3
"""Replay of the frozen upstream predicate (tools/round43-hexrun-audit.py, tool contract
`ledger`/`upstream` clause) against this seat's ledger-fragment.tsv + evidence/ pair.
Read-only; prints one line per row plus a final verdict."""
import json, re, pathlib
BASE = pathlib.Path(__file__).resolve().parent
TOK = re.compile(r'(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])')
rows = [l.split('\t') for l in (BASE / 'ledger-fragment.tsv').read_text().splitlines() if l.strip()]
ok = True
for oid, cls, repo, evid, correct, _date, note in rows:
    raw = (BASE / 'evidence' / evid.rsplit('/', 1)[1]).read_text()
    json.loads(raw)
    shaped = bool(TOK.fullmatch(oid)) and len(oid) != 64
    good = shaped and oid in raw and repo in raw and cls == 'upstream' and correct == '' and len(note) >= 10
    ok &= good
    print(f"{oid} shaped={shaped} token_in_file={oid in raw} repo_in_file={repo in raw} "
          f"class={cls} correct_empty={correct == ''} note_len={len(note)} -> "
          f"{'upstream_ok' if good else 'ledger_bad'}")
print('ALL_ROWS_UPSTREAM_OK' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
