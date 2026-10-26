#!/usr/bin/env python3
"""round48-live-replay-v5-audit.py - kama round-48 C2 (operability, sourced) counter.

Question: at a lane revision, is the lane's live llama.cpp evidence re-runnable
by a fresh session in a form that cannot be met without really re-acquiring
and really re-running it, and is its provenance checked when it is recorded?
The round-47 outside closure routed (corpus/lessons/round-47-verifier-spotcheck.md):
  D1  the frozen round-47 counter trusted the rerun receipt's contents: a replay
      that copies host-cache bytes without downloading, a fabricated rerun of
      0-byte placeholders and a forged started_utc all met it (seat K2Cheat);
  D2  only receipt-1 was replayed; receipts 2 and 3 were trusted on structure;
  D3  the live tool accepted unverifiable provenance at record time (K2Design F1);
  D4  replay agreement was check pass/fail, not the captured surfaces (K2Checks);
  D6  the model URL named the moving `main` ref (X2Revision).

Frozen names (before data):
  release      llama.cpp b11909 = caa8191df159f764fb0160e3d2fc6be008948aee
  asset        https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
               sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b
  model        https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
               commit 499bc8821c6b12b4e53c5bffcb21ec206f212d81,
               sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
               (opened 2026-10-26: x-repo-commit and x-linked-etag of that URL;
               .ufo/waves/round-48/c2/hf-revision-499bc882.txt)
  swap asset   https://github.com/ggml-org/llama.cpp/releases/download/b11906/llama-b11906-bin-ubuntu-x64.tar.gz
               (a real archive whose bytes are not the b11909 digest)
  swap model   .../resolve/22027b1ab988d9d04ec83020f28c2db533985059/tinyllamas/stories260K.gguf
               (serves sha256 68c694e7..., not the recorded digest)
  receipts     .ufo/waves/round-48/c2/live/receipt-1.json, -2.json, -3.json
  replay       tools/kama-live-replay.py     live tool  tools/kama-llamacpp-live.py

v5 receipt contract (v4 plus):
  "schema": "kama-llamacpp-live/v5"
  provenance.model.commit: 40 lower-case hex; provenance.model.url contains
      `/resolve/<commit>/`
  provenance.verified: {"at": "record", "archive_sha256", "member_sha256",
      "model_sha256"} - the live tool hashed, before starting the server, the
      local copy of the release archive (--server-archive), the archive member
      named by provenance.server.member, and the model; they equal
      provenance.server.asset_sha256, server.sha256 and model.sha256.
Live tool record-time contract: given any provenance flag, the live tool
requires all of --server-asset-url, --server-asset-sha256, --server-member,
--model-url and --server-archive; https:// URLs; a model URL pinned to a
40-hex `/resolve/<commit>/`; a member path with no leading `/` and no `..`;
sha256(--server-archive) == --server-asset-sha256; the member's bytes in that
archive hash to sha256(--server); otherwise it exits 2 without starting the
server.
Replay contract: `kama-live-replay.py --receipt R --work DIR --out J` (as round
47; for a v5 receipt it passes the downloaded archive as --server-archive and
expects a v5 rerun) writes J with "match", "refused", "rerun_receipt" and
"inputs" {"archive", "model", "server"}; it fails a rerun whose stable
projection (props fields, slots count and body digest, health status and body
digest, models ids and owned_by, metrics status, loading envelope, teardown
outcome, listener ownership) differs. `kama-live-replay.py --compare A B`
compares two receipts with the same rules (no network) and exits 0 when they
agree, 1 when they differ.

Legs:
  receipts     each of the three receipts at --tip: schema v5, outcome pass, >= 10
               evaluated checks all passed; provenance.server equal to the frozen
               asset and digest with a non-empty member; provenance.model.url,
               .commit and .sha256 equal to the frozen model; model.sha256 equal
               to it; provenance.verified at=record with archive_sha256 = frozen
               asset digest, member_sha256 = server.sha256, model_sha256 = frozen
               model digest; build_info starts with `b11909-`; teardown.log_path
               null or a committed repo-relative path.
  recordcheck  the live tool at --tip (from `git archive`), driven with a stub
               server that writes a marker file when executed, a stub model and
               a stub archive: refuses (exit 2, no marker, no pass receipt) an
               unpinned `resolve/main` model URL, an archive whose digest is not
               the recorded one, an http:// asset URL, a partial provenance flag
               set, and an archive whose member is not the server binary; and, as
               the positive control, with all five flags right it executes the
               stub (marker written).
  replay       for EACH receipt, the replay tool at --tip from `git archive`, with
               HOME, XDG_CACHE_HOME and TMPDIR inside --scratch, exits 0 with
               match true; this counter then hashes the files itself: the rerun's
               server.realpath and model.path and J.inputs.archive lie inside
               --scratch and hash to the receipt's server.sha256, the frozen model
               digest and the frozen asset digest; the rerun is schema v5, outcome
               pass, started_utc not earlier than this counter's start, with the
               frozen model commit; every check the receipt evaluated is evaluated
               with the same passed value; and this counter's own stable
               projection of the rerun equals the receipt's.
  compare      `--compare` on receipt-1 and copies of it: a copy with only
               instance fields changed (port, child_pid, started/ended utc,
               term_wait_ms, log_lines, the models body's `created`) exits 0; each
               of five copies with one stable surface changed (props n_ctx, slots
               count, health body, models id, teardown sigkill_sent) exits 1.
  tamper       copies of receipt-1 with provenance.model.sha256 or
               provenance.server.asset_sha256 changed in the first hex digit:
               exit != 0 and no pass rerun.
  urlswap      a copy of receipt-1 whose asset URL is the swap asset (recorded
               digest unchanged), and one whose model URL and commit name the swap
               revision: each exits 2 with a `digest-mismatch` refusal and no
               rerun receipt (a replay that does not download what the receipt
               names cannot refuse these).
  newrow       corpus/SOURCES.md at --tip has a registry row (`| S...`) containing
               the pinned model URL in full (S039 names the commit, S490 the `main`
               resolve URL; neither names this URL).
met = all seven legs.
PREDICATE (same sentence in the preregistration): three committed v5 b11909
live receipts carry record-time-verified provenance with the model pinned to
an HF revision, the live tool refuses unverifiable provenance before starting
a server, every receipt replays from committed bytes with re-acquired inputs
the counter hashes itself and an equal stable projection, the replay's
comparison separates instance from stable fields, wrong digests and swapped
URLs are refused, and the pinned revision is a source row; receipts=1
recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1.

Output: `receipts=0|1 recordcheck=0|1 replay=0|1 compare=0|1 tamper=0|1
urlswap=0|1 newrow=0|1 replayed=N/3 met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate (git failure).
Read-only on --repo; everything else lives under --scratch and is removed on exit.
Needs network access to github.com and huggingface.co.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
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
ASSET_URL = "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz"
ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"
MODEL_COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             f"{MODEL_COMMIT}/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
SWAP_ASSET = "https://github.com/ggml-org/llama.cpp/releases/download/b11906/llama-b11906-bin-ubuntu-x64.tar.gz"
SWAP_COMMIT = "22027b1ab988d9d04ec83020f28c2db533985059"
SWAP_MODEL = f"https://huggingface.co/ggml-org/models-moved/resolve/{SWAP_COMMIT}/tinyllamas/stories260K.gguf"
RECEIPTS = [f".ufo/waves/round-48/c2/live/receipt-{n}.json" for n in (1, 2, 3)]
REPLAY = "tools/kama-live-replay.py"
LIVE = "tools/kama-llamacpp-live.py"
SCHEMA = "kama-llamacpp-live/v5"
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


def sha_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except (OSError, TypeError):
        return None
    return h.hexdigest()


def inside(path, root):
    try:
        rp, rr = os.path.realpath(str(path)), os.path.realpath(root)
    except (TypeError, ValueError):
        return False
    return rp.startswith(rr + os.sep)


def parse_time(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def evaluated(rec):
    return {c.get("id"): c.get("passed") for c in rec.get("checks") or []
            if isinstance(c, dict) and c.get("evaluated")}


def dig(rec, *keys):
    node = rec
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def projection(rec):
    """This counter's own stable projection of a live receipt."""
    cap = rec.get("captures") if isinstance(rec.get("captures"), dict) else {}
    models = None
    try:
        doc = json.loads(dig(cap, "models", "body") or "null")
        if isinstance(doc, dict):
            models = (sorted(str(m.get("id")) + "|" + str(m.get("owned_by")) for m in doc.get("data") or []
                             if isinstance(m, dict)),
                      sorted(str(m.get("name")) for m in doc.get("models") or [] if isinstance(m, dict)))
    except ValueError:
        models = "unparseable"
    td = rec.get("teardown") if isinstance(rec.get("teardown"), dict) else {}
    return {"props": dig(cap, "props", "fields"),
            "slots": (dig(cap, "slots", "element_count"), dig(cap, "slots", "body_sha256")),
            "health": (dig(cap, "health", "status"), dig(cap, "health", "body_sha256")),
            "models": models,
            "metrics": None,
            "loading": (rec.get("loading_envelope_exact"), dig(rec, "loading_503", "body_sha256")),
            "teardown": tuple(td.get(k) for k in ("returncode", "sigterm_sent", "sigkill_sent", "port_refuses")),
            "ownership": rec.get("port_listener_ownership")}


