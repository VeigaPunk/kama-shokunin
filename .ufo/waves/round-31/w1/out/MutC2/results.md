# MutC2 — five SCORECARD mutations against the frozen C2 counter

Claim served: C2 (calibration), fail-capability of the instrument. Mutation-tester seat, round 31 wave 1.
I did not judge the contract, did not edit the counter, and did not touch any tracked lane file.

## Setup

- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, frozen `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`.
- Scratch clone: `/tmp/r31w1-MutC2` (fresh `git clone --no-hardlinks`, checked out at `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`).
- Counter bytes used read-only from the lane: `.ufo/waves/round-31/count-c2.py`,
  sha256 `2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe` — equals preregistration `C2.counter_sha256`.
- Command shape (every run):
  `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c2.py --repo /tmp/r31w1-MutC2 --tip <rev> [--list] --out /tmp/r31w1-MutC2/<receipt>.json`
- Counter exit code was `0` (evaluated) in every run below; it never exited `2`.

## Baselines (a failing baseline makes a mutant inconclusive, so a met-True baseline was built first)

Pristine `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` (SCORECARD.md sha256 `73a3270dc89b529300f73f380a658c42938d58e5dbb44e46ef885162eb000083`):

```
rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 0e6f8ed6891c
```

All 13 problems are `p1:no-revision`. A mutation on this tip can only ever print `met False`, so the five
mutations were applied to a repaired baseline R (one commit, append-only, the RefRepair-by-design shape):
`716cec45648a26fb321c5f9c9d9639ad8c53337c` appends `## Round 31 — claim-row evidence corrections`
with **11** rows of `| CR31:n | <id> | p1 | p1:no-revision |`:

```
rows 28 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True tip 716cec45648a
```

Eleven rows, not thirteen, because row ids repeat: id `C1` names three distinct failing rows
(lines 266, 320, 379) and the counter's correction key is `(row id, class)`, not the row. One correction
row therefore discharges three claim rows — see finding F3. This is also why R is the *strongest*
baseline the repair protocol can produce (finding F4 shows the literal 13-row protocol fails).

Each mutation is exactly one commit on its own branch from R; the working tree was returned to pristine
bytes after the last run.

## The five mutations

### M1 — delete one claim row from a table (caught)

Commit `65c0f2da1e9ff0ea190f044937fc3f63398580a8`. Deleted the Round-20 row
`| C1 finite named error regressions | ... |` (line 900), a row that passes at R.

```
rows 27 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only False met False tip 65c0f2da1e9f
```

- Expected detector: population floor `rows >= 28`.
- Observed: `rows 27`, no new per-row problem (`base_mismatched` 13 unchanged, `unresolved 0`).
- Verdict: **caught**, by the `rows` term (and `append_only` also went False, since the edit is in place).
  No fail-capable per-row class is involved.

### M2 — measured-commit token changed to a non-existent hash (caught)

Commit `e9910e4a08fa17fdc8b1cc69d4647c1ce6dd7529`. Round-25 row
`C2 (learning claim, frontier K05)` (line 1261), measured-commit cell `receipt 5c95c8f1...e51f8604`
→ `receipt deadbeefdeadbeefdeadbeefdeadbeefdeadbeef`. This row's only hex token was that measured
commit, so no fallback token could satisfy P1.

```
rows 28 base_mismatched 14 exempt 1 valid_corrections 11 false_corrections 0 unresolved 1 append_only False met False tip e9910e4a08fa
```

- Expected class: `p1:no-revision`.
- Observed (from `--out`): `{"row": "C2 (learning claim, frontier K05)", "line": 1261, "round": "25", "class": "p1", "observed": "p1:no-revision"}`.
- Verdict: **caught**, expected class fired.

### M3 — one row's evidence pointed at a path that does not exist (caught only by append_only; P2 did not fire)

Commit `e756d9d4a56c89eafa3a545b5c7a5f567742fb65`. Round-30 row `C1 (measured)` (line 1537):
the whole evidence cell (`c1/before/c1-base.out`; `c1/before/c1-r29-tip.json`; `final/c1-tip.out`;
lesson `corpus/lessons/round-30.md`) → `.ufo/waves/round-30/evidence-does-not-exist.md`.

```
rows 28 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only False met False tip e756d9d4a56c
```

- Expected class: `p2:no-evidence-path`.
- Observed: **no problem at all for line 1537**; `base_mismatched` stayed 13, `unresolved 0`.
- Verdict: **caught** (`met False`) but the catch is `append_only=False` only. The P2 rule itself did not
  fire: the row still names the counting-command script `.ufo/waves/round-30/count-c1.py` (and
  `final/c1-tip.json` in its measured-commit cell), and P2 accepts *any* existing lane path anywhere in
  the row. As a rule, P2 survived this mutation. Probe P2a (below) shows the same defect passing outright
  in append-only space.

