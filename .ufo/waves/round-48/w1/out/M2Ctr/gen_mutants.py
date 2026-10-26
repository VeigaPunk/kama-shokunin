#!/usr/bin/env python3
"""M2Ctr mutant generator (round-48 C2 counter mutation test).

Reads the PRISTINE lane counter (read-only), applies single-site substring
edits to a scratch copy per mutant, asserts each edit matches exactly once,
py_compiles every mutant, and writes a manifest with before/after sha256 and
preregistered predictions. The lane file itself is never modified.
"""
import hashlib
import json
import os
import py_compile

PRISTINE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-live-replay-v5-audit.py"
S = "/fast/scratch/hyaku/kama-r48/M2Ctr"
MUTDIR = os.path.join(S, "mutants")

# (id, region, [(old, new)...], prediction, reason)
MUTANTS = [
    ("M01-schema-v4", "SCHEMA",
     [('SCHEMA = "kama-llamacpp-live/v5"', 'SCHEMA = "kama-llamacpp-live/v4"')],
     "KILLED-TIP", "tip receipts are v5; receipts leg compares rec.schema != SCHEMA"),
    ("M02-asset-sha", "frozen-digests",
     [('ASSET_SHA = "bf94332a', 'ASSET_SHA = "cf94332a')],
     "KILLED-TIP", "receipt provenance.server.asset_sha256 is the real digest; frozen-constant compare fails"),
    ("M03-model-commit", "frozen-digests",
     [('MODEL_COMMIT = "499bc8821', 'MODEL_COMMIT = "599bc8821')],
     "KILLED-TIP", "receipt provenance.model.commit is the real pin; compare fails (also shifts MODEL_URL)"),
    ("M04-model-url-path", "frozen-urls",
     [('f"{MODEL_COMMIT}/tinyllamas/stories260K.gguf")', 'f"{MODEL_COMMIT}/tinyllama/stories260K.gguf")')],
     "KILLED-TIP", "receipt model.url names tinyllamas; MODEL_URL compare fails"),
    ("M05-model-sha", "frozen-digests",
     [('MODEL_SHA = "270cba1bd', 'MODEL_SHA = "370cba1bd')],
     "KILLED-TIP", "receipt model digests are the real ones; frozen-constant compare fails"),
    ("M06-eval-threshold-3", "receipts-leg",
     [('if len(ev) < 10 or not all(v is True for v in ev.values()):',
       'if len(ev) < 3 or not all(v is True for v in ev.values()):')],
     "SURVIVED", "tip receipts have >=10 evaluated checks either way; control receipts leg already passes"),
    ("M07-all-passed-false", "receipts-leg",
     [('not all(v is True for v in ev.values())', 'not all(v is False for v in ev.values())')],
     "KILLED-TIP", "tip receipts have all checks passed=True; all-False is False so a prob is appended"),
    ("M08-verified-at-rerun", "verified-block",
     [('ver.get("at") == "record"', 'ver.get("at") == "rerun"')],
     "KILLED-TIP", "receipts carry verified.at=record; compare fails"),
    ("M09-member-binding-asset", "verified-block",
     [('and ver.get("member_sha256") == dig(rec, "server", "sha256")):',
       'and ver.get("member_sha256") == ASSET_SHA):')],
     "KILLED-TIP", "member_sha256 binds to server.sha256 (member digest), not the archive digest"),
    ("M10-marker-always", "recordcheck",
     [('executed = os.path.exists(marker)', 'executed = True')],
     "KILLED-TIP", "negative recordcheck cases require not executed; marker-True fails them all"),
    ("M11-rc-ignore-executed", "recordcheck",
     [('code == want and not executed and not (isinstance(rec, dict) and rec.get("outcome") == "pass")',
       'code == want and not (isinstance(rec, dict) and rec.get("outcome") == "pass")')],
     "SURVIVED", "no target ships a live tool that executes the stub server on a refused case"),
    ("M12-rc-want-3", "recordcheck",
     [('resolve/main/m.gguf"}), 2),', 'resolve/main/m.gguf"}), 3),')],
     "KILLED-TIP", "live tool refuses unpinned URL with exit 2, not 3"),
    ("M13-inside-true", "inside",
     [('return rp.startswith(rr + os.sep)', 'return True')],
     "EXERCISED-CTL", "control detail loses the 9 'not under scratch' lines; leg stays 0 via started_utc"),
    ("M14-replay-no-hash", "replay-cross-hash",
     [('elif sha_file(fpath) != want:', 'elif False:')],
     "SURVIVED", "tip rerun files hash correctly anyway; control hash branch unreached (inside() gate first)"),
    ("M15-started-utc-drop", "started-utc",
     [('if st is None or st < t0:', 'if st is None:')],
     "EXERCISED-CTL", "control detail loses the 3 'precedes counter start' lines; leg stays 0 via scratch paths"),
    ("M16-compound-mno", "replay-leg",
     [('return rp.startswith(rr + os.sep)', 'return True'),
      ('elif sha_file(fpath) != want:', 'elif False:'),
      ('if st is None or st < t0:', 'if st is None:')],
     "KILLED-CTL", "with all three guards off the copied-receipt cheat passes the replay leg on the control"),
    ("M17-projection-metrics", "projection-keys",
     [('"metrics": dig(cap, "metrics", "status"),', '"metrics": None,')],
     "SURVIVED", "projection() is applied to both sides of the rec-vs-rr compare, so it is self-consistent"),
    ("M18-cmp-instance-want1", "compare",
     [('("instance-only", inst, 0),', '("instance-only", inst, 1),')],
     "KILLED-TIP", "instance-only copy must compare equal (exit 0); demanding 1 fails the leg"),
    ("M19-cmp-props-want0", "compare",
     [('(x or 0) * 2 + 1), 1),', '(x or 0) * 2 + 1), 0),')],
     "KILLED-TIP", "props n_ctx change must exit 1; demanding 0 fails the leg"),
    ("M20-tamper-noop", "tamper",
     [('node[keys[-1]] = ("0" if s[0] != "0" else "1") + s[1:]', 'pass')],
     "KILLED-TIP", "unflipped variant replays cleanly with exit 0 and a pass rerun; tamper leg sees code 0"),
    ("M21-tamper-accept-all", "tamper",
     [('if code in (0, None) or (isinstance(rr, dict) and rr.get("outcome") == "pass"):', 'if False:')],
     "KILLED-CTL", "control tamper refusals disappear; tamper flag flips 0->1 on the control"),
    ("M22-urlswap-prefix-loose", "urlswap",
     [('startswith("digest-mismatch")', 'startswith("digest")')],
     "SURVIVED", "tip refusal prefix still matches the looser prefix; control urlswap already 0"),
    ("M23-urlswap-rerun-ok", "urlswap",
     [('startswith("digest-mismatch") or rr is not None', 'startswith("digest-mismatch")')],
     "SURVIVED", "tip refusals produce no rerun either way; control urlswap already 0"),
    ("M24-urlswap-code0", "urlswap",
     [('if code != 2 or not str(ref or "")', 'if code != 0 or not str(ref or "")')],
     "KILLED-TIP", "tip urlswap refusals exit 2, not 0; demanding 0 fails the leg"),
    ("M25-newrow-noshape", "newrow",
     [('any(ln.lstrip(" ").startswith("| S") and MODEL_URL in ln', 'any(MODEL_URL in ln')],
     "SURVIVED", "tip has a real '| S' row so the shape test is redundant there; control lacks the URL entirely"),
    ("M26-newrow-src-only", "newrow",
     [('newrow = bool(src) and any(', 'newrow = bool(src) or any(')],
     "KILLED-CTL", "SOURCES.md exists at the control base, so newrow flips 0->1 without the row-content check"),
    ("M27-replayed-2", "replay-aggregation",
     [('rep = replayed == 3', 'rep = replayed == 2')],
     "KILLED-TIP", "tip replays 3/3; ==2 makes rep False and the tip run exits 1"),
]

