# CounterC1 — falsify of `.ufo/waves/round-18/c1/measure.py`

VERDICT: partial — pristine baseline reproduces the claim arms exactly and every binding/refusal control held, but the counting command's exit-0 CLEAN is forgeable by its own child: an accepted_bad/good_rejected row-vs-count divergence and a `model_unchanged` label both yield CLEAN (executed experiments below).

## Environment

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-CounterC1` then `git switch -c seat/CounterC1 1c325b2e58fcfdc6761f645b44cedfb1d65243e6` → `git rev-parse HEAD` = `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. All runs inside the clone; nothing copied back except this report.
- Input hashes (sha256, clone working tree):
  - measure.py `a9577ed889572e929b404268b87d50000c56e62c36e6c54f6f9113a3012a490f` (byte-identical to live lane file)
  - controls.py `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`
  - tool `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`; gate `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
  - probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; registry `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c`
  - frozen blobs from `git show e75cf680b53484a61709ee1b2787d8dbc6419f74:…`: tool `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, gate `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`
- Python 3.14.8 (`/usr/bin/python3`). Installs: none (no tool installed or upgraded). Timeouts: none hit (longest run 40.9 s). No listener was opened by any experiment; children are pure-compute (synthetic) or the delivered controls (loopback ephemeral, in-run, reaped — `leaked_processes: []` in baseline).
- Official-pipeline delta noted: `git diff --stat c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d..HEAD` touches only measure.py (+96/−21) among the four C1 files; the official `runs/c1-measure.exit` = 2 (old classification-based cross-check wording "0 row(s) classified misclassified") is superseded by the bucket-aware check at the pushed commit.

## E0 — pristine baseline (GREEN, attribution reference)

Command: `python3 .ufo/waves/round-18/c1/measure.py --controls tests/llamacpp-live/controls.py --frozen-tool scratch-c1/frozen-tool.py --frozen-gate scratch-c1/frozen-gate.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --json --out scratch-c1/out-baseline.json` → `exit=0` in 40.91 s wall.

- `exit 0, clean=True`, `faults []`, `warnings []`, `pins frozen_tool/frozen_gate verified True`.
- Counts: `accepted_bad 5→0 (Δ−5)`, `good_rejected 1→0`, `misclassified 1→0`, `uncontrolled_checks 0→0 ([]→[])`, `gate_flip_arms 16→17`, `good_ok true→true` — exactly the raw arms the round-18 lesson declares.
- Runs: before controls exit 1 (19.917 s, stdout sha `13acb55318063021…`), after exit 0 (20.931 s, stdout sha `204f9a652287156b…`); `leaked_processes []` both sides; controls-reported `tool_sha256/gate_sha256` matched the passed files both sides.

## Findings by severity

### F1 HIGH — counter certifies `accepted_bad`/`good_rejected` without row cross-check; CLEAN is forgeable by the child (executed)

`measure.py:574-585` cross-checks only `misclassified` against row buckets; no counterpart exists for `accepted_bad`/`good_rejected`, and `clean_reasons` (`measure.py:621-633`) plus the exit predicate (`measure.py:838-841`) consume the reported top-level counts verbatim.

- E1 `child_launder_ab.py` (doc: `accepted_bad=0, good_rejected=0, misclassified=0, uncontrolled_checks=[], good_ok=true, exit 0`; rows: `k0 ('accepted','ok')`, `k1 ('accepted','accepted_bad')` with a `gate_flip` object): measured → **exit=0, clean=True, faults [], warnings []** (runs before+after identical, `stdout_sha a7aff6948e302205…`). The child's own retained row says a bad control was accepted while the certified count and verdict say zero — no fault, no warning, not even a note.
- E2 attribution control `child_launder_mc.py` — the identical forgery shape with `bucket='misclassified'` instead — measured → **exit=2** with faults `before/after: misclassified=0 but 1 row(s) have a misclassified outcome bucket`. Same harness (pins verified True both), so the E1 red is attributable precisely to the missing accepted_bad/good_rejected conjunct, not to harness breakage.
- This is NOT the docstring's admitted "controls.py that misreports consistently" case: E1's doc is internally inconsistent and the counter retains the contradicting rows in the same report. The real controls derives counts from its own rows (`tests/llamacpp-live/controls.py:1247-1249`), so the delivered pipeline is consistent today; the gap is that the counter's four-count control reduces to "the child said so" for three of the four counts. Impact: the round's certified "accepted-bad 5 → 0" is protected against byte-swap and exit/count contradiction but not against a buggy/coerced child under-reporting its own accepted_bad rows. Suggested repair: extend the `measure.py:574` cross-check to `accepted_bad` and `good_rejected` (same counted==len(rows) logic), or derive them from rows whenever every row carries a reported bucket.

### F2 MEDIUM — `model_unchanged` label hard-excludes any uncontrolled check from the exit predicate (executed)