### M4 — pinned counter sha256 replaced by a wrong full digest (caught)

Commit `480b2b240cfdb585b8bb60144955cd19676e42c8`. Round-30 row `C1 (measured)` (line 1537) pins the
round-30 counter digest `c3f16ef1…9ce40d`; replaced with 64 zero hex digits
(`0000000000000000000000000000000000000000000000000000000000000000`).
The blob at the row's resolved revision `fdf8cda1` hashes to the original pin
`c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`, so the check was live.

```
rows 28 base_mismatched 14 exempt 1 valid_corrections 11 false_corrections 0 unresolved 1 append_only False met False tip 480b2b240cfd
```

- Expected class: `p3:digest-mismatch:<path>=<actual>`.
- Observed: `{"row": "C1 (measured)", "line": 1537, "round": "30", "class": "p3", "observed": "p3:digest-mismatch:.ufo/waves/round-30/count-c1.py=c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d"}`.
- Verdict: **caught**, expected class fired with the exact observed digest.

### M5 — duplicate a claim row id, in place (caught only by append_only; no duplicate-id rule exists)

Commit `59a49b4f742ce0028bbbcc1c54fa0739f9be7d24`. The Round-20 row
`C1 finite named error regressions` (line 900) copied verbatim directly beneath itself.

```
rows 29 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only False met False tip 59a49b4f742c
```

- Expected detector: none exists in the counter — there is no duplicate-id check and `rows >= 28` is a
  floor, not a population equality. Both copies pass P1/P2/P3 independently.
- Observed: `rows 29`, both copies resolved, `unresolved 0`; only `append_only` is False.
- Verdict: **caught** (`met False`) **by the append-only gate alone**. The duplicate-id rule is absent, so
  the defect form survives the guard whenever the copy is append-only (M5b).

## Supplementary probes (not one of the five; each one commit, labelled)

### M5b — identical duplicate, appended so `append_only` stays True: SURVIVED (defect)

Commit `b4c02de208668054be1b768661625c9b3c2d0afd`: a new `## Round 31 probe — appended duplicate claim
table` inserted after the base bytes and before the corrections heading, containing the Round-20 row
verbatim (same id).

```
rows 29 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True tip b4c02de20866
```

- Verdict: **survived** (`met True`). A claim row id can be duplicated and both copies count; the
  `rows >= 28` floor is satisfiable by padding with a copy. Defect to report (F1).

### P2a — appended *new* claim row with a dead evidence path and a live counter: SURVIVED (defect)

Commit `b339e2e9396c6ab1e01c206c2721c128c56bd1db`: new appended table with row
`C1 probe-dead-evidence`, evidence `.ufo/waves/round-31/evidence-absent.md` (absent), counting command
`python3 tools/error-verdict-census.py ...` (present), P1 token `37bd4c5` (resolvable ancestor).

```
rows 29 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True tip b339e2e9396c
```

- Verdict: **survived** (`met True`). P2 is satisfied by the counting-command path, so an evidence pointer
  that does not exist is never a failure while the row names its counter. Defect to report (F2).

### R13 — the literal repair protocol (one correction row per failing claim row): FAILS

Commit `bd533bf4b8c98be96736c3803d9e5efb9a380a1a`: R with 13 correction rows, i.e. one per failing row as
preregistration `C2.claimed_work` says (three `C1` rows, so three `C1` correction rows).

```
rows 28 base_mismatched 13 exempt 1 valid_corrections 9 false_corrections 5 unresolved 4 append_only True met False tip bd533bf4b8c9
```

- Observed: the duplicated `(C1,p1)` and `(C2,p1)` keys make every duplicate a `false_correction`
  (5 = 3+2), and the four affected problems stay unresolved. The 11-row deduped repair is the only shape
  that prints `met True`.
- Verdict: not one of the five mutations; recorded because it shows the repair instruction as written
  cannot satisfy the predicate. Defect to report (F3/F4).

## Instrument findings to report (survivors are coverage findings, not permission to change the contract)

- **F1 — duplicate ids are invisible.** No duplicate-id check; `rows` is a floor. An appended copy of an
  existing claim row yields `met True` with 29 rows and one phantom row of population (M5b).
- **F2 — P2 is subsumed by P3/paths elsewhere in the row.** P2 passes on any existing path token in
  `row_text`, including the counting-command script and the measured-commit cell. A dead evidence pointer
  is undetectable for any row that carries a live counter (M3 shows the class never firing; P2a shows the
  defect passing in append-only space).
- **F3 — correction keys are row-id strings, not rows.** Three distinct Round 11/12/13 claim rows share id
  `C1`; one `| ... | C1 | p1 | p1:no-revision |` correction row resolves all three (observed in R:
  `valid_corrections 11`, `unresolved 0` over 13 problems). "Exactly one VALID correction row per row"
  cannot be enforced per distinct row.
