# kama round 78 — frozen claims

Frozen before any seat scored. Base revision `c62ffd3aea930b98375f805cc3dfb821a703148b`
(lane `master`, == `origin/master` at freeze; read with `git -C <lane> rev-parse master` —
git HEAD is detached). A rule changed after a seat has scored is not this claim's rule
(kumitate r42): a seat that disagrees reports a disagreement and never edits this file. The
predicate sentence, the counter code and the receipt label are the same sentence in all three
places.

Carry-in: the round-77 non-author closure (`corpus/lessons/round-77-verifier-spotcheck.md`)
routed nine defects (§5). D1 (gate registry row stale: eight arms, `arms=8`, `pass=18`),
D2 (no gate run at the tip), D3 (the `append-exempt-class` capability row still rests on a red
tool), D4 (two round-77 knowledge entries have no coverage-map row), D5
(`register-cutoff-split.md`'s `source:` cites no `S###` row), D6 (C2 predicate/ruling wording),
D7 (registers read from the worktree), D8 (same-commit growth hole) and D9 (two stale pointers)
are duties and kill-rule inputs, not additional claims: D1/D5/D9 ride C1's corrections, D4 rides
C1's F6, D7/D8 ride C2's `out_of_population` rule, D2 is the L1's end-of-round gate run, D3 is
a SCORECARD marking, D6 is restated in C2's predicate below without rewriting round 77's text.

Axes: assigned axes are operability + calibration (`shokunin.conf` kama row; the `MISSION.md`
freshness wording conflict stays open at `.ufo/l0-questions.md:145`). Calibration **7** is the
lane's lowest non-retired assigned score (operability 8), so **C1 satisfies the lowest-axis
duty**. C2 freshness and C3 operability are the other two axes the lane owns; two claims on one
axis would count as one claim, so the three claims name three distinct axes.

Causal separability: C1 reads the round-77 self-record sentences and the round-77 knowledge
entries; C2 reads `tools/append-only-audit.py` output plus the two registers and the contract;
C3 starts a lane-owned child and runs `tools/kama-probe.sh check`. Each counter exits 0 with the
other two tools absent from the tree.

Pre-freeze measurements (committed under `.ufo/waves/round-78/measured/`):

- `before/c1-facts.out` — `SELFRECORD_R77_ENUM claims=6 stale=4`, exit 1 (F3, F4, F5, F6 stale).
- `before/c2-append.out` — `APPEND_REGISTERS ... events=248 ... exempt=56 ... unaccounted=3`,
  exit 1, at `--to c62ffd3a…`.
- `before/c3-noserver.out` — `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, exit 2.
- `control/c3-feasibility.out` — the reachability run of the same three-row scratch registry
  against the pinned child: `registry_rows_evaluated=3 model_ok=1 drift=2 exit=2`.

## C1 — calibration: the round-77 self-record's six declared facts re-derive or are answered by measured value-bound corrections

Motivating evidence, measured at the base revision before freeze (`before/c1-facts.out`): four
of the six facts of the round-77 self-record do not re-derive from the tree. F3: `SKILL.md`'s
pre-report-gate row still declares **eight arms**, `arms=8` and `pass=18`, while the landed gate
module's `ARM_SPECS` carries nine arms including `round77-instruments` and its round-77 receipt
prints `PRE_REPORT_SELFTEST pass=22 fail=0`. F4: `SCORECARD.md:4379` points the C3
predicate/ruling divergence at `corpus/lessons/round-77.md` §Mistakes 4, which is the mutating-git
breach; the divergence is §Freeze divergences item 3. F5/F6: of the two knowledge entries round
77 added, `register-cutoff-split.md` cites no `S###` row in `source:`, and neither entry has a
coverage-map row in `corpus/README.md`.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round78-selfrecord-round77.py --repo <lane>` prints one
> `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0` line and exits 0 only when each
> of six declared facts of the round-77 self-record re-derives from the tree — F1 the `## Axes`
> score vector equals the record's declared vector `operability 8, freshness 8, depth 7,
> coverage 9, calibration 7, adjacency 7`; F2 the canonical capability table carries 34 data
> rows and its highest first-working round is 77; F3 `SKILL.md`'s pre-report-gate row names the
> same arms as the gate module's `ARM_SPECS` (including `round77-instruments`), carries that
> count's `arms=` token and the self-test tally of the round-77 gate-selftest receipt; F4 the
> round-77 C3 freeze-divergence sentence names `corpus/lessons/round-77.md` §Freeze divergences
> item 3; F5 every knowledge entry added by round 77 carries a `source:` line citing at least
> one `S###` row id; F6 every knowledge entry added by round 77 has a coverage-map row in
> `corpus/README.md` — and each fact that does not re-derive is answered by a committed
> correction block naming the fact id, the old value re-derived at the sealed revision
> `6c1550a14babaca092cfcc3106f792d695652200`, the new value and the date; it exits 1 naming
> `SELFRECORD_R77_FINDING <mismatch|unbacked|cheat> <fact>` for a non-re-deriving fact with no
> valid correction, a correction whose stated new value does not re-derive, or a graded fact
> whose ground the counter ignores; and 2 on could-not-evaluate (missing self-record or lesson,
> unreadable gate module, CLI misuse).

- Scope rulings declared here, before data: (a) the sealed revision is the round-77 tip
  `6c1550a14babaca092cfcc3106f792d695652200`, not the base, because the record's own values
  were written there; (b) `corrected` counts facts, not correction blocks: two blocks naming one
  fact are one correction and the second is reported `duplicate`; (c) F3's self-test tally is
  read from the round-77 committed receipt `measured/after/gate-selftest.out`, never by running
  `pre-report-gate.py` (seat rule); (d) the correction blocks live in `SCORECARD.md`
  §Round 78 §Corrections and in `corpus/lessons/round-78.md` §Corrections — the counter reads
  both and grades one block per fact.
- Counting command: `python3 tools/round78-selfrecord-round77.py --repo .`
- Before → after: exit 1 `SELFRECORD_R77_ENUM claims=6 stale=4` → exit 0
  `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0`.
- Kill rule: `cheat-constant` (a counter printing the target line regardless of tree state),
  `stale-uncorrected` (one sealed value reverted in a scratch clone), `correction-wrong-value`
  (a correction stating a value that does not re-derive), `unbacked` (a correction naming the
  right value with no derivation of the old one), `pointer-wrong` (F4 pointing at §Mistakes 4)
  and `duplicate-correction` must each be red.
- Control that skips the claimed work: the landed counter on a scratch clone with the four
  repairs reverted prints `SELFRECORD_R77 claims=6 mismatches=4 corrected=0 unbacked=0` and exits
  1 (`measured/control/c1-norepair.out`). A do-nothing round cannot reach the after line.

## C2 — freshness: every base audit event is accounted once at the live tip, and register rows outside the audited population change no bucket

Motivating evidence, measured at the base revision before freeze (`before/c2-append.out`): the
round-77 counter at the base revision prints `APPEND_REGISTERS to=c62ffd3a… events=248
accepted=53 exempt=56 permitted=28 out_of_region=4 restored=99 disclosed=5 unaccounted=3
accepted_cutoff=10f37171… exempt_cutoff=c2aa7fb2… introductions=1/1 rotation_safe=1`, exit 1,
with three `APPEND_REGISTERS_FINDING unaccounted` lines for the round-77 SCORECARD deletions
(`05a03980`, `0fca5e18`, `21458716`; each `ungraded` in the audit, deleted lines inside the
contract's exempt-head regions). The round-77 command was frozen at `--to cc6e1d3c`, so the
round-76 and round-77 events were never inside its population (round-77 routed defect D7).

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round78-append-registers.py --repo <lane> --to c62ffd3aea930b98375f805cc3dfb821a703148b`
> prints one `APPEND_REGISTERS to=c62ffd3aea930b98375f805cc3dfb821a703148b events=248
> accepted=<a> exempt=<x> permitted=<p> out_of_region=<o> restored=<r> disclosed=<d>
> unaccounted=0 introductions=1/1 rotation_safe=1` line and exits 0 only when every deletion
> event the append-only audit reports at that revision sits in exactly one of the six buckets
> (their sum equals `events`), each bucket row is committed at the audited revision or earlier,
> register rows naming an event commit that is not ancestral to the audited revision are counted
> on a separate `APPEND_REGISTERS_OUT_OF_POPULATION rows=<n>` line and change no bucket, the two
> register files' sha256 prefixes are printed on a separate `APPEND_REGISTERS_REGISTERS
> exempt=<hex12> accepted=<hex12>` line, and rotation detection rejects a reintroduced path
> carrying new rows; it exits 1 naming `APPEND_REGISTERS_FINDING
> <missing-row|wrong-count|wrong-class|inside-region|out-of-population|rotation-reintroduced|uncommitted>
> <detail>` otherwise, and 2 on could-not-evaluate.

- Scope rulings declared here, before data: (a) admissibility of an **event** is ancestry to the
  audited revision (round 77's ruling (a) restated; round 77's predicate wording "under that
  register's own introduction cutoff" is superseded by C2's own sentence and its text is not
  rewritten — routed defect D6); (b) **register** introduction is separate provenance: each
  register's first commit is discovered from history, a reintroduced path with new rows fails
  `rotation-reintroduced`, and the read is the committed blob at the audited revision, never the
  worktree (routed defect D7); (c) a row committed in the same commit as the damage it blesses
  is rejected when the row's named event is not ancestral to that commit (routed defect D8);
  (d) `permitted` and `out_of_region` keep round 77's `permitted == deleted`-with-zero-graded
  and every-deletion-outside-all-declared-regions readings, unchanged.
- Counting command: `python3 tools/round78-append-registers.py --repo . --to c62ffd3aea930b98375f805cc3dfb821a703148b`
- Before → after: exit 1 `events=248 … unaccounted=3` → exit 0 `events=248 … unaccounted=0` with
  the bucket sum equal to `events`.
- Kill rule: `missing-row`, `wrong-count`, `wrong-class`, `inside-region`, `rotation-reintroduced`,
  `out-of-population-row` (a row naming an event after `--to` must leave every bucket unchanged)
  and `uncommitted` (a worktree-only row) must each be red.
- Control that skips the claimed work: the landed counter on a scratch clone with the three new
  register rows removed prints `unaccounted=3` and exits 1 (`measured/control/c2-norows.out`).

## C3 — operability: the lane's reconciliation verdict is exercised end-to-end against a live pinned llama.cpp child

Motivating evidence: the three registered consumers have sampled `DEAD` since 2026-10-14 and the
lane's verdict path (`MODEL_OK` / `MODEL_MISMATCH` / `DEAD`) has never been exercised against a
live server in-repo, only against parser fixtures. The pinned child, model and probe are all
present on this host (round-71 re-derivation; `before/c3-noserver.out` shows the same scratch
registry without a server at `model_ok=0 drift=3`). The reachability run before freeze
(`control/c3-feasibility.out`) prints `registry_rows_evaluated=3 model_ok=1 drift=2 exit=2`
against `~/.local/opt/llama-b11755/llama-server` and `~/.cache/kama-shokunin/models/stories260K.gguf`.

**Predicate (frozen, verbatim — the same sentence is the module's `PREDICATE` constant and the
receipt label):**

> `python3 tools/round78-live-reconcile.py --repo <lane>` prints one `LIVE_RECONCILE rows=3
> model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp served=stories260K` line and exits
> 0 only when it starts the pinned `llama-server` (binary and model sha256 recorded) as a child
> on a loopback port that is neither a registered consumer port nor currently listening, writes
> a three-row scratch registry under its own scratch root — a row whose expected id normalises to
> the served id, a row whose expected id does not, and a row naming an unserved port — runs
> `bash tools/kama-probe.sh check --registry <scratch>` and observes `MODEL_OK` on the first,
> `MODEL_MISMATCH` on the second and `DEAD` on the third, requires the live row's probe evidence
> to name `runtime=llama.cpp` and the served id to be the pinned fixture model, refuses any
> registered consumer port before probing, tears the child down and writes a receipt carrying the
> child's exit status; it exits 1 naming `LIVE_RECONCILE_FINDING <class> <detail>` when a verdict
> differs, when a responder without llama.cpp runtime evidence reaches `MODEL_OK`, or when a
> registered port was probed, and 2 on could-not-evaluate (pinned binary, model or probe absent;
> CLI misuse).
- Scope rulings declared here, before data: (a) the child is the lane-owned fixture class of
  rounds 16/17/18/61/63 (unregistered loopback port, torn down in the run, no unit, no
  `~/.config`, `~/.omp` or systemd write), still pending L0 ratification for the class; (b) the
  scratch registry is evidence, not a registry row: `registry/endpoint-consumers.tsv` is
  untouched and the three registered consumers keep their recorded `DEAD` state; (c) the counter
  is a trial instrument, not a readiness gate for configured consumers.
- Counting command: `python3 tools/round78-live-reconcile.py --repo .`
- Before → after: `registry_rows_evaluated=3 model_ok=0 drift=3 exit=2` (no server) → the
  `LIVE_RECONCILE` line, exit 0; the graded probe line `registry_rows_evaluated=3 model_ok=1
  drift=2 exit=2` is carried in the receipt.
- Kill rule: `fake-responder` (a plain HTTP responder serving the same `/v1/models` JSON without
  llama.cpp runtime evidence must not reach `MODEL_OK`), `registered-port` (a registry naming
  8080 or 34113 is refused before any probe), `wrong-expect` (the matching row must be
  `MODEL_OK`, the mismatching row `MODEL_MISMATCH`), `no-teardown` (a receipt without the child
  exit status is red).
- Control that skips the claimed work: the same three-row registry with no server prints
  `model_ok=0 drift=3 exit=2`; the counter cannot print its line without starting the child.

## Frontier step (not a claim)

Census before → after with `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate
--root /home/vgpnk/Projects/shokunin kama` (before: exit 0, 290 rows — A 275 / B 11 / C 4,
mined 261, queued 8, rejected 21). One own-work row is admitted for the instrument class C2
extends and one external candidate is opened and decided; the round lesson carries the Gate
block, value-bound corrections, `## Mistakes` and the attack dispositions. `merge/kama/` is
read-only: the id-collision guard and the quarantine slice are re-derived this round, and
`Assimilation: none` unless an entry clears PROVINCE/QUALITY and a fresh census mirror. One
`considerthese/2026-10-26.md` proposal (proposals 1 or 3) lands as a QUALITY criterion citing
the file and date, or the report says why not.

## Seat plan (frozen with the claims)

ONE v1 wave of 12 seats: 3 executor (C1, C2, C3), 3 scribe (knowledge/sources, lesson/QUALITY,
SKILL+README duties), 1 scout (independent re-derivation + routed-defect status), 1 connector
(sibling overlap + assimilation guard), 1 reviewer, 2 critic (one falsifies the counters, one
runs the do-nothing controls with the landed counters), 1 mutation-tester. Attack 4/12 = 33 %.
