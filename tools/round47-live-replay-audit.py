#!/usr/bin/env python3
"""round47-live-replay-audit.py - kama round-47 C2 (operability, sourced) counter.

Question: at a lane revision, can a fresh session re-run the lane's live
llama.cpp lifecycle evidence from committed bytes alone? Round-45 closure N-E /
D3 and round-46 closure D5 found that the live receipts name a server binary
and a model only by host paths (~/.local/opt/..., ~/.cache/...) and a sha256,
and a log path inside deleted seat scratch: when the cache file vanished the
receipts could not be re-run, and the log pointer was dead. This counter asks
for receipts that carry where every input came from, and for a replay tool
that re-acquires those inputs into an empty home, verifies each digest,
re-runs the lifecycle and agrees with the original, and refuses a receipt
whose recorded digest does not match what it downloads.

Frozen names (before data):
  release     llama.cpp b11909 = caa8191df159f764fb0160e3d2fc6be008948aee
              (gh api repos/ggml-org/llama.cpp/releases/tags/b11909 at freeze:
              published 2026-10-26T21:00:58Z, prerelease true)
  asset       https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
              sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b
              (the release record's `digest`)
  receipts    .ufo/waves/round-47/c2/live/receipt-1.json, -2.json, -3.json
  replay      tools/kama-live-replay.py
  live tool   tools/kama-llamacpp-live.py (schema kama-llamacpp-live/v4)

Receipt contract (v4 additions to the v3 receipt):
  "schema": "kama-llamacpp-live/v4"
  "provenance": {"server": {"asset_url": <url>, "asset_sha256": <64-hex>,
                            "member": <path of llama-server inside the archive>},
                 "model":  {"url": <https url>, "sha256": <64-hex>}}
  teardown.log_path: null, or a repo-relative path committed at the tip.
Replay contract: `python3 tools/kama-live-replay.py --receipt R --work DIR --out J`
re-acquires the asset and the model from the receipt's provenance into DIR,
verifies both sha256 values before use, runs tools/kama-llamacpp-live.py with
the receipt's alias, ctx and threads, and writes J: one JSON object with
"schema": "kama-live-replay/v1", "rerun_receipt" (path of the new live
receipt or null), "match" (bool) and "refused" (reason string or null). Exit 0
when the rerun matches, 1 when it ran and differs, 2 when it refused or could
not run.

Legs:
  receipts  each of the three receipts exists at --tip with schema
            kama-llamacpp-live/v4, outcome pass, >= 10 evaluated checks, every
            evaluated check passed; provenance.server.asset_url and asset_sha256
            equal the frozen asset and digest; provenance.server.member is a
            non-empty string; provenance.model.url starts with https:// and
            provenance.model.sha256 equals model.sha256 (64-hex);
            captures.props.fields.build_info starts with `b11909-`;
            teardown.log_path is null or a relative path (no `..`) that exists
            at --tip.
  replay    from `git archive <tip>` extracted under --scratch, with HOME,
            XDG_CACHE_HOME and TMPDIR inside --scratch, the replay tool on
            receipt-1 exits 0 and its J names a rerun receipt that this counter
            checks itself: schema v4, outcome pass, started_utc not earlier than
            this counter's start, server.sha256 and model.sha256 equal to
            receipt-1's, server.realpath and model.path inside --scratch, and
            for every check id receipt-1 evaluated, the rerun evaluated it with
            the same passed value.
  tamper    the replay tool on two copies of receipt-1, one with
            provenance.model.sha256 and one with provenance.server.asset_sha256
            altered in its first hex digit, each exits nonzero and leaves no
            rerun receipt with outcome pass.
  newrow    corpus/SOURCES.md at --tip has a registry row (a line starting with
            `| S`) that contains `b11909` and the release commit.
met = receipts and replay and tamper and newrow.
PREDICATE (same sentence in the preregistration): three committed b11909 live
receipts record where their server and model came from, a fresh-home replay
from committed bytes re-acquires and digest-verifies both and reproduces
receipt-1's checks, a receipt with a wrong recorded digest is refused, and
b11909 is registered as a source; receipts=1 replay=1 tamper=1 newrow=1.

Output: `receipts=0|1 replay=0|1 tamper=0|1 newrow=0|1 rerun_checks=N met=True|False`,
then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate (git failure).
Read-only on --repo; everything else lives under --scratch and is removed on exit.
Needs network access to github.com and the model URL for the replay legs.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone

RELEASE = "b11909"
COMMIT = "caa8191df159f764fb0160e3d2fc6be008948aee"
ASSET_URL = ("https://github.com/ggml-org/llama.cpp/releases/download/b11909/"
             "llama-b11909-bin-ubuntu-x64.tar.gz")
ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"
RECEIPTS = [f".ufo/waves/round-47/c2/live/receipt-{n}.json" for n in (1, 2, 3)]
REPLAY = "tools/kama-live-replay.py"
SCHEMA = "kama-llamacpp-live/v4"
HEX64 = re.compile(r"[0-9a-f]{64}")


class EvalError(Exception):
    pass


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def at_tip(repo, tip, path):
    p = git(repo, "show", f"{tip}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


def parse_time(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def inside(path, root):
    try:
        rp, rr = os.path.realpath(str(path)), os.path.realpath(root)
    except (TypeError, ValueError):
        return False
    return rp == rr or rp.startswith(rr + os.sep)


def evaluated(rec):
    out = {}
    for c in rec.get("checks") or []:
        if isinstance(c, dict) and c.get("evaluated"):
            out[c.get("id")] = c.get("passed")
    return out


def check_receipt(repo, tip, path, rec, detail):
    probs = []
    if rec.get("schema") != SCHEMA:
        probs.append(f"schema {rec.get('schema')!r}")
    if rec.get("outcome") != "pass":
        probs.append(f"outcome {rec.get('outcome')!r}")
    ev = evaluated(rec)
    if len(ev) < 10 or not all(v is True for v in ev.values()):
        probs.append(f"evaluated={len(ev)} all_passed={all(v is True for v in ev.values())}")
    prov = rec.get("provenance") if isinstance(rec.get("provenance"), dict) else {}
    srv = prov.get("server") if isinstance(prov.get("server"), dict) else {}
    mdl = prov.get("model") if isinstance(prov.get("model"), dict) else {}
    if srv.get("asset_url") != ASSET_URL:
        probs.append(f"provenance.server.asset_url {srv.get('asset_url')!r}")
    if srv.get("asset_sha256") != ASSET_SHA:
        probs.append(f"provenance.server.asset_sha256 {srv.get('asset_sha256')!r}")
    if not isinstance(srv.get("member"), str) or not srv.get("member"):
        probs.append("provenance.server.member missing")
    if not str(mdl.get("url") or "").startswith("https://"):
        probs.append(f"provenance.model.url {mdl.get('url')!r}")
    msha = (rec.get("model") or {}).get("sha256") if isinstance(rec.get("model"), dict) else None
    if not (isinstance(mdl.get("sha256"), str) and HEX64.fullmatch(mdl.get("sha256"))
            and mdl.get("sha256") == msha):
        probs.append("provenance.model.sha256 is not model.sha256 (64-hex)")
    try:
        bi = rec["captures"]["props"]["fields"]["build_info"]
    except (KeyError, TypeError):
        bi = None
    if not str(bi or "").startswith(RELEASE + "-"):
        probs.append(f"build_info {bi!r}")
    td = rec.get("teardown") if isinstance(rec.get("teardown"), dict) else {}
    lp = td.get("log_path", "absent-key")
    if lp == "absent-key":
        probs.append("teardown.log_path key missing")
    elif lp is not None:
        if (not isinstance(lp, str) or os.path.isabs(lp) or ".." in lp.split("/")
                or git(repo, "cat-file", "-e", f"{tip}:{lp}", check=False).returncode != 0):
            probs.append(f"teardown.log_path {lp!r} is not a committed repo-relative path")
    for p in probs:
        detail.append(f"receipts: {path}: {p}")
    return not probs


def run_replay(tree, receipt, work, outj, env, timeout=1200):
    try:
        p = subprocess.run([sys.executable, os.path.join(tree, REPLAY), "--receipt", receipt,
                            "--work", work, "--out", outj], capture_output=True, text=True,
                           env=env, cwd=tree, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, None, "timeout"
    try:
        with open(outj) as fh:
            j = json.load(fh)
    except (OSError, ValueError):
        j = None
    return p.returncode, j, (p.stdout[-400:] + " | " + p.stderr[-400:]).replace("\n", " ")


def load_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    t0 = datetime.now(timezone.utc)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r47c2-", dir=root)
    detail = []
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
            arc = git(a.repo, "archive", "--format=tar", tip).stdout
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        tree = os.path.join(S, "tree")
        os.makedirs(tree)
        with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
            # links are skipped (the lane tree holds absolute symlinks in old wave evidence)
            tf.extractall(tree, filter=lambda m, dest: None if (m.issym() or m.islnk())
                          else tarfile.data_filter(m, dest))
        env = dict(os.environ)
        for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
            d = os.path.join(S, sub)
            os.makedirs(d, exist_ok=True)
            env[k] = d
        # receipts
        recs = {}
        rok = True
        for path in RECEIPTS:
            raw = at_tip(a.repo, tip, path)
            rec = None
            if raw is not None:
                try:
                    rec = json.loads(raw)
                except ValueError:
                    rec = None
            if not isinstance(rec, dict):
                detail.append(f"receipts: {path} absent or not a JSON object at tip")
                rok = False
                continue
            recs[path] = rec
            if not check_receipt(a.repo, tip, path, rec, detail):
                rok = False
        have_tool = at_tip(a.repo, tip, REPLAY) is not None
        if not have_tool:
            detail.append(f"{REPLAY} absent at tip")
        r1 = recs.get(RECEIPTS[0])
        # replay
        rep, nchecks = False, 0
        if have_tool and r1 is not None:
            code, j, tail = run_replay(tree, os.path.join(tree, RECEIPTS[0]), os.path.join(S, "work-replay"),
                                       os.path.join(S, "replay.json"), env)
            probs = []
            rr = load_json(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
            if code != 0:
                probs.append(f"exit {code}: {tail}")
            if not isinstance(j, dict) or j.get("schema") != "kama-live-replay/v1":
                probs.append("replay JSON missing or schema is not kama-live-replay/v1")
            if not isinstance(rr, dict):
                probs.append("rerun receipt missing")
            else:
                st = parse_time(rr.get("started_utc"))
                if rr.get("schema") != SCHEMA or rr.get("outcome") != "pass":
                    probs.append(f"rerun schema/outcome {rr.get('schema')!r}/{rr.get('outcome')!r}")
                if st is None or st < t0:
                    probs.append(f"rerun started_utc {rr.get('started_utc')!r} precedes counter start")
                srv, mdl = rr.get("server") or {}, rr.get("model") or {}
                if srv.get("sha256") != (r1.get("server") or {}).get("sha256"):
                    probs.append("rerun server.sha256 differs from receipt-1")
                if mdl.get("sha256") != (r1.get("model") or {}).get("sha256"):
                    probs.append("rerun model.sha256 differs from receipt-1")
                if not inside(srv.get("realpath"), S) or not inside(mdl.get("path"), S):
                    probs.append(f"rerun inputs not re-acquired under scratch: {srv.get('realpath')!r} {mdl.get('path')!r}")
                ev1, evr = evaluated(r1), evaluated(rr)
                nchecks = len(evr)
                for cid, passed in ev1.items():
                    if cid not in evr or evr[cid] != passed:
                        probs.append(f"check {cid}: receipt-1 {passed} rerun {evr.get(cid, 'not-evaluated')}")
            for p in probs:
                detail.append(f"replay: {p}")
            rep = not probs
        # tamper
        tam = False
        if have_tool and r1 is not None:
            tam = True
            for name, keys in (("model", ("provenance", "model", "sha256")),
                               ("asset", ("provenance", "server", "asset_sha256"))):
                rec = json.loads(json.dumps(r1))
                node = rec
                try:
                    for k in keys[:-1]:
                        node = node[k]
                    v = node[keys[-1]]
                    node[keys[-1]] = ("0" if v[0] != "0" else "1") + v[1:]
                except (KeyError, TypeError, IndexError):
                    detail.append(f"tamper-{name}: receipt-1 lacks {'.'.join(keys)}")
                    tam = False
                    continue
                tp = os.path.join(tree, f".ufo/waves/round-47/c2/live/tamper-{name}.json")
                with open(tp, "w") as fh:
                    json.dump(rec, fh)
                code, j, tail = run_replay(tree, tp, os.path.join(S, f"work-{name}"),
                                           os.path.join(S, f"tamper-{name}.json"), env)
                rr = load_json(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
                if code in (0, None) or (isinstance(rr, dict) and rr.get("outcome") == "pass"):
                    detail.append(f"tamper-{name}: exit {code}, rerun outcome "
                                  f"{rr.get('outcome') if isinstance(rr, dict) else None}: not refused")
                    tam = False
        # newrow
        src = at_tip(a.repo, tip, "corpus/SOURCES.md")
        newrow = bool(src) and any(
            ln.startswith("| S") and RELEASE in ln and COMMIT in ln
            for ln in src.decode("utf-8", "replace").split("\n"))
        if not newrow:
            detail.append(f"newrow: no registry row names {RELEASE} and {COMMIT}")
        met = bool(rok and rep and tam and newrow)
        lines = [f"receipts={int(rok)} replay={int(rep)} tamper={int(tam)} newrow={int(newrow)} "
                 f"rerun_checks={nchecks} met={met}", f"tip={tip} started={t0.isoformat()}"]
        lines += [f"detail: {d}" for d in detail]
        text = "\n".join(lines)
        print(text)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
        return 0 if met else 1
    finally:
        shutil.rmtree(S, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