- **F4 — the instruction "one correction row per failing claim row" fails its own counter** (R13:
  `false_corrections 5`, `unresolved 4`, `met False`). A repair seat must discover the dedupe rule, which
  is not stated in the preregistration.
- **Not a finding:** M1/M2/M4 are genuinely fail-capable for their targeted terms; M3/M5 were caught only
  by `append_only`, so no credit for P2 or duplicate detection accrues from them.

## Before/after hashes (SCORECARD.md only)

| rev | commit | blob sha1 | sha256 |
|---|---|---|---|
| pristine | `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` | `21203e66c4a468a093998ccdc5cb57c470b5b9e2` | `73a3270dc89b529300f73f380a658c42938d58e5dbb44e46ef885162eb000083` |
| R | `716cec45648a26fb321c5f9c9d9639ad8c53337c` | `e1c5efdbc112e97af7cfbb5ad372c0a34eb8b3ca` | `dddb95bbf5a34ac465beeb9508826b465e2d164d68c045eab63ab6b909fd8cc1` |
| M1 | `65c0f2da1e9ff0ea190f044937fc3f63398580a8` | `24e024202ab716e8db4c4e71360a075f98012647` | `94f69dbdc77822df7eb78909c664aba1031b51f9f8de848bb4d4e99543152492` |
| M2 | `e9910e4a08fa17fdc8b1cc69d4647c1ce6dd7529` | `b63b899135cb1014d7e0b0b46343517da53220c2` | `a33c41df731cafedc0b108d6f9fb76bf7fa86ffddc338e0aef5e78e71e4a8226` |
| M3 | `e756d9d4a56c89eafa3a545b5c7a5f567742fb65` | `6bed43b7ed746cf295e36243bef0fe5d6848f6be` | `638eaeedec3defaccd27ffefdeeaf77543b599c7bfc6aacb32bcb0bf3d3ec414` |
| M4 | `480b2b240cfdb585b8bb60144955cd19676e42c8` | `67881f7eddc4ad4a3ec0102a953e765727068bb0` | `341258a66380c3f328f4e1d70fa4cda0d1bb3b32af5bad83c1147f794cfb586b` |
| M5 | `59a49b4f742ce0028bbbcc1c54fa0739f9be7d24` | `d6cd526552e8b53dd6a103e1bd2ac278592c8355` | `9e5a2510ec8b26e35565c2e145f9655e9988d62514400fcb00839978ee3070de` |
| M5b | `b4c02de208668054be1b768661625c9b3c2d0afd` | `f6bbc13db28bf8a310e7e5d1f5f74d5e94415978` | `11401d2a217aa0baae84f518927d0bcae47496bd7defa12b6c188e800487070c` |
| P2a | `b339e2e9396c6ab1e01c206c2721c128c56bd1db` | `a52b963a4d644aabd883f4bb0bc1b7792bfd4aaf` | `280d05266dd2d1ff22405004fcfd1215fede7490a301add26c01f9bf8c5e46f1` |
| R13 | `bd533bf4b8c98be96736c3803d9e5efb9a380a1a` | `c674ed7c014b92a203748a4a6173b811fd146933` | `322fcde9ec67328ded083000e830bf7b20ce3aca73076b77547d397bc765cac0` |

Receipts per run: `/tmp/r31w1-MutC2/r31-c2-{pristine,R,M1,M2,M3,M4,M5,M5b,P2a,R13,restored}.json`.

## Restoration evidence

- `git -C /tmp/r31w1-MutC2 checkout 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` → HEAD `0e6f8ed...`,
  `git status --porcelain` shows only the untracked receipt JSONs in the scratch root (no tracked diff).
- `sha256sum /tmp/r31w1-MutC2/SCORECARD.md` = `73a3270dc89b529300f73f380a658c42938d58e5dbb44e46ef885162eb000083`,
  identical to the frozen pristine blob; blob sha1 `21203e66c4a468a093998ccdc5cb57c470b5b9e2`.
- Counter rerun on restored bytes reproduces the pristine line byte for byte:
  `rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 0e6f8ed6891c`.
- No lane file was edited; no git command ran in the lane; no server or port was used; no installs.
  The frozen counters `.ufo/waves/round-31/count-c1.py` and `count-c2.py` were only read (sha256 above).

## What the L1 must not trust

- Do not read M3 or M5 as evidence that P2 or duplicate detection works: both fell to `append_only` only.
- Do not land a repair with one correction row per failing row (13 rows): that shape prints `met False`
  (`false_corrections 5`, `unresolved 4`). Only the 11-row dedupe meets, and it certifies three distinct
  `C1` rows with one correction.
- Do not treat `met True` from the repaired baseline as per-row evidence: F1/F2/F3 let padding,
  dead evidence pointers and id-collapsed corrections pass the frozen predicate unchanged.
