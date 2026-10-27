# V4Receipts — round-55 receipt audit (kama, w1)

**Verdict:** every printed number in `controls/*.out`, `measured/*.out` and
`c1/battery/*.out` re-derives (C2 reproduced byte-identically and exit-code-exactly
from an own clone; C1 re-derives structurally against the frozen counter code, the
frozen `HOST_LIBS` set, `readelf` on the host install and the `SOURCES.md` git diff)
— with one disclosed freeze-contract defect (F1, MEDIUM), one cosmetic receipt-prose
mislabel in the frozen counter (F3, LOW), and two stale receipts that were in the
frozen receipt dir at audit time and were removed by commit `c2c05e30` mid-audit
(F2, resolved; evidence preserved).

## Audit state

- Lane HEAD during audit: `8abadfed` → integration `c2c05e30` → `bf336baa` while
  this report was being written; findings below mark which state each applies to.
- Frozen preregistration `.ufo/waves/round-55/preregistration.json`: committed once
  in `9c60eae6` (only commit touching it), identical in worktree — freeze intact.
- Counter bytes (kill-rule condition): `sha256sum` of both worktree files AND both
  blobs at `9c60eae6` = preregistration `counter_sha256` for C1
  (`c81fe971…579af`) and C2 (`d70a1729…26510c`) — unchanged at HEAD `bf336baa`.

## Re-derivation evidence

**C1** (`tools/round54-replay-code-audit.py`; `sha256` verified above):

- Leg booleans and N/3 tallies are the conjunction at `:954` with the print at
  `:955-959`; every receipt carries exactly three per-run groups (b1-b3) of
  bind/sealed/code/envnames/twopass/rehash detail lines — counted, consistent.
- `8 archive files` = `len(cobs['files'])` (`:791`); the printed list is the
  `sorted` basenames of that same set (`:794`) — identical in every passing
  receipt, matching the 8 libs the server maps; `REQUIRED` (`:135`) members all
  present.
- `13 root-owned host files` = `len(host)` where only basenames in the frozen
  `HOST_LIBS` (`:137-143`, exactly 13 names: ld-linux, brotli×3, crypto, c, gcc_s,
  gomp, m, ssl, stdc++, z, zstd) are admitted as host; `host ≤ 13` by construction
  (`:563-566`). `m-ldpreload.out` keeping 13 while `LD_PRELOAD=/usr/lib/libzstd.so.1.5.7`
  is consistent: libzstd is in the set (`:142`), so the preload is an admissible
  mapping and only the name `LD_PRELOAD` fails (`envnames=0/3`, exit 1) — exactly
  the frozen design (runner comment `run-battery.py:30-33`).
- `newrow`: `newrow_leg` (`:863-873`) counts SOURCES.md lines at --tip absent at
  BASE `3a600d2f` and matches `GITDOC_URL` (`:130`). `git diff 3a600d2..9c60eae`
  shows exactly 2 added lines (re-written S510 `used-by` row + new S511 row), and
  only S511's URL contains `git-scm.com/docs/git-config#…GITCONFIGCOUNT` →
  `2 rows new since base; 1 name the git environment doc: ['| S511 |']` re-derived.
  At base run tip=base → `0`/`[]` ✓. (`ln[:8]` explains the `| S511 |` print.)
- `anon=0`, `teardown` (invoker SIGKILLed, port refuses, KILL_WAIT=30s at `:152`),
  `seals 15` = `SEALS` (`:145`), `envnames` 5 (clean) / 6 (mutant-injected
  LD_AUDIT) / failure line (m-ldpreload) — all internally consistent; `anon` counts
  anonymous exec maps rows (`:516-518`, `:826`).
- pids/ports/inodes/nonces: per receipt b1<b2<b3 pid ordering holds; all nonce
  strings (`kama witness <16hex>`) and memfd inodes are distinct across receipts —
  no duplicated evidence. Controls' server pids (1175488+) < build's (1188271+) —
  consistent with controls-run-before-measurement; the commit history shows it
  structurally too (controls in freeze `9c60eae`, measurements + battery in `8abadfed`).
