# Z02EvidenceLean — derivable evidence, oversized artifacts, and the replay-minimal set

Seat: `Z02EvidenceLean` (simplifier, leaf), round 56 w1, lane `kama-shokunin`. Axes: operability, calibration.
Scope: the **wave evidence** produced for round 56 — not the production counters (that is `Z01DeadWeight`'s
scope). Advisory only: no claim predicate, counter, target, kill rule or preregistration byte was changed,
and nothing was deleted in the lane.

**Verdict.** The wave's evidence set contains **503,476 removable bytes (36.4 % of 1,384,600)** that add no
information an auditor cannot reconstruct from bytes already frozen: 6 duplicate groups, 3
byte-derivable artifacts, and 1 content-dedup compaction. Conversely, the set that *is* required for independent replay is **6 witness
receipts of 924 bytes plus two commits and one 3,689-byte preregistration** — I replayed C1 and C2 end to end
from a fresh clone and got every frozen field and exit without writing a byte into the lane. Two evidence
defects block a clean external replay: the battery hardcodes the lane path for its output
(`tools/round56-env-leg-battery.py:10-14,37`), and the receipts the frozen C1 target names are **not in the
freeze commit** (untracked).

## 1. Inventory (measured)

| Measure | Value |
|---|---|
| Files under `.ufo/waves/round-56/` | 259 |
| Total bytes | 1,384,600 |
| Distinct sha256 blobs | 174 |
| Duplicate copies | 85 (142,553 bytes) |
| Of which one file pair | `w1/validate.out` = `w1/dispatch.json` (115,671 B, sha256 `a8ca4025…`) |
| Largest single seat directory | `X06Census` 297,672 B — 252,706 B of it one `git show` copy |
| Committed at freeze tip | `preregistration.json`, `controls/base-c1.out`, `controls/base-c2.out`, `sources/{ld.so.8,rtld-audit.7}.html`, the five round-56/54 tools |
| Untracked at freeze tip | `measured/`, `census/`, `w1/` (porcelain `??`) |

Per-file accounting with hashes and re-derivation recipes: `Z02EvidenceLean/candidates.tsv`.

## 2. Necessary for independent replay

A replay needs the *producers and their inputs*, not the wave's derived files. The closure I verified:

| # | Artifact | Bytes | Why it cannot be dropped |
|---|---|---|---|
| 1 | commit `e10b6d39` (base) | — | `tools/round54-replay-code-audit.py` (`c81fe971…`), `corpus/SOURCES.md` blob `e25f363d…`, and the absence of every round-56 file |
| 2 | commit `efc6b3ec` (freeze) | — | frozen counter `fc3d4b63…`, driver `ec7a2519…`, battery `79b19596…`, checker `c7b0d787…`, prereg `fa4b5a10…`, both source HTMLs; tool bytes at the tip equal the worktree byte for byte (all five) |
| 3 | `controls/base-c1.out`, `controls/base-c2.out` | 275 | red-baseline execution witness; the C2 one carries an operator-appended `exit=1` that the tool does not emit |
| 4 | `measured/{base-c1,build-c1,m-drop-ldaudit}.out` | 551 | C1's three measured legs: pid, `problems=[]`, and appended `exit=` |
| 5 | `measured/build-c2.out` | 98 | the only C2 freeze-tip receipt — and the only one **without** an `exit=` line |
| 6 | `census/start.out` | 13,082 | the only pre-freeze registry snapshot; after S512/S513 landed it is not derivable. Currently untracked |
| 7 | `V04LateOutputs/r55-uncommitted-manifest.json` | 56,665 | r55 immutability guard: 305/305 entries still match disk at `efc6b3ec`; becomes non-derivable on the next lane write |
| 8 | mutant *definition* (`m-drop-ldaudit.diff`, 673 B) | 673 | the 47,518-byte copy is regenerable from it (sha `a3faaf6e…`); the digest itself is **not** frozen (F5) |

Items 3–5 are 924 bytes and are the only **execution witnesses** (pids, stream order, appended exits) that
no commit carries. Items 1–2 are the replay inputs; 6–8 are audit/definition inputs.

Verified minimal replay, from a `--no-local` clone of the lane at `efc6b3ec`, `HOME`/`TMPDIR` inside seat
scratch, nothing written to the lane:

