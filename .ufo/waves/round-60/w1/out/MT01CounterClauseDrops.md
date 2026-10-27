# MT01CounterClauseDrops — round-60 C1 counter clause-drop mutation test

Seat: MT01CounterClauseDrops (mutation tester, leaf). Axes: operability/calibration. Judged on operability.
Attacked invariant: the C1 claim's detection clause — "each of its 7 controls is rejected" — is load-bearing
for every clause of `tools/round60-c1-counter.py::verify()` at the frozen tip.

Measured tip: `e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1` (commit; lane HEAD `11f2d667…` had advanced past it,
counter was run with `--tip e0b5b1e…` explicitly, matching the assignment). Counter under test is the tip's own
`tools/round60-c1-counter.py` (working-tree sha256 `175c291674fc53e71d415fa22e31b3665bcb52f4501ea56b638c405aef677d86`,
byte-identical to my pristine copy). Lane source untouched.

## Method

1. Copied the counter to scratch (`/fast/scratch/hyaku/kama-r60/MT01CounterClauseDrops/pristine.py`).
2. Generated 31 mutants, each dropping exactly one verify() clause (the clause's `bad.append` neutralized, or
   the REQUIRED loop filtered to exclude one check id). Every replacement asserted its expected occurrence
   count before applying. Mutant hashes: `out/MT01CounterClauseDrops/evidence/scripts/mutant-hashes.txt`.
3. Ran baseline (pristine) + 31 mutants, each a full fresh-nonce live lifecycle against the tip:
   `python3 <mutant> --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e0b5b1e… --work <scratch>/work-<name>`.
   Baseline gated the battery; 8 mutants ran concurrently (each run owns its own ephemeral port).
4. Forensic pass (separate): one live run (nonce `c180a667979787dd95`), then 29 minimal forgeries probed against
   pristine + all 31 mutant `verify()`s to attribute exactly which clause catches what, and to design the
   smallest additional controls. Receipt + serve.log copied to `out/MT01CounterClauseDrops/evidence/`.
5. Verdict rule (as tasked): mutant still prints `met=True` → that clause is uncovered by the 7 controls.

Baseline (pristine): `exit=0 · tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1
tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True` — detector valid; baseline passed, results are conclusive.

## Battery result: mutant → output → verdict

All 32 raw outputs: `out/MT01CounterClauseDrops/evidence/results/<name>.txt`.

| mutant (clause dropped) | counter output deltas | met | verdict |
|---|---|---|---|
| pristine (baseline) | all controls rejected | True | baseline valid |
| binary-sha | tamper_rejected=**2/3** | **False** | **covered** (uniquely, by tamper t2 `binary_sha256="0"*64`) |
| nonce | all rejected (stale still 1/1) | True | uncovered |
| verdict | all rejected | True | uncovered |
| port | all rejected (t3 still 3/3) | True | uncovered |
| req-all (REQUIRED loop dropped) | all rejected (fake still 2/2) | True | uncovered |
| req-binary-digest … req-teardown (16 single-check drops) | all rejected | True | uncovered (all 16) |
| capture-sha | all rejected (t1 still 3/3) | True | uncovered |
| tags-entry | all rejected (t1 still 3/3) | True | uncovered |
| ps-digest | all rejected | True | uncovered |
| version | all rejected | True | uncovered |
| teardown | all rejected | True | uncovered |
| log-listening | all rejected (log still 1/1) | True | uncovered |
| log-generate | all rejected (log still 1/1) | True | uncovered |
| manifest | all rejected | True | uncovered |
| manifest-layer | all rejected | True | uncovered |
| blob-sha | all rejected | True | uncovered |

**30 of 31 mutants survived** (`met=True`, exit 0). Only `binary-sha` is uniquely pinned by the 7 controls.

## Why each survivor survives (mechanism, from the forgery map)

Forgery map (pristine verify() trip sets; full table in `evidence/forgery-map.md`):

| forgery | pristine trips | clauses needed |
|---|---|---|
| stale nonce (verify under different nonce) | `nonce capture-parse manifest` | nonce redundant: the nonce is re-derived from capture bodies (qualified `kama-<nonce>:latest` lookup → `capture-parse`) and the manifest glob is nonce-derived (`manifest`) |
| tamper t1: tags body `kama-`→`kamb-` unsigned | `capture-sha:tags tags-entry` | dropping either clause leaves the other → both uncovered |
| tamper t3: port→8080 | `port log-listening` | log-listening regex interpolates the receipt port → double coverage → port uncovered |
| log file removed (committed control) | `log-listening log-generate` | either alone suffices → both uncovered |
| verdict→MODEL_KO | `verdict` only | no committed control forges verdict |
| each check flip (16) | `check:<cid>` only | no committed control touches `checks[]`; fake-binary controls still rejected via `binary-sha` alone |
| v1-models body + " " (unsigned) | `capture-sha:v1-models` only | t1's double coverage masks the capture-sha clause |
| tags re-signed duplicate entry | `tags-entry` only | needs body re-signed to isolate |
| ps-after re-signed digest swap | `ps-digest` only | no committed control forges it |
| version re-signed "0.40.10" | `version` only | no committed control forges it |
| teardown.returncode=1 | `teardown` only | no committed control forges it |
| Listening line only removed | `log-listening` only | — |
| POST /api/generate line only removed | `log-generate` only | — |
| manifest file removed | `manifest` only | no committed control removes it |
| manifest layer `sha256:<model>` zeroed | `manifest-layer` only | no committed control edits it |
| blob + 1 byte | `blob-sha` only | no committed control corrupts it |