src = open(PRISTINE).read()
pristine_sha = hashlib.sha256(src.encode()).hexdigest()
manifest = []
for mid, region, pairs, pred, reason in MUTANTS:
    text = src
    lines = []
    for old, new in pairs:
        n = text.count(old)
        assert n == 1, f"{mid}: anchor matches {n} times: {old[:60]!r}"
        idx = text.index(old)
        lines.append(text[:idx].count("\n") + 1)
        text = text.replace(old, new, 1)
    assert text != src, mid
    mpath = os.path.join(MUTDIR, f"{mid}.py")
    with open(mpath, "w") as fh:
        fh.write(text)
    py_compile.compile(mpath, doraise=True)
    msha = hashlib.sha256(text.encode()).hexdigest()
    manifest.append({"id": mid, "region": region, "lines": lines, "prediction": pred,
                     "reason": reason, "sha256": msha,
                     "edits": [{"old": o[:80], "new": nw[:80]} for o, nw in pairs]})
with open(os.path.join(S, "mutants.json"), "w") as fh:
    json.dump({"pristine_sha256": pristine_sha, "pristine_path": PRISTINE, "mutants": manifest}, fh, indent=1)
print(f"pristine {pristine_sha[:16]} generated {len(manifest)} mutants, all py_compile OK")
for m in manifest:
    print(f'{m["id"]:26s} L{m["lines"]} pred={m["prediction"]:13s} {m["sha256"][:12]}')