def check_receipt(repo, tip, path, rec, detail):
    probs = []
    if rec.get("schema") != SCHEMA or rec.get("outcome") != "pass":
        probs.append(f"schema/outcome {rec.get('schema')!r}/{rec.get('outcome')!r}")
    ev = evaluated(rec)
    if len(ev) < 10 or not all(v is True for v in ev.values()):
        probs.append(f"evaluated={len(ev)} all_passed={all(v is True for v in ev.values())}")
    srv, mdl, ver = dig(rec, "provenance", "server") or {}, dig(rec, "provenance", "model") or {}, \
        dig(rec, "provenance", "verified") or {}
    if srv.get("asset_url") != ASSET_URL or srv.get("asset_sha256") != ASSET_SHA:
        probs.append("provenance.server is not the frozen asset")
    if not isinstance(srv.get("member"), str) or not srv.get("member"):
        probs.append("provenance.server.member missing")
    if mdl.get("url") != MODEL_URL or mdl.get("commit") != MODEL_COMMIT or mdl.get("sha256") != MODEL_SHA:
        probs.append(f"provenance.model {mdl!r} is not the frozen pinned model")
    if dig(rec, "model", "sha256") != MODEL_SHA:
        probs.append("model.sha256 is not the frozen model digest")
    if not (ver.get("at") == "record" and ver.get("archive_sha256") == ASSET_SHA
            and ver.get("model_sha256") == MODEL_SHA and isinstance(dig(rec, "server", "sha256"), str)
            and ver.get("member_sha256") == dig(rec, "server", "sha256")):
        probs.append(f"provenance.verified {ver!r} does not bind archive, member and model")
    if not str(dig(rec, "captures", "props", "fields", "build_info") or "").startswith(RELEASE + "-"):
        probs.append("build_info is not b11909")
    td = rec.get("teardown") if isinstance(rec.get("teardown"), dict) else {}
    lp = td.get("log_path", "absent-key")
    if lp == "absent-key":
        probs.append("teardown.log_path key missing")
    elif lp is not None and (not isinstance(lp, str) or os.path.isabs(lp) or ".." in lp.split("/")
                             or git(repo, "cat-file", "-e", f"{tip}:{lp}", check=False).returncode != 0):
        probs.append(f"teardown.log_path {lp!r} is not committed")
    for p in probs:
        detail.append(f"receipts: {path}: {p}")
    return not probs


