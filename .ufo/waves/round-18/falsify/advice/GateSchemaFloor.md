VERDICT: confirm — under `--require-schema v3` the current gate rejects every older self-declaration (v1 and v2) and every unknown schema with INVALID exit 1; the only live escape is the flagless default, reported below as the permissive boundary.

# GateSchemaFloor — schema-floor boundary falsification (round 18, wave 2)

Seat: KamaR18.GateSchemaFloor (leaf, isolated clone, 2026-10-20).
Target: gate `tests/llamacpp-live/check-receipt.py` at lane master
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, sha256
`c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`.
Producer `tools/kama-llamacpp-live.py` (same commit). Clone:
`/tmp/kama-r18-falsify-GateSchemaFloor` (branch `seat/GateSchemaFloor`),
`git log --oneline c6dc46f..1c325b2 -- tests/llamacpp-live/check-receipt.py
tools/kama-llamacpp-live.py` printed nothing, so the tested gate bytes are the
measured-revision bytes. Runtime: `/usr/bin/python3` = Python 3.14.8.
No tools installed (none needed). No servers, no sockets, no ports opened;
every gate call was a short-lived subprocess (30/30 exited, none linger;
`pgrep -af "scratch/experiment|check-receipt"` after the run: empty).

## Attack, as assigned

Declare v1/v2 under `--require-schema v3`; test each floor (v1, v2, v3) and
unknown schemas; show the current v3 gate cannot escape by merely
self-declaring an older schema when the caller requires v3; report the default
permissive boundary honestly.

Fixtures, all inside the clone, all pin-clean (pins taken from each receipt's
own recorded `model/server/probe/tool` sha256 so any rejection is attributable
to the schema/floor predicate, never to a pin):

- `v3.json` — byte copy of committed `.ufo/waves/round-18/live/receipt-1.json`
  (genuine v3, `outcome: "pass"`).
- `v3_as_v1.json`, `v3_as_v2.json` — same object, `schema` re-declared
  `kama-llamacpp-live/v1` / `v2` (the forgery surface; the producer cannot be
  asked to emit these: `SCHEMA = 'kama-llamacpp-live/v3'` at
  `tools/kama-llamacpp-live.py:49`, and no argparse flag overrides it).
- `v1.json` / `v2.json` — committed round-16 `receipt.json` (v1) and round-17
  `receipt-1.json` (v2), the genuine legacy receipts.
- Unknown-schema variants of `v3.json`: `kama-llamacpp-live/v4`,
  `kama-llamacpp-live/V3` (case), `""`, and the key deleted.
- `v2_as_v3.json` — round-17 receipt up-labeled v3.
- `ne.json` — the gate selftest's own not-evaluated derivation
  (`_selftest_receipt_v3()` with the exact `no_loading` transform from
  `check-receipt.py:1855-1871`), plus v1/v2 relabels of it.

## Results (30/30 as predicted, 0 unexpected; full raw log in the appendix)

Floor matrix on genuine receipts (no-harm + minimum semantics):

| case | argv | exit | first problem line |
|---|---|---|---|
| G1 | v3 + floor v3 | 0 | `VALID` |
| F1 | v1 + floor v3 | 1 | `schema 'kama-llamacpp-live/v1' is below --require-schema v3` |
| F2 | v1 + floor v2 | 1 | `... is below --require-schema v2` |
| F3 | v1 + floor v1 | 0 | `VALID` |
| F4 | v1 flagless | 0 | `VALID` (round-16 verdict preserved) |
| F5 | v2 + floor v3 | 1 | `schema 'kama-llamacpp-live/v2' is below --require-schema v3` |
| F6 | v2 + floor v2 | 0 | `VALID` |
| F7 | v2 flagless | 0 | `VALID` (round-17 verdict preserved) |
| F8 | v3 + floor v2 | 0 | `VALID` (minimum, not exact) |
| F9 | v3 + floor v1 | 0 | `VALID` |
| F10 | v3 flagless | 0 | `VALID` |

Headline — v3-evidence receipts self-declaring older schemas, caller requires
v3:

| case | declared | argv | exit | problems |
|---|---|---|---|---|
| A1 | v1 | floor v3 | 1 | 4: `required check 'teardown_exited' is absent`, 2× `unexpected check id ...`, **plus** `schema 'kama-llamacpp-live/v1' is below --require-schema v3` |
| A2 | v2 | floor v3 | 1 | exactly 1: `schema 'kama-llamacpp-live/v2' is below --require-schema v3` |
| A5 | v1 | flagless | 1 | 3 id-set problems only (floor inactive) |
| A6 | v1 | floor v1 | 1 | same 3 id-set problems (declared 1 ≥ minimum 1) |

