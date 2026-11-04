# kama round 77 — lesson

author: kama L1 (round 77)

Lane: kama. Round 77, one v1 build-and-attack wave of 13 seats.
Base: `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`.
Freeze commit: `7d60e2ab58866a0366937d61c9712483be57b36e`, the commit adding
`plans/round-77-claims.md`. Assigned lesson axes: calibration, freshness.
This is a source-and-receipt account at the scribe cut, not a claim that unexecuted counters passed.

## Mistakes

1. **`self-blocking-admission`** — a mechanism whose own admission rule forbids its growth.
   *Evidence pointer:* at base `cc6e1d3c`, `tools/round76-append-exempt.py:76-86,140-152`
   combines both register introductions and applies the earliest cutoff to every row.
   `corpus/lessons/round-76.md:36-52` records the resulting unsatisfiable target; the round-77
   baseline receipt `.ufo/waves/round-77/measured/before/c2-append.out` reports
   `events=241 register=53 exempt=47 restored=95 disclosed=5 unaccounted=41`, exit 1.
   An eligible event after that introduction can never enter the register, however faithfully
   the register is appended.
   *Captured-by:* none at freeze for the admission/growth contradiction; KQ114 requires a real
   do-nothing/control check, but the old negative run did not establish that future admission
   was possible.
   *Fix:* C2 separates register introduction provenance from admissible event ancestry to the
   audit revision, with a distinct history check rejecting a reintroduced path carrying new rows.
   *Shown able to fail:* the retained historical receipt
   `.ufo/waves/round-76/measured/after/append-exempt-selftest.out:1-6` records
   `rotation-reintroduced PASS exit=1 expected=1` under
   `TMPDIR=<scratch> python3 tools/round76-append-exempt.py --selftest` (overall exit 0).
   That witness injects introduction/ancestry facts; it does not establish real history discovery.
   The new module's `rotation-reintroduced` arm constructs an actual delete/re-add history, but
   EX02Registers explicitly reports it **unexecuted** at this cut. Therefore the historical red
   witness is real; the new fix's end-to-end failing demonstration is not yet evidenced here.

2. **`ungraded-is-not-one-class`** — chaining one wrong class from an aggregate audit bucket.
   *Evidence pointer:* at base `cc6e1d3c`, `tools/append-only-audit.py:651-670,719-720`
   excludes deletions outside an `only=` region from graded lines, then folds them into
   `ungraded`; `file_regions` at lines 477-487 retains the actual contract prefixes.
   Round-76's `tools/round76-append-exempt.py:58-72,130-133` cannot treat that bucket as
   synonymous with `exempt-head`. A contract-permitted outside-region deletion is not an
   exempt-head deletion merely because both are ungraded.
   *Captured-by:* KQ72/KQ84 require bound-region accounting and prohibit trusting ungraded alone;
   no base counter separately names the `out_of_region` class.
   *Fix:* C2 re-reads contract `only=` prefixes and every deleted line's parent section, crediting
   `out_of_region` only when every deletion is outside all declared regions. The separate
   `permitted` carriage bucket requires `permitted == deleted` and zero graded/ungraded lines.
   *Shown able to fail:* the authored `inside-region` arm deletes within `## Errata` and expects
   an unaccounted finding; `permitted-overclaim` plants a graded line to defeat carriage credit.
   Neither is claimed executed at this cut. These are declared detectors, not measured kills.

3. **`source-admitted-before-clean-mirror`** — a later clean census does not repair admission order.
   *Evidence pointer:* round-77 SC01Knowledge reports its preappend scratch census exited 2 for
   missing scratch `shokunin.conf`, then appended S549; the later real census exited 0.
   *Captured-by:* KQ124, which requires a retained exit-0 mirror census before append.
   *Fix:* withhold KQ124 conformance credit for this admission; do not relabel the later green
   census as the prerequisite. This is a disclosed round-local defect, not a successful repair
   or a new passing demonstration.

## Gate

- **New row S549**, `corpus/SOURCES.md:301`: Git git-log manual,
  URL https://git-scm.com/docs/git-log, access date **2026-11-04**.
  Located quote, **11 words**: “Any combination of the filter characters (including none) can be used.”
  Location: `--diff-filter`, retained HTML line 6737; preceding lines 6732-6736 define A as Added.
  SC01Knowledge retained the fetched bytes and reports curl exit 0; this scribe independently
  opened the live URL and located the same sentence in its reader output.
  Scope: added-path filtering mechanics, not proof of earliest-introduction policy, ancestry,
  byte stability, or execution. Row tier is **B**, not an inferred tier-A runtime guarantee;
  used-by is `corpus/knowledge/baseline-receipt-binding.md`.
- **Rejected candidate, checked live this round:** PostgreSQL 18 §5.6 System Columns,
  https://www.postgresql.org/docs/current/ddl-system-columns.html, accessed 2026-11-04.
  Its `xmin` paragraph describes inserting transaction identity for a row version, and `ctid`
  describes a physical location that can change. Neither defines Git register-admission
  cutoffs or baseline-receipt binding. Rejected for scope, not as false or redundant knowledge.
  **Flip:** an explicitly assigned database-backed audit problem with its own implementation
  and measured witness; a database analogy alone cannot certify C2.
- Source admission limit: S549's later exit-0 real census does not discharge the failed
  preappend-mirror prerequisite (Mistake 3). No round-77 counter, gate, or mutation pass is
  asserted by this lesson. The mutation seat's early three invocations each exited 2 with
  `[Errno 2] No such file or directory`; later authored modules do not retroactively change those runs.

