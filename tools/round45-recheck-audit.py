#!/usr/bin/env python3
"""round45-recheck-audit.py - kama round-45 C1 (freshness) counter.

Question: at a lane revision, does every frozen C1 key - the ten registry rows
the round-44 plan named outside the round-44 llama.cpp population (S010, S014,
S019, S038, S041, S046, S048, S055, S058, S477; S048 split into its two cited
files, so 11 keys) - carry a re-verification class that this counter re-derives
from committed evidence (byte copies of the pinned and the current upstream
file, live receipts of the official llama.cpp b11889 binary, the b11755 release
JSON, a llama.cpp ls-remote capture), is every drifted or removed key flagged in
its row's used-by entries, does SOURCES.md carry a round-45 re-verification
section, and are the b11889 binary row and the live-receipt row registered?

Frozen names (before data):
  ledger   registry/recheck-r45.tsv, header
           key id kind pin_ref new_ref pin_copy new_copy witness_pin witness_new class note
  classes  unchanged-file | holds | holds-reworded | drifted | removed
  release  b11889 = d854d98bae598388ecea1ed84396587e5edc326d, asset
           llama-b11889-bin-ubuntu-x64.tar.gz digest sha256:2076290f...d350
  model    stories260K.gguf sha256 270cba1b...256d (the round-16..18 model)

Machine witness per kind (the class is never taken from a note):
  file      pin_copy and new_copy are committed byte copies of upstream
            <repo>/<path> at the frozen pin_ref and new_ref (new_copy `-` only
            for `removed`). When the registry anchor names a sha256 for the pin
            file, pin_copy must hash to it. witness_pin and witness_new are
            verbatim excerpts (>= 12 chars after whitespace collapse); w(x, f)
            means x occurs in copy f after whitespace collapse.
              unchanged-file  sha(pin) == sha(new) and w(witness_pin, pin)
              holds           sha differ, w(witness_pin, pin) and w(witness_pin, new)
              holds-reworded  sha differ, w(witness_pin, pin), not w(witness_pin, new),
                              w(witness_new, new), not w(witness_new, pin), note >= 40
              drifted         same byte signature as holds-reworded, note >= 40
                              (reworded vs drifted is the reader's call; the
                              counter only proves the anchored text moved)
              removed         new_copy `-`, w(witness_pin, pin), note >= 40
  live      new_copy is a committed directory holding >= 3 receipt-*.json of
            schema kama-llamacpp-live/v3 whose props build_info starts with
            `b11889-d854d98`, whose model sha256 is the frozen model, all with
            one server sha256. The statement checks below are re-graded from
            each receipt; derived class = holds when every check holds in every
            receipt, drifted when any evaluated check fails, otherwise
            unverified.
              S041  checks loading_envelope_graded, health_ready, models_alias_id,
                    models_owned_by_llamacpp, metrics_not_enabled (status 501),
                    probe_model_ok, probe_mismatch all evaluated and passed
              S046  captures.health.body == '{"status":"ok"}', loading_observed
                    and loading_envelope_exact true, teardown returncode 0,
                    sigkill_sent false, port_refuses true
              S055  exactly 11 checks, all evaluated and passed, outcome pass,
                    port_listener_ownership child, teardown returncode 0
  identity  (S038) new_copy is the committed release JSON of tag b11755: its
            target_commitish is 704366d7...ad6ad and asset
            llama-b11755-bin-ubuntu-x64.tar.gz has size 22240468 and digest
            sha256:753bfa73...e226 -> holds, else drifted
  inventory (S477) new_copy is a committed `git ls-remote --tags` capture of
            ggml-org/llama.cpp: refs/tags/b11755 maps to 704366d7...ad6ad ->
            holds, else drifted (the row's figure is dated; the new count is a
            note, not a class)
A row is VALID when it is the only row for its key, id/kind/refs equal the
frozen key, and its class equals the derived class. Unverified = keys without a
valid row.
Flags: for every valid key classed drifted or removed, every used-by path of
the row's registry line at the tip contains a line naming the id and `round 45`
or `round-45`.
Section: SOURCES.md has a heading containing `Round-45 re-verification`.
New rows: the registry has a row naming `llama-b11889-bin-ubuntu-x64.tar.gz`,
the asset digest and the receipts' server sha256, and a row naming
`.ufo/waves/round-45/c1/live`; newrows counts the two (0..2).
--fetch re-downloads every file copy and the release JSON and re-runs the
ls-remote, and requires byte equality / field equality with the committed
evidence (fetch_bad counts failures; any failure invalidates the key).
met = unverified=0 flags_missing=0 section=1 newrows=2 (and fetch_bad=0 when
--fetch is given).
PREDICATE (same sentence in the preregistration): every frozen C1 key carries a
ledger class the counter re-derives from committed evidence, every drifted or
removed key is flagged in its row's used-by entries, SOURCES.md has a round-45
re-verification section, and the b11889 binary and live-receipt rows are
registered; unverified=0 flags_missing=0 section=1 newrows=2.

Output: `pop=P rows=R valid=V unverified=U unchanged=a holds=b reworded=c
drifted=d removed=e flags_missing=F section=S newrows=N fetch=0|1 fetch_bad=B
met=True|False` then `detail:` lines. Exit 0 met, 1 not met, 2 could not
evaluate. Read-only on --repo; --work (or TMPDIR) holds nothing persistent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request

LEDGER = "registry/recheck-r45.tsv"
HEADER = ["key", "id", "kind", "pin_ref", "new_ref", "pin_copy", "new_copy",
          "witness_pin", "witness_new", "class", "note"]
CLASSES = ("unchanged-file", "holds", "holds-reworded", "drifted", "removed")
RELEASE_COMMIT = "d854d98bae598388ecea1ed84396587e5edc326d"
ASSET = "llama-b11889-bin-ubuntu-x64.tar.gz"
ASSET_DIGEST = "2076290f3b80b7642e2dc165c01fbf1be386a56b4612ba45576d20527834d350"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
B11755 = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
B11755_ASSET = ("llama-b11755-bin-ubuntu-x64.tar.gz", 22240468,
                "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226")
LIVE_DIR = ".ufo/waves/round-45/c1/live"

# key -> (id, kind, upstream repo, upstream path, pin_ref, new_ref, anchor sha256 of pin file or None)
FILES = {
    "S010": ("S010", "ollama/ollama", "docs/api/openai-compatibility.mdx",
             "c1737589973d5cefd676ef16eb43835663540035", "66ab8482e08035a3238dff04a5739c4371c61bfe", None),
    "S014": ("S014", "ggml-org/ggml", "docs/gguf.md",
             "6af560d55df03ad92116e3c0a697779584477e85", "da8e2a54b919557b816b1c2beb432ccb766f7ce0", None),
    "S019": ("S019", "open-telemetry/semantic-conventions-genai", "docs/gen-ai/gen-ai-metrics.md",
             "547934afa90a34298441caf80c43b27255c3a292", "20259355b9631e3f032dcc099d1b5a2666818c42", None),
    "S048:tcp_ipv6.c": ("S048", "torvalds/linux", "net/ipv6/tcp_ipv6.c",
                        "8d3ae59288f1e7d58d76558a6ee96d533bc5019f", "c03c1a14507dfaf8b856c2608f9ac216021fc222",
                        "dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558"),
    "S048:in6.h": ("S048", "torvalds/linux", "include/uapi/linux/in6.h",
                   "8d3ae59288f1e7d58d76558a6ee96d533bc5019f", "c03c1a14507dfaf8b856c2608f9ac216021fc222",
                   "4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d"),
    "S058": ("S058", "ggml-org/ggml", "docs/gguf.md",
             "da8e2a54b919557b816b1c2beb432ccb766f7ce0", "da8e2a54b919557b816b1c2beb432ccb766f7ce0",
             "1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020"),
}
LIVE = ("S041", "S046", "S055")
POP = list(FILES) + list(LIVE) + ["S038", "S477"]
KIND = {**{k: "file" for k in FILES}, **{k: "live" for k in LIVE}, "S038": "identity", "S477": "inventory"}
REFS = {**{k: (v[3], v[4]) for k, v in FILES.items()},
        **{k: (B11755, RELEASE_COMMIT) for k in LIVE},
        "S038": ("b11755", "b11755"), "S477": (B11755, "ls-remote")}
S041_CHECKS = ("loading_envelope_graded", "health_ready", "models_alias_id", "models_owned_by_llamacpp",
               "metrics_not_enabled", "probe_model_ok", "probe_mismatch")


class EvalError(Exception):
    pass


def git(repo, *args, check=True, text=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=text)
    if check and p.returncode != 0:
        err = p.stderr if text else p.stderr.decode("utf-8", "replace")
        raise EvalError(f"git -C {repo} {' '.join(args)}: {err.strip()[:200]}")
    return p


def show_bytes(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False, text=False)
    return p.stdout if p.returncode == 0 else None


def collapse(b):
    if isinstance(b, bytes):
        b = b.decode("utf-8", "replace")
    return re.sub(r"\s+", " ", b).strip()


def has(w, blob):
    return collapse(w) in collapse(blob)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def http_get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "kama-round45-recheck-audit"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


def fetch_release_json(tag):
    p = subprocess.run(["gh", "api", f"repos/ggml-org/llama.cpp/releases/tags/{tag}"], capture_output=True)
    if p.returncode == 0:
        return json.loads(p.stdout)
    st, body = http_get(f"https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/{tag}")
    if st != 200:
        raise EvalError(f"release {tag} fetch status {st}")
    return json.loads(body)


def release_fields(js):
    asset = next((a for a in js.get("assets", []) if a.get("name") == B11755_ASSET[0]), None)
    return (js.get("target_commitish"), asset and asset.get("size"), asset and asset.get("digest"))


def derive_file(key, d, get, fetch, fbad, why):
    rid, repo, path, pin_ref, new_ref, anchor = FILES[key]
    pin = get(d["pin_copy"]) if d["pin_copy"] not in ("", "-") else None
    if pin is None:
        return why("pin_copy missing at tip")
    if anchor and sha(pin) != anchor:
        return why(f"pin_copy sha256 {sha(pin)[:12]} != anchor {anchor[:12]}")
    new = None if d["new_copy"] in ("", "-") else get(d["new_copy"])
    if d["new_copy"] not in ("", "-") and new is None:
        return why("new_copy missing at tip")
    if fetch:
        st, b = http_get(f"https://raw.githubusercontent.com/{repo}/{pin_ref}/{path}")
        if st != 200 or b != pin:
            fbad.append(key)
            return why(f"fetch pin status {st} or bytes differ")
        st, b = http_get(f"https://raw.githubusercontent.com/{repo}/{new_ref}/{path}")
        if (new is None and st != 404) or (new is not None and (st != 200 or b != new)):
            fbad.append(key)
            return why(f"fetch new status {st} or bytes differ")
    wp, wn = d["witness_pin"], d["witness_new"]
    if len(collapse(wp)) < 12:
        return why("witness_pin shorter than 12 chars")
    if not has(wp, pin):
        return why("witness_pin not in pin_copy")
    if new is None:
        return "removed"
    if sha(pin) == sha(new):
        return "unchanged-file"
    if has(wp, new):
        return "holds"
    if len(collapse(wn)) < 12 or not has(wn, new) or has(wn, pin):
        return why("anchored text moved but witness_new is not new-only text")
    return "moved"


def grade_live(receipts):
    """-> (class or None, server shas, reason)"""
    shas, fails, unev = set(), [], []
    for name, r in receipts:
        if r.get("schema") != "kama-llamacpp-live/v3":
            return None, shas, f"{name} schema {r.get('schema')}"
        bi = (((r.get("captures") or {}).get("props") or {}).get("fields") or {}).get("build_info") or ""
        if not bi.startswith("b11889-d854d98"):
            return None, shas, f"{name} build_info {bi!r}"
        if ((r.get("model") or {}).get("sha256")) != MODEL_SHA:
            return None, shas, f"{name} model sha differs"
        shas.add((r.get("server") or {}).get("sha256"))
    return "ok", shas, ""


def live_checks(key, r):
    """-> list of (name, evaluated, passed)"""
    checks = {c.get("id"): c for c in r.get("checks") or []}
    out = []
    if key == "S041":
        for cid in S041_CHECKS:
            c = checks.get(cid)
            ok = bool(c and c.get("passed"))
            if cid == "metrics_not_enabled" and c:
                ok = ok and (c.get("observed") or {}).get("status") == 501
            out.append((cid, bool(c and c.get("evaluated")), ok))
    elif key == "S046":
        cap = (r.get("captures") or {}).get("health") or {}
        td = r.get("teardown") or {}
        out.append(("health_body_exact", "body" in cap, cap.get("body") == '{"status":"ok"}'))
        out.append(("loading_observed_exact", "loading_observed" in r,
                    bool(r.get("loading_observed")) and bool(r.get("loading_envelope_exact"))))
        out.append(("teardown_rc0_nosigkill_refused", bool(td), td.get("returncode") == 0
                    and td.get("sigkill_sent") is False and td.get("port_refuses") is True))
    else:
        cl = r.get("checks") or []
        td = r.get("teardown") or {}
        out.append(("eleven_checks", True, len(cl) == 11))
        out.append(("all_evaluated_passed", bool(cl), all(c.get("evaluated") and c.get("passed") for c in cl)))
        out.append(("outcome_pass", "outcome" in r, r.get("outcome") == "pass"))
        out.append(("child_owned_graceful", bool(td), r.get("port_listener_ownership") == "child"
                    and td.get("returncode") == 0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--fetch", action="store_true", help="re-download upstream bytes and compare")
    ap.add_argument("--out")
    a = ap.parse_args()
    detail, fbad = [], []
    counts = {c: 0 for c in CLASSES}
    try:
        tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.strip()
        cache = {}

        def get(path):
            if path not in cache:
                cache[path] = show_bytes(a.repo, tip, path)
            return cache[path]

        led = get(LEDGER)
        rows, seen = {}, {}
        if led is not None:
            ls = [x for x in led.decode("utf-8", "replace").splitlines() if x.strip()]
            if ls and ls[0].split("\t") == HEADER:
                for x in ls[1:]:
                    f = x.split("\t")
                    if len(f) != len(HEADER):
                        detail.append(f"bad ledger line: {x[:60]}")
                        continue
                    d = dict(zip(HEADER, f))
                    seen[d["key"]] = seen.get(d["key"], 0) + 1
                    rows[d["key"]] = d
            else:
                detail.append("ledger header mismatch")
        live_shas = set()
        valid = {}
        for key in POP:
            d = rows.get(key)
            if d is None:
                detail.append(f"{key} missing")
                continue
            reasons = []

            def why(msg):
                reasons.append(msg)
                return None

            rid = key.split(":")[0]
            kind = KIND[key]
            derived = None
            if seen[key] > 1:
                why("duplicate key")
            elif (d["id"], d["kind"]) != (rid, kind) or (d["pin_ref"], d["new_ref"]) != REFS[key]:
                why(f"id/kind/refs differ from frozen {rid} {kind} {REFS[key]}")
            elif d["class"] not in CLASSES:
                why(f"class {d['class']!r} not in vocabulary")
            elif kind == "file":
                derived = derive_file(key, d, get, a.fetch, fbad, why)
                if derived == "moved":
                    derived = d["class"] if d["class"] in ("holds-reworded", "drifted") else None
                    if derived is None:
                        why("anchored text moved: class must be holds-reworded or drifted")
                if derived in ("holds-reworded", "drifted", "removed") and len(d["note"]) < 40:
                    derived = why("note shorter than 40 chars")
            elif kind == "live":
                lst = git(a.repo, "ls-tree", "--name-only", f"{tip}:{d['new_copy']}", check=False)
                names = sorted(n for n in lst.stdout.split() if re.fullmatch(r"receipt-[^/]*\.json", n)) \
                    if lst.returncode == 0 else []
                if d["new_copy"] != LIVE_DIR or len(names) < 3:
                    why(f"need >= 3 receipt-*.json under {LIVE_DIR}")
                else:
                    recs = []
                    for n in names:
                        try:
                            recs.append((n, json.loads(get(f"{LIVE_DIR}/{n}"))))
                        except (TypeError, ValueError):
                            why(f"{n} not JSON")
                    if not reasons:
                        ok, shas, msg = grade_live(recs)
                        if ok is None:
                            why(msg)
                        elif len(shas) != 1 or None in shas:
                            why(f"receipts disagree on server sha256 {sorted(map(str, shas))}")
                        else:
                            live_shas |= shas
                            res = [c for _, r in recs for c in live_checks(key, r)]
                            if any(ev and not ok for _, ev, ok in res):
                                derived = "drifted"
                            elif all(ev and ok for _, ev, ok in res):
                                derived = "holds"
                            else:
                                why("a statement check was not evaluated in some receipt")
                            if derived == "drifted" and len(d["note"]) < 40:
                                derived = why("note shorter than 40 chars")
            elif kind == "identity":
                b = get(d["new_copy"]) if d["new_copy"] not in ("", "-") else None
                try:
                    js = json.loads(b) if b is not None else None
                except ValueError:
                    js = None
                if js is None or js.get("tag_name") != "b11755":
                    why("release JSON of tag b11755 missing at tip")
                else:
                    if a.fetch:
                        try:
                            if release_fields(fetch_release_json("b11755")) != release_fields(js):
                                fbad.append(key)
                                why("fetched release fields differ from committed JSON")
                        except EvalError as e:
                            fbad.append(key)
                            why(str(e))
                    if not reasons:
                        derived = "holds" if release_fields(js) == (B11755, *B11755_ASSET[1:]) else "drifted"
            else:
                b = get(d["new_copy"]) if d["new_copy"] not in ("", "-") else None
                if b is None:
                    why("ls-remote capture missing at tip")
                else:
                    refs = dict((ln.split("\t")[1], ln.split("\t")[0]) for ln in collapse_lines(b) if "\t" in ln)
                    if "refs/tags/b11755" not in refs:
                        why("capture has no refs/tags/b11755 line")
                    else:
                        if a.fetch:
                            p = subprocess.run(["git", "ls-remote", "https://github.com/ggml-org/llama.cpp.git",
                                                "refs/tags/b11755"], capture_output=True, text=True)
                            if p.returncode != 0 or not p.stdout.startswith(refs["refs/tags/b11755"]):
                                fbad.append(key)
                                why("fetched refs/tags/b11755 differs from capture")
                        if not reasons:
                            derived = "holds" if refs["refs/tags/b11755"] == B11755 else "drifted"
            if not reasons and derived is not None and derived != d["class"]:
                why(f"ledger class {d['class']} != derived {derived}")
            if reasons or derived is None:
                detail.append(f"{key} invalid: {'; '.join(reasons) or 'no class derived'}")
                continue
            valid[key] = d
            counts[d["class"]] += 1
        sources = (get("corpus/SOURCES.md") or b"").decode("utf-8", "replace").splitlines()
        reg = {}
        for x in sources:
            m = re.match(r"^ {0,3}\|\s*(S\d{3,})\s*\|", x)
            if m:
                reg[m.group(1)] = x
        flags_missing = 0
        for key, d in valid.items():
            if d["class"] not in ("drifted", "removed"):
                continue
            line = reg.get(d["id"])
            if line is None:
                flags_missing += 1
                detail.append(f"{key} registry row missing")
                continue
            used = [u.strip() for u in line.rstrip().rstrip("|").split("|")[-1].split(",") if u.strip()]
            for u in used:
                t = (get(u) or b"").decode("utf-8", "replace")
                if not any(d["id"] in ln and re.search(r"round[ -]45", ln, re.I) for ln in t.splitlines()):
                    flags_missing += 1
                    detail.append(f"{key} not flagged in {u}")
        section = int(any(x.startswith("#") and "Round-45 re-verification" in x for x in sources))
        newrows = 0
        rowtexts = list(reg.values())
        if any(ASSET in x and ASSET_DIGEST in x and live_shas and all(s in x for s in live_shas) for x in rowtexts):
            newrows += 1
        else:
            detail.append("no registry row names the b11889 asset, its digest and the receipts' server sha256")
        if any(LIVE_DIR in x for x in rowtexts):
            newrows += 1
        else:
            detail.append(f"no registry row names {LIVE_DIR}")
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    unverified = len(POP) - len(valid)
    met = unverified == 0 and flags_missing == 0 and section == 1 and newrows == 2 and not fbad
    line = (f"pop={len(POP)} rows={len(rows)} valid={len(valid)} unverified={unverified} "
            f"unchanged={counts['unchanged-file']} holds={counts['holds']} reworded={counts['holds-reworded']} "
            f"drifted={counts['drifted']} removed={counts['removed']} flags_missing={flags_missing} "
            f"section={section} newrows={newrows} fetch={int(a.fetch)} fetch_bad={len(fbad)} met={met}")
    text = "\n".join([f"tip={tip}", line] + [f"detail: {x}" for x in detail]) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    sys.stdout.write(text)
    return 0 if met else 1


def collapse_lines(b):
    return b.decode("utf-8", "replace").splitlines()


if __name__ == "__main__":
    sys.exit(main())