```
python3 tools/round56-prereg-check.py --repo . --tip e10b6d39…   → present=0 roster_match=0 kills=0 controls=0 met=False  exit=1
python3 tools/round56-prereg-check.py --repo . --tip efc6b3ec…   → present=1 roster_match=1 kills=1 controls=2 met=True   exit=0
python3 tools/round56-env-leg-test.py --counter tools/round56-replay-code-audit.py --expect detected → detected exit=0
python3 tools/round56-env-leg-test.py --counter tools/round54-replay-code-audit.py --expect missed   → missed   exit=0
python3 tools/round56-env-leg-test.py --counter <rebuilt mutant> --expect missed                    → missed   exit=0
python3 tools/round56-env-leg-test.py --counter <rebuilt mutant> --expect detected                  → missed   exit=1
python3 <battery copy with 2-line path rebind>                                                      → 3/3 pass, exit=0
```

Receipts: `Z02EvidenceLean/replay/{c1-legs.out,c2-e10b6d3.out,c2-efc6b3e.out,battery.out}`.

## 3. Why "replay" is field-level, not byte-level

Frozen receipts carry `pid=` and are captured two different ways: the battery writes `stdout + stderr`, the
driver's parent logs stderr first. A raw `diff` between the frozen receipt and a re-run is therefore non-empty
even after pid normalisation. Sorted + pid-normalised, the diff is empty (`derivations/proofs.txt`, last
section). X01ReplayC1's table calls the pair "identical, `diff_exit=0`"; that holds only after
normalisation + sort (F6). Any future evidence identity check must normalise pid and stream order, or record
only fields.

## 4. Deletion candidates (forward only — lane read-only, 0 deleted)

| # | Path | Bytes | Proof it carries nothing new |
|---|---|---|---|
| D1 | `w1/out/X06Census/SOURCES-base.md` | 252,706 | sha256 `4962c9a0…` = `git show e10b6d39:corpus/SOURCES.md`; `cmp` identical. Replace citations with the `git show` form |
| D2 | `w1/out/X01ReplayC1/m-drop-ldaudit.py` | 47,518 | rebuilt from frozen counter + committed `.diff` → sha256 `a3faaf6e…` exactly; the diff is 2 changed lines, line numbers below it unchanged |
| D3 | `w1/validate.out` | 115,671 | **byte-identical to `w1/dispatch.json`** (sha `a8ca4025…`); the name promises a validation verdict the bytes do not contain |
| D4 | `w1/out/swarm-registry.json` | 52,626 | `members` dict equals `dispatch.json:registry.members`; remaining fields are `schema`/`wave`/`createdAt`/`updatedAt`/`reportDir`; all 64 `agentId` are null (no progress recorded) |
| D5 | `w1/out/X06Census/rerun-validate2.out` | 13,167 | identical to `rerun-validate.out` (sha `3eeea0f4…`); determinism is one equality assertion |
| D5b | `w1/out/S04Policy/census-worktree-validate.out` | 13,167 | third copy of the same `3eeea0f4…` bytes |
| D6 | `w1/out/X08ExitReceipts/receipts/` | 4,613 | 7/7 files byte-identical to wave-root `controls/`, `measured/`, `preregistration.json`; `receipts-check.py` already takes `--receipts`/`--prereg`, so it can read the originals |
| D7 | `S03SecretScan/gitleaks-{delta,commit-range}.json` | 6 | both the 3-byte `[]` with sha `37517e5f…`, same as the primary snapshot |
| D8 | `Z01DeadWeight/receipts/runs/battery-slim.out` | 161 | identical to `X01ReplayC1/replay-battery-stdout.txt` (sha `60916c85…`) |
| D9 | `X03CleanEnv/receipts/` content dedup | 3,841 of 5,452 | 62 files = 8 blobs; 21 copies of one 98-B output, 20 of one 99-B output, 16 empty stderr. Proposal: keep one copy of each content + a `scenario\tsha256\texit` TSV |

**Total 503,476 B (36.4 %).** Every candidate is replaced by an *existing* authority (a git object,
`dispatch.json`, or the wave-root receipt), so none introduces a second convention.

Two more are derivable but I recommend **retaining**:

- `V02StaleLesson/append-only-audit.json` (58,874 B) — re-running `tools/append-only-audit.py --json --to
  efc6b3ec` reproduced sha `dbc791ee…` and exit 1 exactly. It is regenerable today, but it is the claim's
  only locally readable witness if history moves; keep (or regenerate, never hand-edit).
- `w1/spec.json` (53,625 B) — 46,683 B (`items`/`role`/`axes`) equal `dispatch.registry.members`; only the
  3,091-byte wave `context` is unique. Splitting context out and projecting items from dispatch removes the
  duplicate authority without losing the prompt text.

