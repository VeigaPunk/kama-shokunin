#!/usr/bin/env python3
"""round43-health-audit.py - kama round-43 C3 (coverage, assimilation) counter.

Question: at a revision, does the corpus hold the process map of vLLM's health
surface that the base tree did not hold - the v0.31.0 `/health` endpoint
belongs to the weight-cache daemon (`vllm preload`), not to the inference
server whose one `/health` route the corpus already holds (row S004) - as ONE
admitted knowledge entry, sourced on two rows opened this round, each backed by
a committed copy whose located quote also occurs in a live refetch?

Fixed names (frozen before data):
  entry     corpus/knowledge/runtime-health-surface-processes.md
  sources   REL  page  https://github.com/vllm-project/vllm/releases/tag/v0.31.0
                 api   https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.31.0
                 copy  .ufo/waves/round-43/c3/vllm-v0.31.0-release.json
                 quote "a `/health` endpoint (#58552)"           (JSON field body)
            PR   page  https://github.com/vllm-project/vllm/pull/58552
                 api   https://api.github.com/repos/vllm-project/vllm/pulls/58552
                 copy  .ufo/waves/round-43/c3/vllm-pr-58552.json
                 quotes "Add an HTTP `/health` endpoint to the weight cache daemon parent process."
                        "distinguish daemon startup from readiness"   (field body)
  lesson    corpus/lessons/round-43.md
  scratch   .ufo/waves/round-43/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice}
            and at least one file under .ufo/waves/round-43/assimilation/guard/

Legs (each 0/1):
  entry     the entry exists at --tip; its first three non-blank lines start
            `source:`, `verified-at:`, `recheck:`; the `source:` line names the
            registry ids of both rows; the body contains `weight cache daemon`,
            `vllm preload`, `#58552`, the states `starting`, `ready` and `failed`,
            the held row id `S004`, and the phrase `different process`.
  rows      both sources are registry rows (found by URL in the source cell; ids
            absent at --base) with 11 cells under the registry header; kind
            `docs` and tier `A` for REL, kind `community` and a tier other than
            `A` for PR; status `mined`; opened `2026-10-25`; used-by names the
            entry; the anchor cell holds the 64-hex SHA-256 of the row's copy.
  coverage  at --base no tracked .md outside `.ufo/` contains `weight cache
            daemon` or `vllm preload` (case-insensitive); at --tip the entry
            exists and corpus/README.md has a line naming its path.
  gate      the lesson has a `## Gate` section; for each new row a line naming its
            id, its URL and the date 2026-10-25 carries a double-quoted quote of
            <= 25 words that occurs (whitespace-normalised) in the `body` or
            `title` of the committed copy; a `### Assimilation set` section has
            one line with `admit` and one with `reject`; the four scratch files
            exist, `quarantine-slice` is non-empty, `collisions` is empty or the
            lesson names a renumber map, and `guard/` holds a file.
  refetch   a live fetch of each api URL (`gh api`, else curl) contains that
            source's frozen quotes and every quote the gate leg accepted for it
            (whitespace-normalised) in `body`/`title`; a network
            failure reads 0 (the counter cannot re-derive the quote).
  census    `sources-census.sh validate --file <tip export>/corpus/SOURCES.md`
            exits 0.
met = all six legs 1.

Output: `entry=E rows=R coverage=C gate=G refetch=F census=N met=True|False` then
`detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo. Temporary export is removed.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

DATE = "2026-10-25"
ENTRY = "corpus/knowledge/runtime-health-surface-processes.md"
LESSON = "corpus/lessons/round-43.md"
SRC = {
    "REL": dict(page="https://github.com/vllm-project/vllm/releases/tag/v0.31.0",
                api="https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.31.0",
                copy=".ufo/waves/round-43/c3/vllm-v0.31.0-release.json",
                quotes=["a `/health` endpoint (#58552)"], kind="docs", tier_a=True),
    "PR": dict(page="https://github.com/vllm-project/vllm/pull/58552",
               api="https://api.github.com/repos/vllm-project/vllm/pulls/58552",
               copy=".ufo/waves/round-43/c3/vllm-pr-58552.json",
               quotes=["Add an HTTP `/health` endpoint to the weight cache daemon parent process.",
                       "distinguish daemon startup from readiness"], kind="community", tier_a=False),
}
SCRATCH = ["reg-ids", "staged-ids", "collisions", "quarantine-slice"]
CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"
_tmp: list[str] = []


def _cleanup() -> None:
    while _tmp:
        shutil.rmtree(_tmp.pop(), ignore_errors=True)


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))


def git(repo, *args, binary=False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


def blob(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def registry(text):
    """id -> {column name: cell}, columns read from the header row."""
    rows, hdr = {}, None
    for l in text.split("\n"):
        if re.match(r"^\s*\|\s*id\s*\|", l):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]
        elif hdr and re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) == len(hdr) == 11:
                rows[c[0]] = dict(zip(hdr, c))
    return rows


def copy_text(data):
    """Searchable text of a committed API copy: JSON body + title, else raw."""
    try:
        j = json.loads(data.decode("utf-8", "replace"))
        return norm("\n".join(str(j.get(k) or "") for k in ("title", "body")))
    except (ValueError, AttributeError):
        return norm(data.decode("utf-8", "replace"))


def live_text(api):
    for cmd in (["gh", "api", api.replace("https://api.github.com/", "")],
                ["curl", "-sS", "-m", "60", "-H", "Accept: application/vnd.github+json", api]):
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if p.returncode == 0 and p.stdout:
            t = copy_text(p.stdout)
            if t:
                return t
    return None


def evaluate(repo, tip, base):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    base = git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
    legs = dict(entry=0, rows=0, coverage=0, gate=0, refetch=0, census=0)
    d = []
    copies = {k: blob(repo, tip, v["copy"]) for k, v in SRC.items()}
    for k, v in copies.items():
        if v is None:
            d.append(f"detail: evidence copy missing: {SRC[k]['copy']}")
    ctext = {k: copy_text(v) for k, v in copies.items() if v is not None}
    reg_tip = registry((blob(repo, tip, "corpus/SOURCES.md") or b"").decode(errors="replace"))
    reg_base = registry((blob(repo, base, "corpus/SOURCES.md") or b"").decode(errors="replace"))
    ids = {}
    for k, v in SRC.items():
        for sid, c in reg_tip.items():
            if sid not in reg_base and v["page"] in c.get("source", ""):
                ids[k] = sid
    # rows
    ok = len(ids) == len(SRC)
    if not ok:
        d.append(f"detail: rows: new rows found by URL {ids}; need {sorted(SRC)}")
    for k, sid in ids.items():
        c = reg_tip[sid]
        bad = []
        if c.get("kind") != SRC[k]["kind"]: bad.append(f"kind {c.get('kind')}")
        if (c.get("tier") == "A") != SRC[k]["tier_a"]: bad.append(f"tier {c.get('tier')}")
        if c.get("status") != "mined": bad.append(f"status {c.get('status')}")
        if c.get("opened") != DATE: bad.append(f"opened {c.get('opened')}")
        if ENTRY not in c.get("used-by", ""): bad.append("used-by lacks entry")
        if copies.get(k) is None or hashlib.sha256(copies[k]).hexdigest() not in c.get("anchor", ""):
            bad.append("anchor lacks copy sha256")
        if bad:
            ok = False
            d.append(f"detail: row {sid} ({k}): {', '.join(bad)}")
    legs["rows"] = int(ok)
    # entry
    entry = blob(repo, tip, ENTRY)
    if entry is None:
        d.append(f"detail: {ENTRY} absent at tip")
    else:
        t = entry.decode(errors="replace")
        head = [l for l in t.split("\n") if l.strip()][:3]
        ok = len(head) == 3 and head[0].startswith("source:") and head[1].startswith("verified-at:") \
            and head[2].startswith("recheck:") and len(ids) == len(SRC) and all(s in head[0] for s in ids.values())
        if not ok:
            d.append(f"detail: entry provenance trio or source ids wrong: {[h[:70] for h in head]}")
        low = t.lower()
        for need in ("weight cache daemon", "vllm preload", "#58552", "starting", "ready", "failed", "s004", "different process"):
            if need not in low:
                ok = False
                d.append(f"detail: entry lacks {need!r}")
        legs["entry"] = int(ok)
    # coverage
    ok = True
    for p in git(repo, "ls-tree", "-r", "--name-only", "-z", base).split("\0"):
        if p.endswith(".md") and not p.startswith(".ufo/"):
            t = (blob(repo, base, p) or b"").decode(errors="replace").lower()
            if "weight cache daemon" in t or "vllm preload" in t:
                ok = False
                d.append(f"detail: coverage: base already holds the ground in {p}")
                break
    if blob(repo, base, ENTRY) is not None:
        ok = False
        d.append("detail: coverage: entry already present at base")
    rd = (blob(repo, tip, "corpus/README.md") or b"").decode(errors="replace")
    if entry is None or not any(ENTRY in l for l in rd.split("\n")):
        ok = False
        d.append("detail: coverage: entry or README coverage line absent at tip")
    legs["coverage"] = int(ok)
    # gate
    ok = True
    gate_q = {k: [] for k in SRC}
    les = (blob(repo, tip, LESSON) or b"").decode(errors="replace")
    m = re.search(r"^## Gate[^\n]*\n(.*?)(?=^## |\Z)", les, re.S | re.M)
    sec = m.group(1) if m else ""
    if not m:
        ok = False
        d.append(f"detail: gate: {LESSON} has no ## Gate section")
    for k, sid in ids.items():
        good = False
        for l in sec.split("\n"):
            if sid in l and SRC[k]["page"] in l and DATE in l:
                for q in re.findall(r'"([^"]{8,})"', l):
                    if len(q.split()) <= 25 and k in ctext and norm(q) in ctext[k]:
                        good = True
                        gate_q[k].append(q)
        if not good:
            ok = False
            d.append(f"detail: gate: no dated, <=25-word quote located in the copy for {sid} ({k})")
    am = re.search(r"^### Assimilation set[^\n]*\n(.*?)(?=^#{1,3} |\Z)", les, re.S | re.M)
    if not am or not re.search(r"\badmit", am.group(1), re.I) or not re.search(r"\breject", am.group(1), re.I):
        ok = False
        d.append("detail: gate: ### Assimilation set lacks an admit line and a reject line")
    base_dir = ".ufo/waves/round-43/assimilation"
    for s in SCRATCH:
        b = blob(repo, tip, f"{base_dir}/{s}")
        if b is None:
            ok = False
            d.append(f"detail: gate: scratch file {s} absent")
        elif s == "quarantine-slice" and not b.strip():
            ok = False
            d.append("detail: gate: quarantine-slice empty")
        elif s == "collisions" and b.strip() and "renumber" not in les.lower():
            ok = False
            d.append("detail: gate: collisions non-empty and lesson names no renumber map")
    if not [p for p in git(repo, "ls-tree", "-r", "--name-only", "-z", tip, base_dir + "/guard").split("\0") if p]:
        ok = False
        d.append("detail: gate: guard/ holds no file")
    legs["gate"] = int(ok)
    # refetch
    ok = True
    for k, v in SRC.items():
        lt = live_text(v["api"])
        if lt is None:
            ok = False
            d.append(f"detail: refetch: {v['api']} could not be fetched")
            continue
        for q in v["quotes"] + gate_q[k]:
            if norm(q) not in lt:
                ok = False
                d.append(f"detail: refetch: quote absent from live {k}: {q[:60]!r}")
    legs["refetch"] = int(ok)
    # census
    ex = tempfile.mkdtemp(prefix="r43c3-")
    _tmp.append(ex)
    subprocess.run(["tar", "-x", "-C", ex], input=git(repo, "archive", "--format=tar", tip, binary=True), check=True)
    if os.path.isfile(CENSUS):
        p = subprocess.run(["bash", CENSUS, "validate", "--file", os.path.join(ex, "corpus/SOURCES.md")],
                           capture_output=True, text=True, timeout=300)
        legs["census"] = int(p.returncode == 0)
        if p.returncode:
            d.append(f"detail: census validate exit {p.returncode}: {p.stdout.strip()[:200]}")
    else:
        d.append("detail: sources-census.sh absent")
    return tip, legs, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--base", default="6897ead55c24ba08c9ac0b09466d4fbfe005a459")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        tip, legs, d = evaluate(os.path.abspath(a.repo), a.tip, a.base)
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    met = all(legs.values())
    out = "\n".join([f"tip={tip}", "entry={entry} rows={rows} coverage={coverage} gate={gate} refetch={refetch} "
                     "census={census} met={m}".format(m=met, **legs), *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w").write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