`measure.py:122` (`EXCLUDED_UNCONTROLLED = frozenset({'model_unchanged'})`) and `measure.py:571-573` drop that label from `uncontrolled_checks` into `uncontrolled_excluded` before `clean_reasons` runs.

- E3 `child_unc_model.py` (`uncontrolled_checks=['model_unchanged']`): measured → **exit=0, clean=True**, `uncontrolled_excluded=['model_unchanged']` (stdout sha `f888ded6b076e1a0…`).
- E4 `child_unc_props.py` (same doc, label `props_alias`): measured → **exit=1, clean=False**, reason `uncontrolled_checks=props_alias`.
- Any uncontrolled check id relabelled `model_unchanged` defeats the fourth count. The exclusion duplicates the real controls' own subtraction (`controls.py:1271-1272`, `INPUT_INTEGRITY` at `controls.py:191`), so at counter level it is trust, not control. Note the selftest asserts exactly this behavior (`model-only` → exit 0, `measure.py` selftest), so it is deliberate — but it remains a label-only laundering channel a fresh child exercised. Repair direction: exclude only ids the doc itself declares in `input_integrity_checks` AND require the controls' declared universe to match, or drop the counter-level exclusion and let the controls own it.

### F3 MEDIUM — self-contradictory `gate_flip_arms` tolerated note-only (executed)

`measure.py:538-540` records a top-level `gate_flip_arms` that conflicts with the number of rows carrying `gate_flip` objects as a *note*, never a fault; the exit predicate ignores notes.

- E5 `child_gfa_conflict.py` (`gate_flip_arms=99`, 1 row with a `gate_flip` object): measured → **exit=0, clean=True** with note `gate_flip_arms=99 but 1 row(s) carry a gate_flip object` (stdout sha `b3f855b6a920271a…`).
- `gate_flip_arms` is part of the certified evidence (16→17 in E0) and a self-mutant kill signature (`drop-gate-flip-arm`); an inflated or zeroed value passes with a note in the JSON only. Repair: fault on `flip_seen and gate_flip_arms != flip_arms`.

### F4 LOW — interpreter identity recorded as version string, not pinned

`measure.py` records `python: sys.version.split()[0]` ("3.14.8" in E0) and spawns controls with `sys.executable`; per-run argv (which embeds the interpreter path) is retained, but the interpreter binary is not hashed or pinned, so a same-version different-interpreter substitution is undetected. Limits: no claim text visited pins the interpreter; recorded as a residual pin gap only.

### F5 LOW — probe/registry pins are self-referential (code-read, not executed)

Probe is hashed and recorded but bound to no reference value; comparability holds only because the same path serves both sides by construction. Registry resolution mirrors the controls' own (`measure.py _registry_note` vs `controls.py:172-173`), absence → warning (`registry absent: … stages an EMPTY registry`); if controls then fails staging (`controls.py:832-835` raises `ControlsFault`), measure faults exit 2 — this second half is code-cited, not executed.

### F6 INFO — per-cell raw output retention is hash+doc, not bytes

Each run record retains parsed `doc`, `doc_canonical_sha256`, and `stdout_sha256` (E0: after canon `bb00521ab379963b…`, before canon `35d72d9f22644fd9…`); raw stdout bytes are not persisted anywhere, so post-hoc byte re-verification is impossible (doc-tamper detection via canonical sha remains). The docstring documents exactly this; no claim is overstated. stderr retained as 2000-byte tail only.

## Positive controls (held)

- E6 frozen-binding refusal: drifted `--frozen-tool` copy (sha `fcb3a66bfd896855…`) → **exit=2, runs empty**, fault `frozen_tool … sha256 fcb3a66b… != git e75cf680…:tools/kama-llamacpp-live.py sha256 0efd1723…`; the honest sibling pin stayed `verified True`. Byte-exact restoration not required (scratch copy), original untouched (`git status` clean aside from `scratch-c1/`).
- E0 baseline: `tool_sha256/gate_sha256` mismatch path and exit-0-vs-counts path are selftest-covered (`measure.py --selftest` asserts both; official `runs/` retains its exit 0), and E2/E6 exercised the refusal paths live.
- Claim-arm reproduction (E0) matches the lesson's raw numbers arm-for-arm, so the delivered counts were not fabricated at counter level.

## Denominators and limits

Fresh synthetic-child attacks here are a separate denominator from the named round-17 survivor set and from measure.py's own three self-mutants (official `c1-self-mutants.exit` = 0, all killed). Experiments ran the measurement mode only; `--self-mutants` mode was not re-exercised. C1's live tool/gate receipts were not attacked (other seats own those); a successful counter forgery does not by itself refute the operability claim's substance — it shows the counting command's CLEAN verdict and its four certified numbers are child-trusted for 3 of 4 counts, so L1 should not present the counter as independently controlling those numbers.

## Teardown

Report written; `rm -rf /tmp/kama-r18-falsify-CounterC1` executed after writing; no seat-owned listener or process remains (nothing in any experiment outlived its run: baseline `leaked_processes []`, children pure-compute).
