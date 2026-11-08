# SB01LessonDraft — round-95 lesson body (kama w1, calibration)

Seat `SB01LessonDraft` (scribe, axis: calibration). Lane `kama-shokunin`. Read-only in the lane; the only writes are
this file and my own out dir `.ufo/waves/round-95/w1/out/SB01LessonDraft/`. No delegation, no model choice, no
network beyond read-only GETs of the pinned public URLs, no burners left running (`--burners 0` on every counter run;
the two counter runs I started exited and were reaped).

## Scope

Draft the round-95 lesson body for `corpus/lessons/round-95.md` — the `## Gate` table (one row per NEW source row
S616/S617, plus one REJECTED candidate actually opened) and the `## Mistakes` rows (class · evidence pointer ·
captured-by · fix) mined from this round's own record: the round-94 M5/M6 freeze defects, the 20-file discriminator
that did not discriminate at base until the population was raised, and mistakes in the round-95 plan/counters
themselves. Deliverable for the L1 to integrate: `out/SB01LessonDraft/round-95-lesson-draft.md`.

## Commands and outputs (true exit codes)

- `sha256sum` over 5 downloads (raw S616/S617, both READMEs, the codeload tarball) → `e0e43f22…a973`,
  `7f4d7c35…6b54`, `a5544e6c…c008`, `eafc1b53…a137`, `f50a52f4…ea13` — the tarball digest equals the plan's pinned
  `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`. Exit 0. Receipt
  `out/SB01LessonDraft/digests-and-quotes.out`.
- `cmp` raw download vs the extracted archive member, four files → `cmp exit=0` each (server-context.cpp,
  server-schema.cpp, cli/README.md, tools/server/README.md). Exit 0.
- `sed -n '1489p' server-context.cpp` → `for (int i = 0; i < params_base.n_parallel; i++) {`;
  `sed -n '65p' server-schema.cpp` → `->set_hard_limits(1, params_base.n_parallel)`;
  `sed -n '56p' cli/README.md` → `-np, --parallel N … (default: 1)`;
  `sed -n '194p;1005p;1019p' tools/server/README.md` → `--port PORT … (default: 9931)`, `"total_slots": 1,`,
  `` `total_slots` - the total number of slots for process requests (defined by `--parallel` option)``. Exit 0.
- `git show c798e831:corpus/SOURCES.md | grep -c "^| S[0-9]"` → 355; `grep -c "^| S[0-9]" corpus/SOURCES.md` → 357
  (census before → after 355 → 357). Exit 0.
- `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, 120 `kama` lines, last
  line `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.
- `python3 tools/round95-freeze-audit.py --repo . --rev c798e831` → `receipts=7 present=7 missing=0 tokens=0
  matching=0 cited=17 unresolved=4 met=False`, **exit 1** (S616/S617 unresolved at F). Same command with
  `--plan plans/round-95-amendment-1.md --rev bba10f75` → `receipts=9 present=9 missing=0 tokens=24 matching=24
  cited=14 unresolved=0 met=True`, **exit 0**. `--selftest` → `FREEZE_AUDIT_SELFTEST pass=5 fail=0`, exit 0.
- `python3 tools/round95-router-budget.py --repo . --rev a27656a454b1a2364f8b6e55f42fbca8c2e86ee4 --work <scratch>
  --allow-clock --slow-files 20 --skip-load --burners 0` → `W03-slow-x40 ok=1 … run1=…/46.30s run2=…/58.35s` and
  `cells=10 mismatches=0 positive_mismatches=0 … w03_seconds=58.3`, **exit 0** — the BASE probe is green at twenty
  files, i.e. the "red before" did not exist there. Receipt `out/SB01LessonDraft/base-20-files.out`.
- `python3 tools/round95-router-budget.py --repo . --rev f63256607916cdeb35580a7af315b5f4b54eba18 --work <scratch>
  --slow-files 8 --skip-load --burners 0` → `could-not-evaluate: W03 natural pass 19.0s < 1.2 x 60s`, **exit 2** —
  the margin guard fires as designed below 1.25 × the base constant. Receipt
  `out/SB01LessonDraft/m1-guard-8-files.out`.
- Counter byte-identity F vs HEAD: `git show c798e831:tools/round95-*.py | sha256sum` vs HEAD → identical for all
  three counters. Exit 0.