- Mutant receipts' `tip=` values are fixture commits of the battery's deleted
  scratch clone (unverifiable objects by design; control's `tip=9c60eae` = `FREEZE`
  at `run-battery.py:14` ✓).

**C2** (`tools/round54-cited-path-check.py`): reproduced byte-identically from
`git clone --shared` → `python3 tools/round54-cited-path-check.py --repo $S/lane
--tip <tip> --fleet /home/vgpnk/Projects/shokunin --fleet-rev
6c4aba34c2a22519152d8c6f32e1039eecb1381b`:

- tip run → `diff` vs `measured/c2-build.out`: **identical**; exit 0.
- base run → `diff` vs `controls/base.c2.out`: **identical**; exit 1.
- `cited=693 unresolved=14 disclosed=14` in both runs and receipts — internally
  consistent: `disclosed` counts only non-(fixed/externalized/superseded) rows
  (`:641-642`), so the superseded row leaves it at 14 while removing the drop via
  the `exempt` set (`:646-655`) → base `dropped=1`, build `dropped=0`.
- `scenarios=15/15`: exactly 15 `fixture ok:` detail lines (matches `SCENARIOS=15`
  at `:168`, including the round-55 superseded honest/forged pair at `:773-796`).
- The dropped token ``SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md``
  is EXACTLY the superseded ledger row's (surface, token) at
  `registry/cited-path-corrections.tsv:46` (`…\tsuperseded\tcorpus/lessons/round-53-verifier-spotcheck.md\t…`),
  and the replacement is the cited-at-tip resolving file — the mechanism the
  class exists for.
- Fleet: receipts pin `fleet=6c4aba34…` (receipt field); `--fleet-rev` defaults to
  HEAD, so re-derivation requires the recorded rev — as it should.

## Findings

### F1 (MEDIUM) — frozen battery contract vs delivered battery

`.ufo/waves/round-55/preregistration.json` (frozen, `9c60eae6`):

- `:44` mutants: `m-ldpreload (envnames)`, **`m-ldaudit-writable (code)`**,
  **`m-ldaudit-foreign (hostlibs)`**, `m-member-flip (rehash)`
- `:19` target: *"each named mutant receipt prints met=False (exit 1) with its
  named leg failing"*
- `:20` kill_rule: *"falsified if … any battery mutant prints met=True"*

Committed reality (`run-battery.py`, all receipts at `8abadfed`):

- `m-ldaudit-writable` was never produced by the committed runner (replaced as the
  code-leg kill by unfrozen `m-text-flip`, which does trip `code=0/3`, exit 1).
- `m-ldaudit-foreign` is committed with `kind="vector"` whose pass condition is
  `rc==0 and met` (`:137-138`) — i.e. a frozen **named mutant whose met=True is the
  expected outcome**; its receipt prints `met=True` and `hostlibs=3/3`.
- The hostlibs leg consequently has **no live kill** in the battery (the LD_AUDIT
  injection is void on this glibc — `run-battery.py:54-56`; the vector receipt is
  honest evidence of that).

Read literally the frozen kill rule is tripped (a named battery mutant prints
`met=True`); read by intent the delivered battery deviates from the frozen mutant
list and leaves one leg covered only by vector analysis. `corpus/lessons/round-55.md:95-104`
now records this verbatim and honestly ("not repaired in the frozen
preregistration"), so the defect is *disclosed*, not hidden — severity MEDIUM (it
weakens, not voids, the C1 evidence; the 3 live legs are killed and the met-path
is independently green). Proposed fix text: `fixes/F1-prereg-battery-contract.md`.

### F2 (MEDIUM→RESOLVED) — two stale receipts in the frozen receipt dir at audit time