## Freeze divergences

Compared the frozen plan with the available C1/C2/C3 implementation source, not merely seat labels.
The observed branch tip at the initial read was the freeze commit; this is not a certification
of a later landing commit or a mechanical normalized-PREDICATE equality check.

1. **C2 admission interpretation:** predicate lines 101-103 say rows are “under that register's
   own introduction cutoff”; scope ruling lines 113-118 instead admits event commits ancestral
   to the audit revision and allows append-only growth. The implementation follows the latter.
   Reason supplied by EX02Registers: growth must remain possible while introductions remain
   independent provenance and rotation guards. Both frozen formulations remain recorded;
   this lesson does not adjudicate their conflict or rewrite either one.
2. **C2 input revision split:** `evaluate` reads working-tree register TSVs while the audit,
   contract and introduction histories come from `--to`. Reason in the module docstring: a new
   append must account for the explicitly historical audit revision. This differs from the
   prior committed-register read; a clean committed-input binding is not established by source
   inspection. Freeze scope does not explicitly pin the register read to one of these views.
3. **C3 correction scope:** the implementation ignores correction blocks already present verbatim
   in the sealed record, avoiding same-id round-75 corrections being applied to round-76 facts;
   newly appended corrections require dated, value-bound provenance. This is an explicit
   implementation interpretation of “superseded” in the predicate, not an observed passing run.
4. **Source tier:** the new live Git manual row is B under SC01Knowledge's specific assignment,
   rather than the broader tier-A wording reported by that seat. This changes source-authority
   labeling, not any frozen counter predicate, exit map or target.

C1's baseline-only ancestry/byte-stability branch and inherited fence/record scope, and C3's six
named facts and 0/1/2 exit intentions are present in the inspected source. That is source evidence
only. No “none observed” claim about unobserved final landed bytes is made.

## Round-77 duties

- **D1 — coverage map:** SC03 appended the missing selfrecord-fact-binding row and correction;
  its re-derivation records 49 files/41 mapped/8 missing at the cited round-76 revision, leaving
  seven missing after the new row. Disposition: authored and evidence-rederived, not a new census run by this seat.
- **D2 — stale population 46:** remains an owed value-bound SCORECARD correction to 47 at
  `c2aa7fb2`; EX03 authored the C3 detector but did not edit the record or execute it. No closure credit at this cut.
- **D3 — post-cutoff undercount:** SC03 appended corrections to round-76 lesson and LOG;
  `.ufo/waves/round-77/w1/SC03Corrections/after-postcutoff.out` records pre=31/post=6/total=37,
  exit 0: five SCORECARD events plus the register-introduction commit's SOURCES event.
- **D4 — Gate discipline:** SC03 added the exact 15-word CommonMark sentence, S548 access
  date/own-work command, and S498 used-by old→new history in round-76 Gate; its derivation
  receipts report exit 0. This Gate separately supplies S549 URL/date/located quote and a real rejection.
- **D5 — capability without green demonstration:** no verified append-registers capability
  admission at this cut; EX02 reports the module/selftests unexecuted. A row or authored detector
  alone cannot close this duty. Historical append-exempt-class stays a red demonstration, not green evidence.
- **D6 — committed draft pointer:** **apply with repaired pointer**, not discard. SC03 applied the
  substance to LOG with `.ufo/waves/round-76/measured/after/gate-selftest.out`; the draft remains
  historical, not authority for its nonexistent proposed path. Its after-logtally receipt exits 0,
  preserving historical pass18 as unbacked and actual round-76 pass21 as receipt-backed, without rerunning the gate.

## Gate — L1 integration correction (2026-11-04)

The seat's Gate admitted **S549** as the round's new row. L1 integration rejected it and admitted
**S550** instead; the seat text above is retained as filed history.

- **S549 rejected as a duplicate.** `https://git-scm.com/docs/git-log` is already held three times
  (S073, S085, S093) and S073's scope cell names the `--diff-filter`/added-path ground S549
  claimed. Re-appending it duplicated the claim; the round's expansion is the knowledge entry, not
  the row (the same ruling round 76 applied to its CommonMark candidate). Flip: a distinct anchor
  or claim on that URL that S073/S085/S093 do not hold. The retained live quote (11 words,
  `--diff-filter`, retained HTML line 6737; fetched copy sha256
  `0be728012bad1e48a590db5fa1cd56c9eb4cc746e4b3e1b9bb00954c90ec2961`) stays as Gate evidence for
  this rejection and for the entry's paraphrase.
- **S550 admitted, tier A, own-work.** `python3 tools/round77-citation-baseline.py --repo .
  --round 75` → `CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2
  shifted=0 nonreceipt=0 unclassified=0` exit 0, `--selftest` → `CITATION_BASELINE_SELFTEST
  pass=7 fail=0`, receipts `.ufo/waves/round-77/measured/after/c1-baseline.out`,
  `c1-selftest.out`. Used by `corpus/knowledge/baseline-receipt-binding.md`.
- Census after the change: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin kama` → exit 0 (W04 warnings only, S549 among them as a rejected
  duplicate).
- Duty D6 is closed as **applied**: the log-tally correction already exists at `LOG.md:3044` with
  the repaired receipt `.ufo/waves/round-76/measured/after/gate-selftest.out`; SC03 verified and
  did not duplicate it.
- Duty D5 is closed by the landed green demonstration: `tools/round77-append-registers.py
  --selftest` → `APPEND_REGISTERS_SELFTEST pass=7 fail=0` at
  `cc6e1d3c…`, and the counter prints the frozen C2 line.