- `git log --all --name-only -- '.ufo/waves/round-95/**' | grep -i harm` → only `controls/harm-pair.out` (7db1c54a) and
  `controls/harm-tip2.out` (ed3bd05f); `harm-base.out` / `harm-tip.out` exist at **no** revision. Exit 0.
- In-process re-run of the frozen counter's own `sources_status()` on a forged plan citing rejected rows S027/S591 →
  `cited=16 unresolved=0`, i.e. `met` would be True: the `rejected` arm cannot fire (`cells[8]` = opened date, status
  is `cells[7]`). Same for the token arm with every value doctored → `tokens=24 matching=24`, `token_missing: []`.

## Findings

**NOTE-1 — the round-94 M5 defect repeats one class down.** The frozen plan's K2 names "the base harm receipt the M1
commit carries" (`plans/round-95-claims.md:58`) and the measurement-time list names `harm-base.out`/`harm-tip.out`
(:28); neither file exists at any revision (command above). The freeze-time half (7 receipts) IS all present at
`c798e831`, so round 95 fixed the class C3 grades — the ungraded half is the one that slipped. Lesson row M3.

**NOTE-2 — the plan's own cell list contradicts the frozen counter's bytes.** Plan:46 "W03 twenty distinct slow" and
:65 "~50 s of CPU at 20 distinct slow files" vs `tools/round95-router-budget.py:88` `SLOW_FILES = 40` and docstring
:49 "~82 s"; measured W03 is 81.7–99.7 s (`measured/c1.out`, `measured/c1-m1b.out`). The plan is frozen, so this is
recorded, not repaired (amendment 3 NOTE-6). Lesson row M2.

**NOTE-3 — C3's "status not rejected" arm is dead on all rejected rows.** `tools/round95-freeze-audit.py:76-77` reads
`cells[8]`; the registry's status is `cells[7]` (`corpus/SOURCES.md:11`). A forged plan citing S027+S591 audits
`unresolved=0 met=True`. Reproduced independently of the wave seat. Lesson row M4.

**NOTE-4 — C3's token arm checks names, never values, and only fires on the tool's own line.** Doctoring every value
on the amendment-1 C2 predicate still audits `met=True`; every shipped plan reports `tokens=0` at its own freeze. Lesson
row M5.

**NOTE-5 — the 20-file discriminator really did not discriminate, re-measured.** The base probe at twenty files is
green (`mismatches=0`, exit 0, receipt `base-20-files.out`); the lesson's M1 originally quoted "45.37 s", a figure
that appears nowhere in the committed tree (`grep -rFn "45.37" .ufo/waves/round-95/` → only the lesson line). The
draft therefore states the re-measured 46.30/58.35 s and the green base run instead of the unbacked number. Lesson
row M1.

**NOTE-6 — a second rejection candidate, opened and rejected.** `tools/server/README.md` @ b12177 (2620 lines, sha256
`eafc1b53…a137`) ties `total_slots` to the `--parallel` flag (:1019) and its own `/props` example prints
`"total_slots": 1` (:1005): it documents one server's count, not the resolved per-entry rule, so it cannot decide
`R20`/`R21`. Added as a Gate row with its flip condition.

## Deliverables

- `.ufo/waves/round-95/w1/out/SB01LessonDraft/round-95-lesson-draft.md` — the draft lesson body (`## Gate` with S616,
  S617 and two rejections incl. flip conditions; `## Mistakes` M1–M9; the round-94 D2/D3 dispositions).
- `.ufo/waves/round-95/w1/out/SB01LessonDraft/digests-and-quotes.out` — digests, `cmp` exit codes, located quotes.
- `.ufo/waves/round-95/w1/out/SB01LessonDraft/base-20-files.out` — base probe at 20 slow files (green).
- `.ufo/waves/round-95/w1/out/SB01LessonDraft/m1-guard-8-files.out` — margin guard refusing below 1.25 × 60 s.
- `.ufo/waves/round-95/w1/SB01LessonDraft.md` — this report.
- Scratch `/fast/scratch/hyaku/kama-r95/SB01LessonDraft/` removed after copying the receipts; no clone left on disk;
  no burner, stub listener or counter process left running.

VERDICT: holds — the draft lesson body is complete and every row carries a command or a path that exists (two new
NOTES: round-94's M5 defect recurs in the plan's ungraded measurement-time receipt class, and the plan's own W03
cell list contradicts the frozen counter's bytes).