At HEAD `8abadfed`, the battery dir held `m-ldaudit-writable.out` and
`m-extra-in-tree.out` — both `met=True`, neither producible by the committed
`run-battery.py` (not in `MUTANTS`; pid epochs 1.33M and 225-256K vs the runner's
1.5-1.6M on this pid_max=4194304 host; both committed in the same `8abadfed`).
Integration commit `c2c05e30` deleted both (`D` lines verified) and the lesson
names them as history. Recovered verbatim from `8abadfed` into
`receipts/attic-8abadfed/` for the audit trail. Status/notes: `fixes/F2-stale-receipts-status.md`.

### F3 (LOW) — "(16 executable ranges)" is a summed pass count, not a range count

`tools/round54-replay-code-audit.py:717` sets `cobs["ranges"] =
first["ranges"] + second["ranges"]` — the sum of both observation passes;
`compared` increments once per executable maps row of an archive member (`:537`).
Each of the 8 libs has exactly one R E PT_LOAD (`readelf -lW` on the host install:
8 segments total → 8 ranges/pass), so `16` = 8 ranges × 2 passes. The `twopass`
line's "16 range reads" is the correct label (`:799-800`); the `code` line's
"(16 executable ranges)" (`:791`) overstates the count 2× — prose defect in a
frozen counter; the number itself re-derives. Proposed fix (next freeze only):
`fixes/F3-range-label.diff`.

## Residual risk / verification gaps

- No independent re-execution of the C1 counter was done by this seat: its replay
  lifecycle (archive/model downloads, loopback llama-server, teardown) is covered
  by 10 committed receipts today and by the dedicated rerun seats; this seat
  re-derived every printed C1 number against the frozen code instead. Leftover
  `pgrep -af llama-server` at audit time showed only peer seat J5EnvNames' own
  loopback replay (pid 3523374, port 40863) — not mine, not touched.
- Battery `.out` files record `met=` only; exit codes live in the runner's
  uncommitted stdout summary — exit-code re-derivation is via `:966` mapping
  (documented in the lesson), and my C2 reruns did confirm exit 0/1 directly.
- Mutant `tip=` commits are objects of the deleted scratch clone — unverifiable
  from the lane by design.
- C2 `cited=693` equality across base and build is plausible (drop+add balance)
  and reproduced, but the receipts do not decompose the 693 per surface — the
  counter does not print that breakdown (advisable detail addition, not a defect).
- Two receipt-side `envnames` counts (5 vs 6) are consistent with the committed
  mutants; the removed `m-ldaudit-writable` receipt's `envnames=5` is consistent
  with its injection never reaching the server env — an explanation consistent
  with, not proven by, surviving evidence.
- `pgrep` noise: one earlier `pgrep -af llama-server` line matched my own shell
  command string — noted as a self-match artifact, not a server.
- Out of scope but noted: `.ufo/waves/round-55/census/end.out` (the lesson's
  "round end" receipt) exists now (committed by `c2c05e30`), after my first pass.

## Tooling

No installs or upgrades performed (`git`, `python3`, `readelf`, `sha256sum` —
all already present); pacman not touched per the host-wide pause. No files
written outside `.ufo/waves/round-55/w1/out/V4Receipts{,.md}` and my scratch
`/fast/scratch/hyaku/kama-r55/w1/V4Receipts/` (clone `git clone --shared` for the
C2 reruns; `git rev-parse --show-toplevel` asserted = clone path; no fixture
commits made).

## Files written

- `.ufo/waves/round-55/w1/out/V4Receipts.md` (this report)
- `.ufo/waves/round-55/w1/out/V4Receipts/receipts/` — all 11 audited receipts (copied)
- `.ufo/waves/round-55/w1/out/V4Receipts/receipts/attic-8abadfed/` — the 2 removed
  stale receipts recovered from `8abadfed`
- `.ufo/waves/round-55/w1/out/V4Receipts/receipts/rerun.{c2-build,base.c2}.out` —
  my byte-identical reproductions
- `.ufo/waves/round-55/w1/out/V4Receipts/evidence/` — lane-verify.txt, hist.txt,
  c2-rerun-exits.txt
- `.ufo/waves/round-55/w1/out/V4Receipts/fixes/` — F1 contract text, F3 diff, F2 status