## 5. Defects found (with proposed fixes)

- **F1 — the battery cannot be replayed from outside the lane.** `tools/round56-env-leg-battery.py:10-14,37`
  hardcodes `LANE=/home/vgpnk/Projects/shokunin/kama-shokunin`, `OUT=<lane>/.ufo/waves/round-56/measured`,
  and scratch `/fast/scratch/hyaku/kama-r56/l1-battery`. An external replayer either writes into the
  read-only lane and overwrites the adjudicated receipts (new pids) or must patch the file — X01ReplayC1 did
  the latter. Fix: `--lane`/`--out` arguments, defaulting to the script's repo root; never rewrite receipts
  on a replay run.
- **F2 — the receipts the frozen C1 target names are untracked.** `git ls-tree -r efc6b3ec --
  .ufo/waves/round-56/{measured,census}` is empty; `measured/`, `census/`, `w1/` are `??`. Only `controls/`,
  `preregistration.json` and the two source HTMLs are committed. The untracked S01 manifest is the only
  digest record, and it is itself untracked. Fix: include `census/start.out` and `measured/*.out` in a freeze
  commit, or freeze their sha256 in `preregistration.json` (the census copy is non-derivable after the
  registry grew).
- **F3 — exit-line conventions are inconsistent.** `measured/*.out` (C1) get `exit=` appended by the battery;
  `measured/build-c2.out` has **no** `exit=` (X08's checker reports `missing-field:exit`); `controls/base-c2.out`
  has an operator-appended `exit=1` that the checker never prints. No replayer can tell tool output from
  wrapper append without reading the producer. Fix: counters emit their own exit line.
- **F4 — `w1/validate.out` is not a validation output.** It is byte-identical to `w1/dispatch.json`
  (115,671 B), so the wave has no validation verdict at all, under a name that says it does. Fix: delete the
  copy and have the validator write its verdict, or rename to `dispatch.copy.json`.
- **F5 — the kill mutant has no frozen digest.** The prereg freezes the counter (`fc3d4b63…`) and the checker
  (`c7b0d787…`) but describes the mutant only in prose. Reproduction from prose + diff is exact
  (`a3faaf6e…`), but drift (whitespace, anchor choice) would not be detected. Fix next round: freeze the
  mutant sha256, or freeze the diff blob id.
- **F6 — evidence "identity" is claimed at byte level where only fields survive.** See §3. X01ReplayC1's
  `diff_exit=0` needs normalisation + sorting; the C2 control receipt needs the operator line separated from
  tool output. Not a falsifier of any frozen target — a calibration defect in how the evidence is described.

## 6. Preserved contract

- Prereg bytes at `efc6b3ec` and in the worktree: both `fa4b5a10…` (unchanged; the roster, predicate, target,
  kill rule and counter digests were not touched).
- Frozen digests re-measured: counter `fc3d4b63…`, checker `c7b0d787…` — equal to `claims.C1/C2.counter_sha256`.
- C1/C2 field outcomes reproduce exactly (exit 1/0, `met=False`/`met=True`, three C1 legs as frozen).
- Lane untouched: `HEAD=efc6b3ec…` before and after; the only tracked modifications are the three
  pre-existing ones (r55 `J2RowCap` pair and `SCORECARD.md`); the only untracked wave paths are the six
  pre-existing ones. No `git add/commit/reset`, no jj write, no `/tmp` use, no tool installs
  (`tool_installs: []` unchanged). Scratch `/fast/scratch/hyaku/kama-r56/Z02EvidenceLean` removed after the
  runs.

## 7. Tradeoffs and limits

- Deleting D1 costs in-place grep of the base registry (replacement: `git show <base>:corpus/SOURCES.md |
  grep`); D2 costs a direct counter path (replacement: apply the 673-B diff); D3/D4 cost the cited filenames,
  so five reports need repointing; D9 costs one-file-per-scenario greppability (mitigated by the TSV).
- I did **not** run the committed battery against its default paths, precisely because F1 would overwrite
  the adjudicated receipts. The battery's behaviour under the 2-line path rebind is what I verified; other
  path assumptions in it are untested by design.
- No symbol-level death proof was needed: no code deletion is proposed here, only evidence whose identity or
  derivability is proven by bytes (`cmp`, sha256, clone rebuild). The `lsp` device is not part of this
  evidence argument.
- The census copy, the r55 manifest and the three C2 copies are *not* claimed stale or wrong — only
  redundant or derivable. Nothing is judged about whether C1/C2 are met; that is the verifier's call.
