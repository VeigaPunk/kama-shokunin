#!/usr/bin/env python3
"""Re-derive every number quoted in findings.md from the verbatim captures.

Usage: python3 reconcile.py <out-dir>
Exit 0 = all checks pass.
"""
import datetime as dt
import gzip
import json
import os
import sys

OUT = sys.argv[1]
recs = [json.loads(l) for l in gzip.open(os.path.join(OUT, 'captures.raw.jsonl.gz'), 'rt')]
summ = json.load(open(os.path.join(OUT, 'evidence', 'summary.json')))
by = {r['label']: r for r in recs}
results = []


def chk(name, cond, detail=""):
    results.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + name + ((" | " + detail) if detail else ""))


g30 = json.loads(by['generate-keep-alive-30s']['body'])
ps30 = json.loads(by['ps-after-keep-alive-30s']['body'])['models'][0]
chk("gen30 load_duration 252138068", g30['load_duration'] == 252138068, str(g30['load_duration']))
chk("gen30 total_duration 7997112810", g30['total_duration'] == 7997112810)
chk("ps30 expires raw", ps30['expires_at'] == "2026-10-27T18:37:03.576020283-03:00", ps30['expires_at'])
chk("ps repeat byte-identical",
    by['ps-after-keep-alive-30s-repeat']['body'] == by['ps-after-keep-alive-30s']['body'])
chk("ps-before empty", json.loads(by['ps-before-any-load']['body']) == {"models": []})
chk("tags-before lists the model",
    any(m['digest'].startswith('8cf91c71') for m in json.loads(by['tags-before']['body'])['models']))
chk("ps after ka0 poll0 empty", json.loads(by['ps-after-keep-alive-0-poll-0']['body']) == {"models": []})
chk("ka0 first poll rel_ms <= 0.01", summ['notes']['keep_alive_0']['first_ps_rel_ms'] <= 0.01,
    str(summ['notes']['keep_alive_0']['first_ps_rel_ms']))
chk("reload cold load_duration 252645769",
    json.loads(by['generate-reload-before-stop']['body'])['load_duration'] == 252645769)
chk("stop exit 0", summ['notes']['ollama_stop']['exit'] == 0,
    str(summ['notes']['ollama_stop']['cli_ms']) + " ms, stdout=" + repr(summ['notes']['ollama_stop']['stdout']))
chk("stop ps empty", json.loads(by['ps-after-ollama-stop-poll-0']['body']) == {"models": []})
chk("stop empty_at_ms <= 0.01", summ['notes']['stop_empty_at_ms'] <= 0.01, str(summ['notes']['stop_empty_at_ms']))
pre = json.loads(by['generate-empty-prompt-no-key']['body'])
chk("preload done_reason load", pre['done_reason'] == 'load')
chk("preload no timing keys", sorted(pre) == ['created_at', 'done', 'done_reason', 'model', 'response'], str(sorted(pre)))
psp = json.loads(by['ps-after-empty-prompt']['body'])['models'][0]
expp = dt.datetime.fromisoformat(psp['expires_at'].replace('Z', '+00:00'))
crep = dt.datetime.fromisoformat(pre['created_at'].replace('Z', '+00:00'))
chk("preload lease ~300s", abs((expp - crep).total_seconds() - 300) < 0.01, f"{(expp - crep).total_seconds():.6f}s")
offs = {r['run']: json.loads(r['body'])['models'][0]['expires_at']
        for r in recs if r['run'].startswith('B-TZ') and r['label'] == 'ps'}
chk("TZ=UTC renders Z", offs['B-TZ-UTC'].endswith('Z'), offs['B-TZ-UTC'])
chk("TZ=Asia/Tokyo renders +09:00", offs['B-TZ-Asia/Tokyo'].endswith('+09:00'), offs['B-TZ-Asia/Tokyo'])
chk("all stop runs leave ps empty",
    all(json.loads(r['body']) == {"models": []} for r in recs if r['label'] == 'ps-after-stop'))
print("SUMMARY", sum(results), "/", len(results), "checks pass")
sys.exit(0 if all(results) else 1)