A2 is the sharpest confirmation: for the v2 relabel the floor is the **sole**
detector — A3 shows the same bytes validate flagless — and it fires with one
attributable problem naming the required value. The floor predicate is
`check-receipt.py:2091-2104` (`version is not None and version < minimum`),
message at `:2097-2100`; argparse `choices=("v1","v2","v3")` at `:2063-2064`.

Unknown / missing schema (U1–U5): `v4`, `V3`, `""`, missing key → INVALID
exit 1 flagless and under every floor; e.g. `schema is
'kama-llamacpp-live/v4', want 'kama-llamacpp-live/v1', ...` (`:271-274`).
Attribution nuance, not an escape: the floor predicate itself **skips**
unknown schemas (`version is None` guard at `:2096`), so under
`--require-schema v3` a `v4` receipt is rejected by the schema-set check, and
the problem list contains no floor line. Outcome (exit 1) is identical; only
the naming differs. `--require-schema v4|v10|V3` → argparse usage error,
exit 2, stderr `unrecognized choice` (E1–E3) — distinguishable from INVALID=1.

Up-relabel (P1): genuine v2 receipt relabeled v3, flagless → exit 1 with 17
problems (`model.arg None missing...`, per-check `evaluated is not a
boolean`, ...). Declaring newer than the evidence is caught by the v3
re-derivation demands without any floor.

Not-evaluated precedence (N1–N5): genuine not-evaluated v3 + floor v3 → exit
3 `NOT-EVALUATED` (N1); the same bytes relabeled v1/v2 under floor v3 → exit
1 with the floor problem, never exit 3 (N2/N3 — a relabel cannot launder
NOT-EVALUATED through the floor path; `problems` are checked before the exit-3
branch at `:2101-2110`). Not-evaluated relabeled v2 is also caught **flagless**
by the v2 boolean demand (`check 'loading_envelope_graded': passed is not a
boolean`, N4/N5), which is exactly the down-direction coverage
CritC1HiddenPass asked for at the v2 floor.

## Default permissive boundary (honest statement)

1. **Flagless, the gate accepts any known schema** (`if args.require_schema
   and ...` at `:2091` — the floor is opt-in). Concretely, `v3_as_v2.json`
   flagless is **VALID exit 0** (A3): v3-produced evidence graded by the
   weaker v2 rules. Everything v3-only is then silently not applied:
   `validate_source_binding` runs only `if is_v3` (`:857-859`), the tri-state
   `passed`/`evaluated`/`outcome` consistency only in the `is_v3` branch of
   the checks loop (`:797-818`), and the `require_observed` exact-envelope
   re-derivations only on the v3 path. A caller that wants v3 semantics must
   pass `--require-schema v3`; nothing in the gate forces it.
2. **The defense sits exactly at the requested value, not below it
   generally**: v3-as-v2 under `--require-schema v2` is VALID exit 0 (A4,
   declared == minimum). Only the v3 floor defends the v3→v2 relabel.
3. **The v1 direction has a second, flag-independent detector; the v2
   direction does not.** A raw v3→v1 relabel is rejected even flagless by the
   check-id-set lock (v1 names exactly 10 checks incl. `teardown_exited`;
   `REQUIRED_CHECKS_V1/V2` at `:55-79`, set closure at `:825-832`). v2 and v3
   share the same 11-check id set, so v3→v2 is invisible without the floor
   flag. A forger who additionally rebuilds a v1-shaped check set from the
   same evidence (the K19 shape) would also pass flagless — the floor flag is
   then the only defense in both directions.
4. **NOT-EVALUATED (exit 3) never overrides a floor violation** and a null
   check cannot survive relabeling into v1/v2 boolean grading (N2–N5).
5. **The producer cannot emit an older schema** (`:49`, no override flag), so
   every down-declaration is a post-hoc receipt edit, precisely the surface
   the opt-in floor closes when the caller asks.

## Named-mutant control (pre-registered V3-M1, MutBaselineControls.md)

