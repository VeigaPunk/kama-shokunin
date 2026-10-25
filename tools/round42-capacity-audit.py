#!/usr/bin/env python3
"""round42-capacity-audit.py - kama round-42 C3 (coverage, assimilation) counter.

Question: at a revision, does the corpus hold the engine-side of the K05
"declared versus served context capacity" ground that the base tree did not
hold - vLLM's served KV-cache capacity (source @ tag v0.32.0) and llama.cpp's
declared `context_length` card key (source @ commit 704366d7) - as ONE
admitted knowledge entry, re-grounded from bytes opened in this round?

Fixed names (frozen before data):
  entry      corpus/knowledge/context-capacity-engine-sides.md
  rows       S478 (vLLM kv_cache_utils.py @ v0.32.0), S479 (llama.cpp
             server-models.cpp @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad)
  evidence   .ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py
             .ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp
  lesson     corpus/lessons/round-42.md
  scratch    .ufo/waves/round-42/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice}
  anchors    in the evidence copies, first line containing
               A1 'num_blocks = available_memory // bytes_per_block'
               A2 'KV cache size: %s tokens'
               A3 'model_info["context_length"] = meta.n_ctx_train;'
             (A1, A2 in the vLLM copy; A3 in the llama.cpp copy).

Legs (each 0/1):
  entry     the entry exists at --tip; its first three non-blank lines start
            `source:`, `verified-at:`, `recheck:`; the `source:` line names S478
            and S479; the body cites `kv_cache_utils.py:<A1 line>`,
            `kv_cache_utils.py:<A2 line>` and `server-models.cpp:<A3 line>` with
            the line numbers this counter computes from the committed copies,
            and states the count of `max_model_len` in the llama.cpp copy as
            `max_model_len` followed within 80 chars by that count (computed here).
  rows      each of S478, S479 is a registry row with 11 cells: kind `code`,
            tier `A`, status `mined`, opened `2026-10-25`, used-by containing the
            entry path, source cell containing its expected raw URL, and an
            anchor cell containing the 64-hex SHA-256 of its committed copy.
  coverage  at --base the entry path is absent and no tracked corpus/ or SKILL.md
            blob contains `kv_cache_size_tokens` or `Maximum concurrency for`
            (uncovered ground); at --tip corpus/README.md has a line naming the
            entry path.
  gate      the lesson has a `## Gate` section naming S478 and S479, each with its
            URL, the access date 2026-10-25 and a double-quoted located quote of
            <= 25 words that occurs (whitespace-normalised) in its committed copy;
            and the assimilation scratch files exist, `collisions` is EMPTY or
            the lesson names its renumber map, and `quarantine-slice` is non-empty.
  census    `sources-census.sh validate --file <tip export>/corpus/SOURCES.md`
            exits 0.
met = all five legs 1.

Output: `entry=E rows=R coverage=C gate=G census=N met=True|False` then
`detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo. Temporary export is removed.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile

DATE = "2026-10-25"
ENTRY = "corpus/knowledge/context-capacity-engine-sides.md"
LESSON = "corpus/lessons/round-42.md"
EV = {
    "S478": (".ufo/waves/round-42/c3/vllm-v0.32.0-kv_cache_utils.py",
             "https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py"),
    "S479": (".ufo/waves/round-42/c3/llamacpp-704366d7-server-models.cpp",
             "https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp"),
}
A1 = "num_blocks = available_memory // bytes_per_block"
A2 = "KV cache size: %s tokens"
A3 = 'model_info["context_length"] = meta.n_ctx_train;'
SCRATCH = ["reg-ids", "staged-ids", "collisions", "quarantine-slice"]
CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"


def git(repo, *args, binary=False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


def blob(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def first_line(data, needle):
    for i, l in enumerate(data.decode(errors="replace").split("\n"), 1):
        if needle in l:
            return i
    return None


def registry_rows(text):
    rows = {}
    for l in text.split("\n"):
        if re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) == 11:
                rows[c[0]] = c
    return rows


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def evaluate(repo, tip, base):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    base = git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
    legs = dict(entry=0, rows=0, coverage=0, gate=0, census=0)
    d = []
    ev = {k: blob(repo, tip, v[0]) for k, v in EV.items()}
    for k, v in ev.items():
        if v is None:
            d.append(f"detail: evidence copy missing: {EV[k][0]}")
    vl = ev["S478"]
    lc = ev["S479"]
    entry = blob(repo, tip, ENTRY)
    lines = {}
    if vl is not None and lc is not None:
        lines = dict(A1=first_line(vl, A1), A2=first_line(vl, A2), A3=first_line(lc, A3),
                     mm=lc.decode(errors="replace").count("max_model_len"))
        if None in (lines["A1"], lines["A2"], lines["A3"]):
            d.append(f"detail: anchor missing in committed copy: {lines}")
    # entry
    if entry is None:
        d.append(f"detail: {ENTRY} absent at tip")
    elif lines and None not in (lines["A1"], lines["A2"], lines["A3"]):
        t = entry.decode(errors="replace")
        head = [l for l in t.split("\n") if l.strip()][:3]
        ok = len(head) == 3 and head[0].startswith("source:") and head[1].startswith("verified-at:") \
            and head[2].startswith("recheck:") and "S478" in head[0] and "S479" in head[0]
        if not ok:
            d.append(f"detail: entry provenance trio/source ids wrong: {[h[:60] for h in head]}")
        need = [f"kv_cache_utils.py:{lines['A1']}", f"kv_cache_utils.py:{lines['A2']}",
                f"server-models.cpp:{lines['A3']}"]
        for n in need:
            if n not in t:
                ok = False
                d.append(f"detail: entry lacks citation {n}")
        if not re.search(r"max_model_len[^\n]{0,80}\b%d\b" % lines["mm"], t):
            ok = False
            d.append(f"detail: entry does not state max_model_len count {lines['mm']} within 80 chars")
        legs["entry"] = int(ok)
    # rows
    sources = blob(repo, tip, "corpus/SOURCES.md")
    rows = registry_rows(sources.decode(errors="replace")) if sources else {}
    ok = True
    for sid, (path, url) in EV.items():
        c = rows.get(sid)
        if c is None or ev[sid] is None:
            ok = False
            d.append(f"detail: row {sid} missing or evidence absent")
            continue
        digest = hashlib.sha256(ev[sid]).hexdigest()
        bad = []
        if c[2] != "code": bad.append(f"kind {c[2]}")
        if c[3] != "A": bad.append(f"tier {c[3]}")
        if c[7] != "mined": bad.append(f"status {c[7]}")
        if c[8] != DATE: bad.append(f"opened {c[8]}")
        if ENTRY not in c[10]: bad.append("used-by lacks entry")
        if url not in c[1]: bad.append("source cell lacks URL")
        if digest not in c[5]: bad.append("anchor lacks copy sha256")
        if bad:
            ok = False
            d.append(f"detail: row {sid}: {', '.join(bad)}")
    legs["rows"] = int(ok)
    # coverage
    ok = True
    if blob(repo, base, ENTRY) is not None:
        ok = False
        d.append("detail: entry already present at base")
    for p in git(repo, "ls-tree", "-r", "--name-only", "-z", base).split("\0"):
        if p and (p.startswith("corpus/") or p == "SKILL.md") and p.endswith(".md"):
            t = (blob(repo, base, p) or b"").decode(errors="replace")
            if "kv_cache_size_tokens" in t or "Maximum concurrency for" in t:
                ok = False
                d.append(f"detail: base already holds the ground in {p}")
                break
    rd = (blob(repo, tip, "corpus/README.md") or b"").decode(errors="replace")
    if not any(ENTRY in l for l in rd.split("\n")):
        ok = False
        d.append("detail: corpus/README.md names no coverage line for the entry")
    legs["coverage"] = int(ok)
    # gate
    ok = True
    les = (blob(repo, tip, LESSON) or b"").decode(errors="replace")
    m = re.search(r"^## Gate[^\n]*\n(.*?)(?=^## |\Z)", les, re.S | re.M)
    sec = m.group(1) if m else ""
    if not m:
        ok = False
        d.append(f"detail: {LESSON} has no ## Gate section")
    for sid, (path, url) in EV.items():
        gl = [l for l in sec.split("\n") if sid in l]
        good = False
        for l in gl:
            q = re.findall(r'"([^"]{8,})"', l)
            if url in sec and DATE in l and any(len(x.split()) <= 25 and ev[sid] is not None and
                                                norm(x) in norm(ev[sid].decode(errors="replace")) for x in q):
                good = True
        if not good:
            ok = False
            d.append(f"detail: gate lacks a dated, <=25-word, located quote line for {sid}")
    for s in SCRATCH:
        b = blob(repo, tip, f".ufo/waves/round-42/assimilation/{s}")
        if b is None:
            ok = False
            d.append(f"detail: scratch file {s} absent")
        elif s == "quarantine-slice" and not b.strip():
            ok = False
            d.append("detail: quarantine-slice empty")
        elif s == "collisions" and b.strip() and "renumber" not in les.lower():
            ok = False
            d.append("detail: collisions non-empty and lesson names no renumber map")
    legs["gate"] = int(ok)
    # census
    with tempfile.TemporaryDirectory(prefix="r42c3-") as ex:
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
    ap.add_argument("--base", default="0b606b03bf0b2a87b791aa537f6c72c941624cf0")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        tip, legs, d = evaluate(os.path.abspath(a.repo), a.tip, a.base)
    except (RuntimeError, subprocess.CalledProcessError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    met = all(legs.values())
    out = "\n".join([f"tip={tip}", "entry={entry} rows={rows} coverage={coverage} gate={gate} census={census} "
                     "met={m}".format(m=met, **legs), *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
