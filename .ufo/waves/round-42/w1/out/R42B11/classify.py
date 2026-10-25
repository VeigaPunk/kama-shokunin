#!/usr/bin/env python3
"""R42B11 final: classify every 8..63-char hex run in the lane's .md/.tsv
documents at a revision, resolve digest abbreviations, and split the residue by
hand-checked kind (git object id, statement key, container id, ip hex, numeric).

Writes only --out (TSV) and --json.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys

HEXRUN = re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{8,63}(?![0-9A-Za-z])")
HEX40 = re.compile(r"(?<![0-9A-Za-z])[0-9a-fA-F]{40}(?![0-9A-Za-z])")
FULL = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
LEDGER = "registry/digest-ledger.tsv"

# Hand-checked kinds for tokens the mechanical rules cannot settle. Every entry
# quotes the document context that justifies it.
OVERRIDE = {
    "0c47e832": ("digest", "round-26-verifier-spotcheck.md:190 'The receipt's channel sha256 `0c47e832…`'"),
    "0ccd533544": ("statement-key", "SCORECARD.md:1509 'SA29:SCORECARD.md:Q:0ccd533544:0'"),
    "17a7db7c81": ("statement-key", "SCORECARD.md:1514 'SA29:SCORECARD.md:P:17a7db7c81:0'"),
    "1c6c1f3e4c": ("statement-key", "SCORECARD.md:1513 'SA29:SCORECARD.md:P:1c6c1f3e4c:0'"),
    "312b3e69b1": ("statement-key", "SCORECARD.md:1508 'SA29:SCORECARD.md:P:312b3e69b1:0'"),
    "422b431349": ("statement-key", "SCORECARD.md:1569 'SA30:SCORECARD.md:Q:422b431349:o0' (also listed as a commit token at round-30-verifier-spotcheck.md:17)"),
    "4a6f7c911e": ("statement-key", "SCORECARD.md:1568 'SA30:SCORECARD.md:Q:4a6f7c911e:o0' (also listed as a commit token at round-30-verifier-spotcheck.md:17)"),
    "4c5d902830": ("statement-key", "SCORECARD.md:1510 'SA29:SCORECARD.md:Q:4c5d902830:0'"),
    "4f8083e30a": ("statement-key", "SCORECARD.md:1507 'SA29:SCORECARD.md:Q:4f8083e30a:0'"),
    "980355388a": ("statement-key", "SCORECARD.md:1506 'SA29:SCORECARD.md:P:980355388a:0'"),
    "a7e98b1030": ("statement-key", "SCORECARD.md:1512 'SA29:SCORECARD.md:Q:a7e98b1030:0'"),
    "f1021c03db": ("statement-key", "SCORECARD.md:1511 'SA29:SCORECARD.md:Q:f1021c03db:0'"),
    "f4c42debcc": ("statement-key", "SCORECARD.md:1504 'SA29:SCORECARD.md:Q:f4c42debcc:0'"),
    "0100007f": ("ip-hex", "loopback-listener-ownership.md:18 '| `127.0.0.1` | tcp `0100007F` |'"),
    "010310ac": ("ip-hex", "round-18-verifier-spotcheck.md:108 'its only address example (line 18, `010310AC:9C4C`)'"),
    "bda15c10": ("container-id", "listener-census.md:50 'container `172.18.0.4` = `docker-jitsi-meet-jvb-1` `bda15c10…`'"),
    "f92b0236": ("container-id", "listener-census.md:51 'container `172.18.0.5` = `docker-jitsi-meet-jicofo-1` `f92b0236…`'"),
    "04411e88": ("git-object", "round-36-verifier-spotcheck.md:20 'fleet master `04411e88`'"),
    "0522e67a": ("git-object", "consumer-registry.md:194 'HEAD `0522e67a`' (deleted checkout)"),
    "10094ed1": ("git-object", "SCORECARD.md:2065 '`28a8bf50` \"baseline\", `10094ed1` \"mut1\"'"),
    "28a8bf50": ("git-object", "SCORECARD.md:2065 '`28a8bf50` \"baseline\"'"),
    "f3517a161e": ("git-object", "SCORECARD.md:2065 '`f3517a161e` \"mut2\"'"),
    "873c5d77": ("git-object", "round-40-verifier-spotcheck.md:19 'detached on the mutation-sandbox lineage (`873c5d77 mut4 …`)'"),
    "13786fbb": ("git-object", "SOURCES.md:54 'byte-identical at b11757 (13786fbb)'; round-17-verifier-spotcheck.md:180 '`git ls-remote …refs/tags/b11757` = `13786fbb…`'"),
    "4c3c5810": ("git-object", "SOURCES.md:13 'repo master 4c3c5810 when the metrics section was read'"),
    "50ed4c01": ("git-object", "gguf-runtime-compatibility-boundary.md:21 '`docs/advanced_features/quantization.md` at commit `50ed4c01`'"),
    "5725fa7d3": ("git-object", "round-1.md:69 'HEADs `5725fa7d3` / `0522e67a`'"),
    "58f49f42": ("git-object", "round-33-verifier-spotcheck.md:15 'report/tip cites c587f10e, 4fdd4e66, …'"),
    "77ff9c05": ("git-object", "round-33-verifier-spotcheck.md:15 commit-citation list"),
    "a1ff8708": ("git-object", "round-33-verifier-spotcheck.md:15 commit-citation list"),
    "5b108c1a": ("git-object", "round-19-verifier-spotcheck.md:104 '`working-tree-on-5b108c1a…`, not on a commit'"),
    "28d34a63": ("git-object", "round-24.md:270 'unknown: unavailable required object: 28d34a63…'"),
    "63a0d4df": ("git-object", "round-41-verifier-spotcheck.md:17 'committed by `kama-shokunin` (`63a0d4df`)'"),
    "77091cea": ("git-object", "sglang-docs-version-pinning.md:23 '`radix_eviction_policy.mdx` | commit `77091cea…`'"),
    "7850a92c": ("git-object", "round-32-verifier-spotcheck.md:15 '`aca07f21…`/`7850a92c…` are synthetic control fixture' commits"),
    "aca07f21": ("git-object", "round-32-verifier-spotcheck.md:15 synthetic control fixture commit"),
    "7b536e11": ("git-object", "round-39-verifier-spotcheck.md:8 'erratum commit `7b536e11`'"),
    "8e953f68": ("git-object", "LOG.md:2241 'attempt 1's commits `eaa4106c` and `8e953f68`'"),
    "eaa4106c": ("git-object", "LOG.md:2241 'attempt 1's commits `eaa4106c` and `8e953f68`'"),
    "964f443e": ("git-object", "LOG.md:56 '(HEAD `964f443e`)' (deleted checkout)"),
    "a65bb98d": ("git-object", "round-29.md:166 'evidence-timestamps.py @ a65bb98d'"),
    "ac9859f4e747": ("git-object", "round-19-verifier-spotcheck.md:24 '`kama-shokunin ac9859f4e747… 03:47:37`' (fleet commit)"),
    "c0ae8d0d": ("git-object", "round-39-verifier-spotcheck.md:14 fleet commit"),
    "d234c359": ("git-object", "round-27-verifier-spotcheck.md:47 'prompt committed before the report | `git log` | `d234c359`'"),
    "d34f7b23": ("git-object", "sglang-docs-version-pinning.md:24 '`session_radix_cache.mdx` | commit `d34f7b23…`'"),
    "e4cd8af3": ("git-object", "round-25-verifier-spotcheck.md:50 '`.ufo/prompts/kama-round-25.md`, committed `e4cd8af3`'"),
    "e52edfda": ("git-object", "round-39-verifier-spotcheck.md:8 'attempt-1 body `e52edfda`' (fleet commit)"),
    "ea72c3ae": ("git-object", "round-29-verifier-spotcheck.md:62 'trees at ea72c3ae/40660352'"),
    "8057282c": ("git-object", "round-27-verifier-spotcheck.md:45 'state branch=master local=8057282c… remote=8057282c…'"),
    "227dd1eeff95": ("git-object", "round-29-verifier-spotcheck.md:76 '`6de225c289b7…` and `227dd1eeff95…` … landed hashes'"),
    "026eede9": ("git-object", "round-30-verifier-spotcheck.md:17 '15 commit tokens (`026eede9`, …)'"),
    "24ce96bc": ("digest", "round-30-verifier-spotcheck.md:37 'three identical digests (`24ce96bc…`, `db4c39bb…`)'; instrument-run-agreement.md:19 'digest=24ce96bc3905'"),
    "24ce96bc3905": ("digest", "instrument-run-agreement.md:19 '`IA runs=3 agree=3 disagree=0 digest=24ce96bc3905 exit=0`'"),
    "db4c39bb": ("digest", "round-30-verifier-spotcheck.md:37 'three identical digests (`24ce96bc…`, `db4c39bb…`)'"),
    "db4c39bbbdfd": ("digest", "instrument-run-agreement.md:21 '`IA runs=3 agree=3 disagree=0 digest=db4c39bbbdfd exit=0`'"),
    "1f9d7b73": ("digest", "LOG.md:1811 'sha256 1f9d7b73…0050'; LOG.md:1823 '`1f9d7b73…4050`; the abbreviation `1f9d7b73…0050`'"),
    "3ad0df68e8423a3b": ("digest", "round-38-verifier-spotcheck.md:74 'cites `SOURCES.append.md` sha256 `3ad0df68e8423a3b…` which matches neither current package bytes (`3ad0df68504e1f49…`)'"),
    "5ad2c74d": ("digest", "round-29.md:159 'sandbox diag-counter sha 5ad2c74d…'"),
    "5cb9f486": ("digest", "SCORECARD.md:1063 'live v3 receipt with 10 links (`5cb9f486…`)'"),
    "612b0a74": ("digest", "round-24.md:350 'population sha256 `612b0a74…2ed88`'"),
    "6c216313": ("digest", "SCORECARD.md:1063 '`install_tree_sha256` unchanged (6c216313…)'; round-19-verifier-spotcheck.md:86 'sha256 of the sorted `name sha` lines is `6c216313…85a2c`'"),
    "6c216313a88d71b1": ("digest", "llamacpp-loading-lifecycle.md:107 'install tree of 51 files hashed (`install_tree_sha256` `6c216313a88d71b1…`)'"),
    "6fb1ec15": ("git-object", "round-37-verifier-spotcheck.md:104 'pin the r36 lesson blob (`6fb1ec15…`)' (git blob id; `git cat-file -t 6fb1ec15` = blob)"),
    "72e81bc6": ("digest", "LOG.md:980 '`taskCall` sha256 `72e81bc6…0812`'"),
    "8b7408e6": ("digest", "round-37-verifier-spotcheck.md:105 'fleet-report blob (`8b7408e6…`)' (fleet-repo content digest)"),
    "9c4c8a64": ("digest", "round-17.md:191 'bound to `taskCall` sha256 `9c4c8a64…2958`'"),
    "b6a31a8e": ("digest", "SKILL.md:1236 'server SHA-256 `b6a31a8e…d804`' (host binary)"),
    "b6a31a8e97615a2a": ("digest", "llamacpp-loading-lifecycle.md:106 'launcher sha256 `b6a31a8e97615a2a…`'"),
    "b9a45a06": ("digest", "round-27-verifier-spotcheck.md:121 'req1/req2/req3 response blobs hash identically (`9ea801fb…b9a45a06`)'"),
    "baa09177": ("digest", "llamacpp-loading-lifecycle.md:120 'sha256 `baa09177…957c`'"),
    "cdf02ba7": ("digest", "round-16-verifier-spotcheck.md:57 'The build `taskCall` digest `cdf02ba7…`'"),
    "d86c4a94": ("digest", "round-31-verifier-spotcheck.md:23 '`sha256sum .ufo/waves/round-31/count-c1.py` → `d86c4a94…9216`'"),
    "f29fab8d": ("digest", "round-23.md:113 'population `f29fab8d…364a`'"),
}


def git(repo, *args, data=None):
    p = subprocess.run(["git", "-C", repo, *args], input=data, capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def _hash_blobs(out):
    blobs, i = set(), 0
    while i < len(out):
        j = out.index(b"\n", i)
        _, typ, size = out[i:j].decode().split()
        size = int(size)
        if typ == "blob":
            blobs.add(hashlib.sha256(out[j + 1:j + 1 + size]).hexdigest())
        i = j + 1 + size + 1
    return blobs


def blobs_reachable(repo, rev):
    ids = [l.split(" ", 1)[0] for l in git(repo, "rev-list", "--objects", rev).decode().split("\n") if l]
    return _hash_blobs(subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                                      input="".join(i + "\n" for i in ids).encode(),
                                      capture_output=True).stdout)


def blobs_store(repo):
    ids = [l.split()[0] for l in git(repo, "cat-file", "--batch-all-objects",
                                    "--batch-check=%(objectname) %(objecttype)").decode().split("\n")
           if l.endswith(" blob")]
    return _hash_blobs(subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                                      input="".join(i + "\n" for i in ids).encode(),
                                      capture_output=True).stdout)


def objects_store(repo):
    return {l.split()[0] for l in git(repo, "cat-file", "--batch-all-objects",
                                      "--batch-check=%(objectname) %(objecttype)").decode().split("\n") if l}


def docs_at(repo, rev):
    out = []
    for path in git(repo, "ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0"):
        if not path or path.startswith(".ufo/") or not path.endswith((".md", ".tsv")):
            continue
        out.append((path, git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace")))
    return out


def parse_ledger(text):
    rows = {}
    for i, line in enumerate(text.split("\n")):
        if not line or (i == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        rows[c[0]] = {"cls": c[1], "subject": c[2], "path": c[3]}
    return rows


def form_of(text, start, end, tok):
    tail, head = text[end:end + 3], text[max(0, start - 3):start]
    if tail.startswith("\u2026") or tail.startswith("..."):
        m = re.match(r"(?:\u2026|\.\.\.)\s*([0-9a-fA-F]{4,63})(?![0-9A-Za-z])", text[end:end + 90])
        if m and m.group(1).lower() != tok:
            return "prefix\u2026suffix", m.group(1).lower()
        return "prefix\u2026", None
    if head.endswith("\u2026") or head.endswith("..."):
        return "\u2026suffix", None
    return "bare", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    rev = git(a.repo, "rev-parse", "--verify", f"{a.rev}^{{commit}}").decode().strip()
    reach, store, objs = blobs_reachable(a.repo, rev), blobs_store(a.repo), objects_store(a.repo)
    docs = docs_at(a.repo, rev)
    ledger = parse_ledger(dict(docs).get(LEDGER, ""))
    full_tokens = collections.Counter()
    cited_sha1 = set()
    occ = []
    for path, text in docs:
        for ln, line in enumerate(text.split("\n"), 1):
            for m in FULL.finditer(line):
                full_tokens[m.group(0)] += 1
            for m in HEX40.finditer(line):
                cited_sha1.add(m.group(0).lower())
            for m in HEXRUN.finditer(line):
                tok = m.group(0).lower()
                form, suffix = form_of(line, m.start(), m.end(), tok)
                occ.append({"path": path, "line": ln, "tok": tok, "form": form, "suffix": suffix,
                            "numeric": bool(re.search(r"\.\d*$", line[max(0, m.start() - 2):m.start()])
                                            or re.match(r"e[+-]?\d", line[m.end():m.end() + 5], re.I)),
                            "ctx": line.strip()})

    groups = collections.OrderedDict()
    for o in occ:
        key = (o["tok"], o["form"], o["suffix"])
        g = groups.setdefault(key, {"tok": o["tok"], "form": o["form"], "suffix": o["suffix"],
                                    "n": 0, "sites": [], "numeric": False, "ctx": o["ctx"]})
        g["n"] += 1
        g["sites"].append(f'{o["path"]}:{o["line"]}')
        g["numeric"] |= o["numeric"]

    rows = []
    for g in groups.values():
        tok, suffix, form = g["tok"], g["suffix"], g["form"]

        def m(d):
            if form == "\u2026suffix":
                return d.endswith(tok)
            if suffix:
                return d.startswith(tok) and d.endswith(suffix)
            return d.startswith(tok)

        cand = {"blob_reach": sorted(d for d in reach if m(d)),
                "blob_store": sorted(d for d in store if m(d)),
                "ledger": sorted(d for d in ledger if m(d)),
                "cited_full": sorted(d for d in full_tokens if m(d))}
        objp = sorted(o for o in objs if o.startswith(tok))
        sha1p = sorted(s for s in cited_sha1 if s.startswith(tok))
        if tok.isdigit() or g["numeric"]:
            kind, cls = "numeric", "not-a-digest"
        elif tok in OVERRIDE:
            kind, cls = OVERRIDE[tok][0], ("digest" if OVERRIDE[tok][0] == "digest" else "not-a-digest")
        elif cand["blob_reach"] or cand["ledger"] or cand["cited_full"]:
            kind, cls = "digest", "digest"
        elif objp or sha1p or len(tok) == 40:
            kind, cls = "git-object", "not-a-digest"
        elif len(tok) == 32:
            kind, cls = "md5-or-32hex", "not-a-digest"
        else:
            kind, cls = "unclassified", "unclassified"
        if kind == "digest":
            if cand["ledger"] and not cand["blob_reach"]:
                res = "ledger"
            elif cand["blob_reach"]:
                res = "blob"
            elif cand["cited_full"]:
                res = "cited-full-only"
            else:
                res = "nothing"
        else:
            res = ""
        union = {d for k in ("ledger", "blob_reach", "cited_full") for d in cand[k]}
        amb = ""
        if kind == "digest" and len(union) > 1:
            amb = "prefix-ambiguous"
        rows.append({"tok": tok, "form": form, "suffix": suffix or "", "len": len(tok), "n": g["n"],
                     "kind": kind, "class": cls, "resolution": res,
                     "digest": (cand["ledger"] or cand["blob_reach"] or cand["cited_full"] or [""])[0],
                     "n_cand": len({d for k in ("ledger", "blob_reach", "cited_full") for d in cand[k]}),
                     "obj_prefix": objp[0] if objp else "", "sha1_prefix": sha1p[0] if sha1p else "",
                     "ambiguous": amb, "sites": g["sites"],
                     "reason": OVERRIDE.get(tok, ("", ""))[1] if tok in OVERRIDE else ""})

    with open(a.out, "w") as f:
        f.write("abbrev\tform\tsuffix\tlen\toccurrences\tkind\tclass\tresolution\tdigest\tn_cand"
                "\tobj_prefix\tsha1_prefix\tambiguous\tsites\treason\n")
        order = {"digest": 0, "git-object": 1, "unclassified": 2}
        for r in sorted(rows, key=lambda r: (order.get(r["kind"], 3), r["resolution"], r["tok"])):
            f.write("\t".join(str(r[k]) for k in ("tok", "form", "suffix", "len", "n", "kind", "class",
                                                  "resolution", "digest", "n_cand", "obj_prefix",
                                                  "sha1_prefix", "ambiguous")) +
                    "\t" + " ".join(r["sites"]) + "\t" + r["reason"].replace("\t", " ") + "\n")

    dig = [r for r in rows if r["kind"] == "digest"]
    summary = {
        "rev": rev, "docs": len(docs),
        "full64_distinct": len(full_tokens), "full64_occurrences": sum(full_tokens.values()),
        "hexruns_distinct": len(rows), "hexruns_occurrences": sum(r["n"] for r in rows),
        "kinds_distinct": dict(collections.Counter(r["kind"] for r in rows)),
        "kinds_occurrences": dict(collections.Counter({k: sum(r["n"] for r in rows if r["kind"] == k)
                                                       for k in {r["kind"] for r in rows}})),
        "digest_distinct": len(dig), "digest_occurrences": sum(r["n"] for r in dig),
        "digest_by_resolution_distinct": dict(collections.Counter(r["resolution"] for r in dig)),
        "digest_by_resolution_occurrences": dict(collections.Counter({k: sum(r["n"] for r in dig if r["resolution"] == k)
                                                                      for k in {r["resolution"] for r in dig}})),
        "digest_nothing_distinct": sum(1 for r in dig if r["resolution"] == "nothing"),
        "digest_nothing_occurrences": sum(r["n"] for r in dig if r["resolution"] == "nothing"),
        "ambiguous": [r["tok"] for r in rows if r["ambiguous"]],
        "unclassified": [r["tok"] for r in rows if r["kind"] == "unclassified"],
        "digest_files": dict(collections.Counter(s.rsplit(":", 1)[0] for r in dig for s in r["sites"])),
    }
    with open(a.json, "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