Pristine green: G1 exit 0 (and R2 after restore). Exact edit: inserted
`    args.require_schema = "v1"` after the unique anchor
`    args = ap.parse_args(argv)` in gate `main`. Under the mutant, the
floor-v3 argv that produced F1/F5 exit 1 now produces **exit 0 VALID** (M1:
genuine v1; M2: genuine v2) — red attributable to the floor predicate alone.
M3: the v3→v1 relabel still exits 1 (id-set lock is an independent second
detector, as A5 predicted). Byte-exact restore: `git checkout --` then sha256
before/after both `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`,
`git status --porcelain` clean except `scratch/`; R1 re-greens the rejection
(exit 1 with the floor line again). So the delivered gate kills the named
round-18 mutant V3-M1; this is the named denominator, not a fresh-mutant
claim — fresh-mutant territory (`version < minimum` → `!= minimum`) is
FreshGate's item and untouched here.

Gate `--selftest`: exit 0, `selftest: 5 VALID and 1 NOT-EVALUATED receipts
accepted; 61 mutations + unreadable case rejected`. Floor rows exist at
`:1874-1881`: v1-under-v1→0, v1-under-v2→1, v2-under-v3→1, v3-under-v3→0.
Coverage note (minor, not a defect): no direct v1-under-floor-v3 selftest row
(transitively covered by v1<v2<v3; the controls suite K19 exercises
v1-under-v3 against the live gate).

## Data-quality note