Reading: ps-digest, version, teardown, manifest, manifest-layer, blob-sha, verdict and the whole REQUIRED family
are only *positively* asserted on the genuine receipt (the `live_ok` path). Dropping such a clause can never break
`live_ok=1/1`, and no committed control forges those fields — so `met` stays True by construction. The remaining
survivors (nonce, port, capture-sha, tags-entry, log-*) are covered only *jointly* with a sibling clause, so each
is individually redundant.

## Smallest additional control per uncovered clause

All are edits inside the existing control block of the counter (in-memory receipt copies, or file edits restored
right after `verify`); each forgery's pristine trip set is exactly the target clause, so each added control is
killed by dropping its clause — including the whole REQUIRED family for the loop control. I did not apply any of
these to the lane (fix-shaped suggestions only).

1. verdict — 4th receipt tamper: `t["verdict"]="MODEL_KO"` must be rejected.
2. REQUIRED family — tamper loop: for each `cid` in REQUIRED, flip `checks[cid].passed=False` (deep copy per cid)
   and require rejection. Covers all 16 single-check clauses and the family as a whole.
3. capture-sha — unsigned body tamper on a capture no other clause parses (`v1-models` body + one space) must be
   rejected. (Or: keep t1 and re-sign it — then capture-sha loses; prefer the unsigned variant.)
4. tags-entry — re-signed tags body carrying a *duplicate* `kama-<nonce>:latest` entry must be rejected.
5. ps-digest — re-signed ps-after with the model digest swapped must be rejected.
6. version — re-signed version body saying `0.40.11`→`0.40.10` must be rejected.
7. teardown — tamper `teardown.returncode=1` must be rejected.
8. log-listening — serve.log with *only* the `Listening on 127.0.0.1:<port>` line removed must be rejected.
9. log-generate — serve.log with *only* the `POST "/api/generate"` line removed must be rejected.
10. manifest — run dir with the manifest file removed (restored after) must be rejected.
11. manifest-layer — manifest with `sha256:<FROZEN_MODEL_SHA>` zeroed (restored after) must be rejected.
12. blob-sha — imported blob with one appended byte (restored after) must be rejected.
13. port — t3 is already rejected, but only via log-listening; to pin the clause itself, assert the clause name:
    `"port" in verify(t3, run1, nonce)` (same clause-named assertion style would tighten every control).
14. nonce — rejection is already redundant (capture-parse + manifest both fire on a stale nonce), so no added
    control is needed for the kill rule; pin the clause only if clause-level attribution matters:
    `"nonce" in verify(rec, run1, stale_nonce)`.

## Scope note

This is a control-granularity coverage finding, not a claim violation: at the frozen tip the predicate holds
(baseline `met=True`, errors=0 reproduced live here), and every clause is individually sound — the forgery map
supplies a minimal forgery that only that clause catches. The gap is that the 7 committed controls exercise
detection in bundles, so 30 of 31 single-clause forgeries would pass undetected by `met`.

## Restoration evidence

- Lane file `tools/round60-c1-counter.py` sha256 before the battery: `175c291674fc53e71d415fa22e31b3665bcb52f4501ea56b638c405aef677d86`;
  after all 32 runs: `175c291674fc53e71d415fa22e31b3665bcb52f4501ea56b638c405aef677d86` (identical; `evidence/scripts/lane-counter-{before,after}.sha256`).
- Mutants ran from scratch copies only; no lane tree write of any kind (no commit/stash/jj anywhere).
- Forensics file-level forgeries restored byte-exact after each probe; final pristine `verify()` accepted the
  restored artifacts (`RESTORATION pristine-accepts-after-restore=True`).
- Disk guard at start: `/fast/scratch/hyaku` 27% used, 593.2G free; scratch removed after evidence copy-out.
- Tooling record (operator directive 2026-10-19): no tools installed or upgraded — none needed; python3/git/tar
  from the host sufficed.

Evidence bundle: `out/MT01CounterClauseDrops/evidence/` (receipt `receipt-nonce-c180a667979787dd95.json`,
`serve.log`, `forgery-map.md`, `results/` (32 counter outputs), `mutants/` (31 mutant sources),
`scripts/` (driver, forensics, hashes, pristine copy)).