def run(argv, env, cwd, timeout=1500):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    return p.returncode, (p.stdout[-300:] + " | " + p.stderr[-300:]).replace("\n", " ")


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def replay(tree, rpath, S, tag, env):
    outj = os.path.join(S, f"{tag}.json")
    code, tail = run([sys.executable, os.path.join(tree, REPLAY), "--receipt", rpath,
                      "--work", os.path.join(S, f"work-{tag}"), "--out", outj], env, tree)
    j = load(outj)
    rr = load(j.get("rerun_receipt")) if isinstance(j, dict) and j.get("rerun_receipt") else None
    return code, j, rr, tail


def recordcheck(tree, S, env, detail):
    d = os.path.join(S, "rc")
    os.makedirs(os.path.join(d, "pkg", "rel"))
    marker = os.path.join(d, "EXECUTED")
    srv = os.path.join(d, "pkg", "rel", "llama-server")
    with open(srv, "w") as fh:
        fh.write(f"#!/bin/sh\necho executed > '{marker}'\nexit 3\n")
    os.chmod(srv, 0o755)
    other = os.path.join(d, "other")
    with open(other, "w") as fh:
        fh.write("#!/bin/sh\nexit 0\n")
    good = os.path.join(d, "good.tar.gz")
    with tarfile.open(good, "w:gz") as tf:
        tf.add(srv, arcname="rel/llama-server")
    wrongmember = os.path.join(d, "wrongmember.tar.gz")
    with tarfile.open(wrongmember, "w:gz") as tf:
        tf.add(other, arcname="rel/llama-server")
    model = os.path.join(d, "m.gguf")
    with open(model, "wb") as fh:
        fh.write(b"GGUF-stub-model-r48")
    msha, gsha = sha_file(model), sha_file(good)
    pinned = f"https://huggingface.co/x/y/resolve/{'a' * 40}/m.gguf"
    full = {"--server-asset-url": "https://example.invalid/rel.tar.gz", "--server-asset-sha256": gsha,
            "--server-member": "rel/llama-server", "--model-url": pinned, "--server-archive": good}
    cases = [
        ("unpinned-model-url", dict(full, **{"--model-url": "https://huggingface.co/x/y/resolve/main/m.gguf"}), 2),
        ("archive-digest-wrong", dict(full, **{"--server-asset-sha256": "0" * 64}), 2),
        ("http-asset-url", dict(full, **{"--server-asset-url": "http://example.invalid/rel.tar.gz"}), 2),
        ("partial-flags", {"--model-url": pinned}, 2),
        ("member-not-server", dict(full, **{"--server-archive": wrongmember,
                                             "--server-asset-sha256": sha_file(wrongmember)}), 2),
        ("all-right-control", full, None),
    ]
    ok = True
    for name, flags, want in cases:
        if os.path.exists(marker):
            os.unlink(marker)
        outr = os.path.join(d, f"{name}.json")
        argv = [sys.executable, os.path.join(tree, LIVE), "--server", srv, "--model", model, "--model-sha256", msha,
                "--ready-timeout", "5", "--out", outr]
        for k, v in flags.items():
            argv += [k, v]
        code, tail = run(argv, env, tree, timeout=300)
        rec = load(outr)
        executed = os.path.exists(marker)
        if want is None:
            good_case = executed
        else:
            good_case = code == want and not executed and not (isinstance(rec, dict) and rec.get("outcome") == "pass")
        if not good_case:
            ok = False
            detail.append(f"recordcheck {name}: exit {code} executed={executed} "
                          f"outcome={rec.get('outcome') if isinstance(rec, dict) else None} {tail[:200]}")
    return ok


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
    S = tempfile.mkdtemp(prefix="r48c2-", dir=root)
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
            tf.extractall(tree, filter=lambda m, dest: None if (m.issym() or m.islnk())
                          else tarfile.data_filter(m, dest))
        env = dict(os.environ)
        for k, sub in (("HOME", "home"), ("XDG_CACHE_HOME", "home/.cache"), ("TMPDIR", "tmp")):
            dd = os.path.join(S, sub)
            os.makedirs(dd, exist_ok=True)
            env[k] = dd
        have_replay = os.path.isfile(os.path.join(tree, REPLAY))
        have_live = os.path.isfile(os.path.join(tree, LIVE))
        # receipts
        recs, rok = {}, True
        for path in RECEIPTS:
            raw = at_tip(a.repo, tip, path)
            try:
                rec = json.loads(raw) if raw is not None else None
            except ValueError:
                rec = None
            if not isinstance(rec, dict):
                detail.append(f"receipts: {path} absent or not a JSON object at tip")
                rok = False
                continue
            recs[path] = rec
            rok = check_receipt(a.repo, tip, path, rec, detail) and rok
        # recordcheck
        rcl = False
        if have_live:
            rcl = recordcheck(tree, S, env, detail)
        else:
            detail.append(f"recordcheck: {LIVE} absent at tip")
        # replay
        replayed = 0
        for n, path in enumerate(RECEIPTS, 1):
            rec = recs.get(path)
            if rec is None or not have_replay:
                continue
            code, j, rr, tail = replay(tree, os.path.join(tree, path), S, f"replay-{n}", env)
            probs = []
            if code != 0 or not isinstance(j, dict) or j.get("match") is not True or j.get("refused") is not None:
                probs.append(f"exit {code} match {j.get('match') if isinstance(j, dict) else None}: {tail[:240]}")
            if not isinstance(rr, dict):
                probs.append("rerun receipt missing")
            else:
                if rr.get("schema") != SCHEMA or rr.get("outcome") != "pass":
                    probs.append(f"rerun schema/outcome {rr.get('schema')!r}/{rr.get('outcome')!r}")
                st = parse_time(rr.get("started_utc"))
                if st is None or st < t0:
                    probs.append(f"rerun started_utc {rr.get('started_utc')!r} precedes counter start")
                if dig(rr, "provenance", "model", "commit") != MODEL_COMMIT:
                    probs.append("rerun model commit is not the frozen commit")
                sp, mp = dig(rr, "server", "realpath"), dig(rr, "model", "path")
                ap_ = dig(j, "inputs", "archive") if isinstance(j, dict) else None
                for label, fpath, want in (("server", sp, dig(rec, "server", "sha256")), ("model", mp, MODEL_SHA),
                                           ("archive", ap_, ASSET_SHA)):
                    if not inside(fpath, S):
                        probs.append(f"{label} file {fpath!r} not under scratch")
                    elif sha_file(fpath) != want:
                        probs.append(f"{label} file {fpath!r} does not hash to {str(want)[:12]}")
                e0, e1 = evaluated(rec), evaluated(rr)
                for cid, passed in e0.items():
                    if e1.get(cid, "not-evaluated") != passed:
                        probs.append(f"check {cid}: {passed} -> {e1.get(cid, 'not-evaluated')}")
                p0, p1 = projection(rec), projection(rr)
                for k in p0:
                    if p0[k] != p1[k]:
                        probs.append(f"projection {k}: {str(p0[k])[:80]} -> {str(p1[k])[:80]}")
            for p in probs:
                detail.append(f"replay {n}: {p}")
            replayed += int(not probs)
        rep = replayed == 3
        r1 = recs.get(RECEIPTS[0])
        work = os.path.join(S, "variants")
        os.makedirs(work, exist_ok=True)

        def variant(name, mutate):
            v = copy.deepcopy(r1)
            mutate(v)
            p = os.path.join(work, f"{name}.json")
            with open(p, "w") as fh:
                json.dump(v, fh)
            return p

        # compare
        cmpok = False
        if have_replay and r1 is not None:
            cmpok = True

            def inst(v):
                v["port"] = (v.get("port") or 0) + 1
                v["child_pid"] = (v.get("child_pid") or 0) + 7
                v["started_utc"], v["ended_utc"] = "2030-01-01T00:00:00Z", "2030-01-01T00:00:09Z"
                td = v.setdefault("teardown", {})
                td["term_wait_ms"] = (td.get("term_wait_ms") or 0) + 11
                td["log_lines"] = ["changed"]
                mb = dig(v, "captures", "models")
                if isinstance(mb, dict) and isinstance(mb.get("body"), str):
                    mb["body"] = re.sub(r'"created":\d+', '"created":1', mb["body"])
                    mb["body_sha256"] = hashlib.sha256(mb["body"].encode()).hexdigest()

            def setp(*keys, val):
                def f(v):
                    node = v
                    for k in keys[:-1]:
                        node = node.setdefault(k, {})
                    node[keys[-1]] = val(node.get(keys[-1])) if callable(val) else val
                return f

            def models_id(v):
                mb = dig(v, "captures", "models")
                mb["body"] = mb["body"].replace('"id":"', '"id":"x', 1)
                mb["body_sha256"] = hashlib.sha256(mb["body"].encode()).hexdigest()

            cases = [("instance-only", inst, 0),
                     ("props-n_ctx", setp("captures", "props", "fields", "default_generation_settings.n_ctx",
                                          val=lambda x: (x or 0) * 2 + 1), 1),
                     ("slots-count", setp("captures", "slots", "element_count", val=lambda x: (x or 0) + 1), 1),
                     ("health-body", setp("captures", "health", "body_sha256",
                                          val=hashlib.sha256(b'{"status":"degraded"}').hexdigest()), 1),
                     ("models-id", models_id, 1),
                     ("teardown-sigkill", setp("teardown", "sigkill_sent", val=lambda x: not x), 1)]
            for name, mut, want in cases:
                try:
                    vp = variant(f"cmp-{name}", mut)
                except (KeyError, TypeError, AttributeError) as exc:
                    detail.append(f"compare {name}: could not build variant: {exc}")
                    cmpok = False
                    continue
                code, tail = run([sys.executable, os.path.join(tree, REPLAY), "--compare",
                                  os.path.join(tree, RECEIPTS[0]), vp], env, tree, timeout=120)
                if code != want:
                    detail.append(f"compare {name}: exit {code} want {want}: {tail[:200]}")
                    cmpok = False
        # tamper
        tam = False
        if have_replay and r1 is not None:
            tam = True
            for name, keys in (("model", ("provenance", "model", "sha256")),
                               ("asset", ("provenance", "server", "asset_sha256"))):
                def flip(v, keys=keys):
                    node = v
                    for k in keys[:-1]:
                        node = node[k]
                    s = node[keys[-1]]
                    node[keys[-1]] = ("0" if s[0] != "0" else "1") + s[1:]
                try:
                    vp = variant(f"tamper-{name}", flip)
                except (KeyError, TypeError, IndexError):
                    detail.append(f"tamper-{name}: receipt-1 lacks {'.'.join(keys)}")
                    tam = False
                    continue
                code, j, rr, tail = replay(tree, vp, S, f"tamper-{name}", env)
                if code in (0, None) or (isinstance(rr, dict) and rr.get("outcome") == "pass"):
                    detail.append(f"tamper-{name}: exit {code}: not refused")
                    tam = False
        # urlswap
        swp = False
        if have_replay and r1 is not None:
            swp = True

            def swap_asset(v):
                v["provenance"]["server"]["asset_url"] = SWAP_ASSET

            def swap_model(v):
                v["provenance"]["model"]["url"] = SWAP_MODEL
                v["provenance"]["model"]["commit"] = SWAP_COMMIT

            for name, mut in (("asset", swap_asset), ("model", swap_model)):
                try:
                    vp = variant(f"swap-{name}", mut)
                except (KeyError, TypeError):
                    detail.append(f"urlswap-{name}: receipt-1 lacks provenance")
                    swp = False
                    continue
                code, j, rr, tail = replay(tree, vp, S, f"swap-{name}", env)
                ref = (j or {}).get("refused") if isinstance(j, dict) else None
                if code != 2 or not str(ref or "").startswith("digest-mismatch") or rr is not None:
                    detail.append(f"urlswap-{name}: exit {code} refused {ref!r} rerun {rr is not None}")
                    swp = False
        # newrow
        src = at_tip(a.repo, tip, "corpus/SOURCES.md")
        newrow = bool(src) and any(ln.lstrip(" ").startswith("| S") and MODEL_URL in ln
                                   for ln in src.decode("utf-8", "replace").split("\n"))
        if not newrow:
            detail.append(f"newrow: no registry row contains {MODEL_URL}")
        met = bool(rok and rcl and rep and cmpok and tam and swp and newrow)
        lines = [f"receipts={int(rok)} recordcheck={int(rcl)} replay={int(rep)} compare={int(cmpok)} "
                 f"tamper={int(tam)} urlswap={int(swp)} newrow={int(newrow)} replayed={replayed}/3 met={met}",
                 f"tip={tip} started={t0.isoformat()}"]
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