`.ufo/waves/round-18/build/advice/C1Measure.md` (line 62 area) records the
current gate hash as `c5715641f34fb9b9ffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
— 65 hex chars, not a valid sha256 length. The tested bytes hash to
`c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` (64), and
the file did not change between the measured revision `c6dc46f` and pushed
`1c325b2`. Likely a transcription slip in that advice file; the gate identity
itself is not in doubt.

## Findings by severity

- **High:** none. The assigned escape (self-declared older schema under
  `--require-schema v3`) does not exist in the delivered gate; every floor
  value and unknown schema rejects as contracted, with exit-1 problems that
  name the floor.
- **Medium (boundary, by design but worth saying loudly):** flagless mode
  validates a v3→v2 relabel (A3) and `--require-schema v2` does too (A4).
  The schema floor is opt-in per invocation; there is no receipt-side or
  producer-side forcing. Any caller that validates receipts without the flag
  gets v1/v2-grade assurance on v3-era bytes.
- **Low (attribution nuance):** unknown schemas bypass the floor predicate
  (`version is None` guard) and are rejected by the schema-set check instead;
  same exit 1, no floor-named problem line. A caller grepping stdout for the
  floor message to confirm the floor fired will not find it on unknown
  schemas.
- **Low (coverage):** gate selftest lacks a direct v1-under-v3 floor row.
- **Data:** 65-char hash transcription in build advice C1Measure.md (above).

Residual risk / verification gaps: pins were always pin-clean by
construction, so floor×pin-mismatch interaction is untested (both problem
sets would independently append; no masking is possible since `problems` is
append-only). Controls-suite arms K19–K22 and the not-evaluated zero-loading
fixture live with sibling seats; I did not re-run them. The tool side was
read (constant `:49`, no flag) but not executed — no live runs, per bounds.

## Commands (all inside the clone)

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateSchemaFloor`
- `git -C /tmp/kama-r18-falsify-GateSchemaFloor switch -q -c seat/GateSchemaFloor 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
- `/usr/bin/python3 scratch/experiment.py` → exit 0, `TOTAL cases 30, unexpected 0`
- `/usr/bin/python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0 (also run inside the script)
- `sha256sum tests/llamacpp-live/check-receipt.py` → `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
- experiment.py sha256 `acca4c6319162f75fd7c9d579bb2285bb1649674d8dcdff53a36426f8a88880b`;
  log.jsonl sha256 `e2d77562b9f34d3b1d54b31b5a74be75daf1f48a83708d3a7a01e22e903b39e8`

## Appendix: exact experiment source

```python
#!/usr/bin/env python3
"""GateSchemaFloor falsify experiment (round 18).

Attack: declare v1/v2 under --require-schema v3; test each floor and unknown
schema; show the current v3 gate cannot escape by merely self-declaring an
older schema when the caller requires v3; report the default permissive
boundary honestly. Named-mutant control: MutBaselineControls.md V3-M1
(require_schema floor downgraded to v1 after parse) must turn the floor
rejections into escapes, then byte-exact restore re-greens them.

Runs only inside the seat clone. Fake/relabel receipts only; no servers,
no ports. /usr/bin/python3 matches the official runner.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

CLONE = "/tmp/kama-r18-falsify-GateSchemaFloor"
GATE = os.path.join(CLONE, "tests/llamacpp-live/check-receipt.py")
SCRATCH = os.path.join(CLONE, "scratch")
PY = "/usr/bin/python3"
LOG = []  # jsonl records of every case

os.makedirs(SCRATCH, exist_ok=True)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
        fh.write("\n")


def recorded_pins(rec):
    return ["--expect-model-sha256", rec["model"]["sha256"],
            "--expect-server-sha256", rec["server"]["sha256"],
            "--expect-probe-sha256", rec["probe"]["sha256"],
            "--expect-tool-sha256", rec["tool"]["sha256"]]


# ---------------------------------------------------------------- fixtures
r16 = os.path.join(CLONE, ".ufo/waves/round-16/live/receipt.json")
r17 = os.path.join(CLONE, ".ufo/waves/round-17/live/receipt-1.json")
r18 = os.path.join(CLONE, ".ufo/waves/round-18/live/receipt-1.json")

v3_path = os.path.join(SCRATCH, "v3.json")
shutil.copyfile(r18, v3_path)
v3 = load_json(v3_path)
PINS_V3 = recorded_pins(v3)

V1, V2, V3S = ("kama-llamacpp-live/v1", "kama-llamacpp-live/v2",
               "kama-llamacpp-live/v3")


def relabel(base, schema, name):
    d = json.loads(json.dumps(base))
    if schema is None:
        d.pop("schema", None)
    else:
        d["schema"] = schema
    p = os.path.join(SCRATCH, name)
    dump_json(d, p)
    return p


v1_path = os.path.join(SCRATCH, "v1.json")
shutil.copyfile(r16, v1_path)
v2_path = os.path.join(SCRATCH, "v2.json")
shutil.copyfile(r17, v2_path)
PINS_V1 = recorded_pins(load_json(v1_path))
PINS_V2 = recorded_pins(load_json(v2_path))

f_v3_as_v1 = relabel(v3, V1, "v3_as_v1.json")
f_v3_as_v2 = relabel(v3, V2, "v3_as_v2.json")
f_unk4 = relabel(v3, "kama-llamacpp-live/v4", "unk4.json")
f_unkV3 = relabel(v3, "kama-llamacpp-live/V3", "unkV3.json")
f_unkempty = relabel(v3, "", "unkEmpty.json")
f_unkmiss = relabel(v3, None, "unkMissing.json")
v2d = load_json(v2_path)
f_v2_as_v3 = relabel(v2d, V3S, "v2_as_v3.json")

# Legitimate not-evaluated v3 fixture: the gate selftest's own derivation.
spec = importlib.util.spec_from_file_location("cr", GATE)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)
ne = cr._selftest_receipt_v3()
ne["transitions"] = [row for row in ne["transitions"]
                     if not (row.get("path") == "/v1/models"
                             and row.get("status") == 503)]
ne.update(loading_503=None, loading_503_bodies=[],
          loading_bodies_dropped=0, loading_observed=False,
          loading_envelope_exact=None, outcome="not-evaluated")
lc = next(c for c in ne["checks"] if c["id"] == "loading_envelope_graded")
lc.update(passed=None, evaluated=False)
lc["observed"].update({"loading_observed": False, "distinct_bodies": 0,
                       "bodies_dropped": 0, "total_503_responses": 0,
                       "all_exact": None, "exact": None,
                       "not_evaluated_reason": "no-loading-503-observed"})
ne_path = os.path.join(SCRATCH, "ne.json")
dump_json(ne, ne_path)
PINS_NE = recorded_pins(ne)
f_ne_as_v1 = relabel(ne, V1, "ne_as_v1.json")
f_ne_as_v2 = relabel(ne, V2, "ne_as_v2.json")

# ---------------------------------------------------------------- runner
def run_gate(label, receipt, extra, expect, tag):
    argv = [PY, GATE, receipt] + list(extra)
    p = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    out = p.stdout.strip().splitlines()
    problems = [l for l in out if l.startswith("  - ")]
    ok = (p.returncode == expect)
    rec = {"tag": tag, "label": label, "argv": argv,
           "exit": p.returncode, "expected": expect, "ok": ok,
           "head": out[0] if out else "",
           "problems": problems,
           "stderr": p.stderr.strip().splitlines()[:3]}
    LOG.append(rec)
    flag = "OK  " if ok else "FAIL"
    print(f"[{flag}] {label}: exit {p.returncode} (want {expect})"
          f" | {rec['head']}")
    for pr in problems[:6]:
        print(f"        {pr}")
    if p.stderr.strip():
        print(f"        stderr: {p.stderr.strip().splitlines()[0]}")
    return rec


R = []
print("== green pristine ==")
R.append(run_gate("G1 genuine v3 + own pins + floor v3", v3_path,
                  PINS_V3 + ["--require-schema", "v3"], 0, "G1"))

print("== floor matrix on genuine legacy receipts ==")
R.append(run_gate("F1 genuine v1 + floor v3", v1_path,
                  PINS_V1 + ["--require-schema", "v3"], 1, "F1"))
R.append(run_gate("F2 genuine v1 + floor v2", v1_path,
                  PINS_V1 + ["--require-schema", "v2"], 1, "F2"))
R.append(run_gate("F3 genuine v1 + floor v1", v1_path,
                  PINS_V1 + ["--require-schema", "v1"], 0, "F3"))
R.append(run_gate("F4 genuine v1 flagless (legacy verdict)", v1_path,
                  PINS_V1, 0, "F4"))
R.append(run_gate("F5 genuine v2 + floor v3", v2_path,
                  PINS_V2 + ["--require-schema", "v3"], 1, "F5"))
R.append(run_gate("F6 genuine v2 + floor v2", v2_path,
                  PINS_V2 + ["--require-schema", "v2"], 0, "F6"))
R.append(run_gate("F7 genuine v2 flagless (legacy verdict)", v2_path,
                  PINS_V2, 0, "F7"))
R.append(run_gate("F8 genuine v3 + floor v2 (minimum semantics)", v3_path,
                  PINS_V3 + ["--require-schema", "v2"], 0, "F8"))
R.append(run_gate("F9 genuine v3 + floor v1", v3_path,
                  PINS_V3 + ["--require-schema", "v1"], 0, "F9"))
R.append(run_gate("F10 genuine v3 flagless", v3_path, PINS_V3, 0, "F10"))

print("== attack: v3-evidence receipt self-declaring older schemas ==")
r_a1 = run_gate("A1 v3-as-v1 + floor v3 (headline)", f_v3_as_v1,
                PINS_V3 + ["--require-schema", "v3"], 1, "A1")
r_a2 = run_gate("A2 v3-as-v2 + floor v3 (headline)", f_v3_as_v2,
                PINS_V3 + ["--require-schema", "v3"], 1, "A2")
r_a3 = run_gate("A3 v3-as-v2 FLAGLESS (permissive boundary)", f_v3_as_v2,
                PINS_V3, 0, "A3")
r_a4 = run_gate("A4 v3-as-v2 + floor v2 (floor v2 does not defend)",
                f_v3_as_v2, PINS_V3 + ["--require-schema", "v2"], 0, "A4")
r_a5 = run_gate("A5 v3-as-v1 FLAGLESS (id-set lock, not floor)",
                f_v3_as_v1, PINS_V3, 1, "A5")
r_a6 = run_gate("A6 v3-as-v1 + floor v1", f_v3_as_v1,
                PINS_V3 + ["--require-schema", "v1"], 1, "A6")

print("== unknown / missing schema ==")
for i, (p, name) in enumerate([(f_unk4, "v4"), (f_unkV3, "V3 case"),
                               (f_unkempty, "empty"),
                               (f_unkmiss, "missing")]):
    R.append(run_gate(f"U{i+1} unknown schema {name} flagless", p,
                      PINS_V3, 1, f"U{i+1}"))
R.append(run_gate("U5 unknown schema v4 + floor v3 (floor skips, "
                  "validator rejects)", f_unk4,
                  PINS_V3 + ["--require-schema", "v3"], 1, "U5"))

print("== up-relabel: older evidence declared v3 ==")
R.append(run_gate("P1 genuine v2 relabeled v3 flagless", f_v2_as_v3,
                  PINS_V2, 1, "P1"))

print("== not-evaluated precedence ==")
R.append(run_gate("N1 genuine not-evaluated v3 + floor v3 -> exit 3",
                  ne_path, PINS_NE + ["--require-schema", "v3"], 3, "N1"))
R.append(run_gate("N2 ne-as-v1 + floor v3 -> exit 1 (floor dominates 3)",
                  f_ne_as_v1, PINS_NE + ["--require-schema", "v3"], 1, "N2"))
R.append(run_gate("N3 ne-as-v2 + floor v3 -> exit 1", f_ne_as_v2,
                  PINS_NE + ["--require-schema", "v3"], 1, "N3"))
R.append(run_gate("N4 ne-as-v2 + floor v2 -> exit 1 via v2 boolean demand",
                  f_ne_as_v2, PINS_NE + ["--require-schema", "v2"], 1, "N4"))
R.append(run_gate("N5 ne-as-v2 flagless -> exit 1", f_ne_as_v2,
                  PINS_NE, 1, "N5"))

print("== argparse guard on the floor value ==")
for i, bad in enumerate(["v4", "v10", "V3"]):
    R.append(run_gate(f"E{i+1} --require-schema {bad!r}", v3_path,
                      PINS_V3 + ["--require-schema", bad], 2, f"E{i+1}"))

# ------------------------------------------------- named mutant V3-M1
print("== named mutant V3-M1 (floor downgraded to v1) ==")
sha_before = sha256_file(GATE)
src = open(GATE, encoding="utf-8").read()
anchor = "    args = ap.parse_args(argv)\n"
assert src.count(anchor) == 1, "parse_args anchor not unique"
open(GATE, "w", encoding="utf-8").write(
    src.replace(anchor, anchor + '    args.require_schema = "v1"\n'))
R.append(run_gate("M1 v1 + floor-v3 argv under V3-M1 -> escapes 0",
                  v1_path, PINS_V1 + ["--require-schema", "v3"], 0, "M1"))
R.append(run_gate("M2 v2 + floor-v3 argv under V3-M1 -> escapes 0",
                  v2_path, PINS_V2 + ["--require-schema", "v3"], 0, "M2"))
R.append(run_gate("M3 v3-as-v1 + floor-v3 argv under V3-M1 -> still 1 "
                  "(id-set lock is a second detector)", f_v3_as_v1,
                  PINS_V3 + ["--require-schema", "v3"], 1, "M3"))
subprocess.run(["git", "-C", CLONE, "checkout", "--",
                "tests/llamacpp-live/check-receipt.py"], check=True)
sha_after = sha256_file(GATE)
print(f"restore: sha_before {sha_before}")
print(f"restore: sha_after  {sha_after}")
print(f"restore byte-exact: {sha_before == sha_after}")
R.append({"tag": "RESTORE", "sha_before": sha_before,
          "sha_after": sha_after, "byte_exact": sha_before == sha_after})
R.append(run_gate("R1 v1 + floor v3 after restore -> 1 again", v1_path,
                  PINS_V1 + ["--require-schema", "v3"], 1, "R1"))
R.append(run_gate("R2 genuine v3 + floor v3 after restore -> 0", v3_path,
                  PINS_V3 + ["--require-schema", "v3"], 0, "R2"))

# ---------------------------------------------------------------- selftest
print("== gate selftest ==")
p = subprocess.run([PY, GATE, "--selftest"], capture_output=True,
                   text=True, timeout=300)
print(f"selftest exit {p.returncode} (want 0)")
print(p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "")
R.append({"tag": "SELFTEST", "exit": p.returncode,
          "tail": p.stdout.strip().splitlines()[-1:]})
LOG.append({"tag": "SELFTEST", "exit": p.returncode,
            "stdout_tail": p.stdout.strip().splitlines()[-1:]})

with open(os.path.join(SCRATCH, "log.jsonl"), "w") as fh:
    for rec in LOG:
        fh.write(json.dumps(rec) + "\n")

fails = [r for r in R if r.get("ok") is False]
print(f"\nTOTAL cases {len([r for r in R if 'ok' in r])}, "
      f"unexpected {len(fails)}")
for f in fails:
    print("UNEXPECTED:", f["label"], f["exit"], "want", f["expected"])
print("gate sha256 (pristine):", sha_before)
sys.exit(1 if fails else 0)
```

Cleanup: the clone/scratch tree `/tmp/kama-r18-falsify-GateSchemaFloor` is
removed after this report is written; nothing was copied back except this
file. No seat-owned listener or process remains (the experiment opened no
socket; post-run `pgrep` for the experiment and gate paths returned empty).
