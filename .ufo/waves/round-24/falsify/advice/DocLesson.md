# DocLesson — falsification of `corpus/lessons/round-24.md` (round 24, lane DocLesson)

Pinned revision under test: `2e254a1763a9c08aa07fc53081287f506c447d84`
("round-24: land completed 64-seat build evidence and explicitly carry residual closure debt").
Scratch clone (read-only, `--no-hardlinks`): `/fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo`,
detached at the pinned revision. No lane, fleet, sibling, routing or production object store was touched.
No full suite, no mutation probe execution, no network payload. Sources read over plain official HTTPS only.

Scope note: the production working tree copy of the lesson has since been appended to by another
falsify lane (38 lines, `## Round24 falsification erratum (appended)`); every quoted line below is
from the **pinned revision** content, which is byte-identical to the production file except for that
appended erratum block (`git diff` = those 38 added lines only).

---

## Verdict summary

| # | Finding | Severity | Class |
|---|---|---|---|
| F1 | The round-24 continuation mistake row claims its capture happened "before L1 candidate source inspection" and that the 44-case freeze happened "before L1 inspection"; the wave's own record contradicts that chronology | **MEDIUM** | chronology truthfulness |
| F2 | The S105 "Located quote" is a de-marked rendering; it is **not** a byte substring of the pinned reader snapshot it points at (plain form 0×, rendered form 2×) | **LOW** | citation fidelity |
| F3 | S103's "Independent opening" cites `SrcRepoLayout.md`, whose own §Design Details attribution of that sentence is the attribution the wave explicitly rejected | **LOW** | traceability |
| F4 | "PM02 is the negative control for the rejected blanket rule" names a control whose kill is only evidenced on a superseded grid copy in baseline mode with a failing pristine; the shipped-pair re-run was never made | **LOW** | evidence status |
| — | Everything else attacked (see HOLD table) | — | holds |

**No finding relabels the withdrawn expectation as passed.** The withdrawn original expectation
(`preregistration.json` expected_after[3]) remains recorded as withdrawn/not-achieved everywhere it
appears; no finding below changes that status.

---

## F1 (MEDIUM) — the "before L1 inspection" chronology is not supported by the wave's own record

### Falsifiable claim as written

`corpus/lessons/round-24.md` (pinned revision), "Mistakes — round24 integration continuation", row 1:

- **Captured-by:** `independent CritScores/CritUnknown/CritNoTrade review before L1 candidate source inspection`
- **Fix:** `... freeze the independent44 before L1 inspection, and grade prospective behavior separately ...`

Also, line 78: `the47 expected cells remain byte-identical to the frozen44 plus the independently filed3-cell supplement.`

### Observed (commands, exit codes, tokens)

```
$ cd /fast/scratch/hyaku/kama-r24/falsify/DocLesson/repo && git log --format='%h | ad=%ad | cd=%cd | %s' --date=iso -6 2e254a1
2e254a1 | ad=2026-10-21 16:45:11 -0300 | cd=2026-10-21 16:45:12 -0300 | land completed 64-seat build evidence ...
f1e755e | ad=2026-10-21 16:39:10 -0300 | cd=2026-10-21 16:39:10 -0300 | reconcile supported source consumers ...
ed1cc3a | ad=2026-10-21 15:14:18 -0300 | cd=2026-10-21 15:44:52 -0300 | restore local promisor verdicts ...   <-- candidate
aacbd52 | ad=2026-10-21 15:12:55 -0300 | cd=2026-10-21 15:14:18 -0300 | append independent opaque-dependency oracle supplement
f66b226 | ad=2026-10-21 15:04:12 -0300 | cd=2026-10-21 15:12:55 -0300 | freeze independent 44-case original and amended oracle
123640b | ad=2026-10-21 15:04:12 -0300 | cd=2026-10-21 15:04:12 -0300 | append preintegration local-object oracle correction
```

```
$ stat -c '%y  %n' <wave files>            # exit 0
2026-10-21 14:47:59 -0300  preregistration.json
2026-10-21 15:00:24 -0300  build/advice/CritScores.md
2026-10-21 15:03:32 -0300  oracle-amendment-1.json
2026-10-21 15:03:38 -0300  build/out/CaseMissingFleetTree/audit-candidate-wip.json
2026-10-21 15:04:52 -0300  build/advice/CritNoTrade.md
2026-10-21 15:08:31 -0300  build/out/CritUnknown/candidate.patch
2026-10-21 15:09:21 -0300  build/out/CritUnknown/witness-output.txt
2026-10-21 15:12:41 -0300  build/out/CritUnknown/hidden_probe.py
2026-10-21 15:12:43 -0300  oracle-snapshot-before-inspection.json
2026-10-21 15:13:00 -0300  build/advice/CritUnknown.md
2026-10-21 15:14:06 -0300  oracle-supplement-2.json
```

Tokens that break the chronology:

1. `CaseMissingFleetTree/audit-candidate-wip.json` (15:03:38) already measures a **candidate auditor blob**
   `5cf9c72a6c3d633df259002caf4b82451dca317fa4cb9d67c9308cc7f52bc2bd` — i.e. candidate work predates the
   44-case snapshot file (15:12:43) by ~9 minutes and predates the freeze commit's committer time
   (15:12:55).
2. `CritUnknown/candidate.patch` (15:08:31) and `witness-output.txt` (15:09:21) are candidate measurements
   taken before the snapshot file existed.
3. `CritUnknown.md` itself is candidate-informed: `:76` `| candidate (ruling v3) | 0, 9/9 | 0, 9/9 | **0, 9/9** |`,
   `:47` "In the candidate, metadata never decides a verdict", `:152` "`out/CritUnknown/candidate.patch`
   implements exactly this ruling", `:269` "Candidate updated (`out/CritUnknown/candidate.patch`, +73/-29)".
   Its mtime **15:13:00 is later than the freeze commit's committer time 15:12:55**, so the third cited
   reviewer is neither pre-candidate nor pre-freeze at the document level.
4. The oracle amendment itself is an L1 ruling on candidate semantics, committed `123640b` at 15:04:12 —
   8 minutes before the freeze commit and before the snapshot file was written. `CritUnknown.md:7`
   ("This supersedes my all-refs-closure gate (ruling v3)") shows the L1's candidate-semantics ruling
   (relayed in the frozen manifest's own `amendment.relayed_by` field) was already circulating and being
   implemented into a candidate before the freeze.

By contrast, two of the three cited reviewers *are* verifiably pre-candidate, and say so themselves:

- `CritScores.md:18` "scratch at `d1b9d95` had no auditor diff when I checked, so I could not …",
  `:38` "[INFERENCE: no candidate exists yet]", `:170` "Unverified: candidate behaviour (no candidate diff existed)".
- `CritNoTrade.md:178` "Any candidate implementation (none existed in `/fast/scratch/hyaku/kama-r24/AuditRepair` at …)".

### What *does* hold (and is the falsifiable, verifiable form of the claim)

The **values** of the frozen 44 are candidate-independent, and I verified this directly rather than trusting
the narrative:

```
$ python3 (compare oracle-snapshot-before-inspection.json vs tests/report-audit/promisor-grid-expectations.json)
shared 44 byte-identical 44 extras ['PG46-opaque-tree-hides-cited-blob', 'PG47-opaque-tree-with-unresolved-fabricated-token', 'PG48-opaque-unused-tree-no-unresolved-token']
rc=0
$ python3 (recompute frozen_auditor_sha256 from git show 0df800e:tools/report-landing-audit.py)
pinned da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1
actual da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1   match True
rc=0
$ python3 (map the 3 supplement rows onto the shipped manifest)
opaque-tree-hides-cited-blob            -> PG46-... exit 2 MATCH
opaque-tree-with-unresolved-fabricated-token -> PG47-... exit 2 MATCH
opaque-unused-tree-no-unresolved-token  -> PG48-... exit 0 MATCH
rc=0
```

So: the 44 are byte-identical to the shipped manifest, pinned to the **base** auditor sha
(`da5041a8…`, i.e. `0df800e`, not the candidate `ea51bc35…`), and the 3 supplement rows carry exactly the
supplement's `expected_exit` values with candidate-independent probes (the supplement's probe
`build/out/CritUnknown/hidden_probe.py` writes and audits the **FROZEN** auditor from `grid.FROZEN`, so its
expectations do not depend on the candidate). The lesson's line-78 claim is therefore **true**, and the
"independently filed" characterisation of the supplement's *expectation values* is **true**.

### Minimal correction (report only; no production edit made)

In the row's Captured-by and Fix cells, replace the wall-clock wording with the two separable facts that are
actually verifiable:

- Captured-by → `CritScores and CritNoTrade, verifiably pre-candidate (CritScores:18, :170 "no candidate diff existed"; CritNoTrade:178 "no candidate implementation existed"); CritUnknown's local-object contract is a candidate-informed document (candidate.patch 15:08:31, candidate row :76) whose expected rows are "derived from source and fixture premises, not from running a candidate" (:198)`.
- Fix → `freeze the independent44 with candidate-independent values (44 shared cases byte-identical to the shipped manifest, base-auditor sha da5041a8…, not the candidate ea51bc35…); the freeze file itself was written after candidate work existed (snapshot 15:12:43 vs candidate-wip audit 15:03:38)`.

Do **not** weaken the value-independence claim — it is independently verified and stronger than the
chronological wording it replaces.

---

## F2 (LOW) — S105's "Located quote" is not byte-present in the snapshot it pins

Lesson lines 95–96 and 153 present the quote `If 'strict' (the default), a UnicodeError exception is raised.`
as the located quote in bytes.decode errors, and point at
`.ufo/waves/round-24/sources/S105.json`, which "pins that snapshot". `S105.json` carries the identical plain
string in its `quote` field and `sha256 54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80`.

```
$ python3 (over the pinned snapshot)                                        # exit 0
sha match True 54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80
counts [0, 0, 0]                # subprocess / TextIOWrapper / text mode  -> the lesson's 0/0/0 is CORRECT
plain-quote occurrences 0
rendered-form occurrences 2     # "If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised."
```

The pinned artifact stores the sentence as markdown (backticked `` `'strict'` `` plus a `UnicodeError`
link); the plain form occurs **0×**. Upstream `docs.python.org` behaves the same way (plain form appears only
after tag-stripping the rendered text). The lesson's negative claims are exactly right — `subprocess`,
`TextIOWrapper`, `text mode` are 0/0/0 in the pinned snapshot — but a reader who greps the pinned file for
the quoted sentence as printed gets zero hits, in a corpus whose whole method is byte-level quote fidelity.

Minimal correction: either print the snapshot's own rendered form (with backticks/link) as the quote, or add
one clause: "the pinned snapshot stores it as markdown emphasis; the plain form occurs 0× and the rendered
form 2× in `python-bytes-decode-reader.txt`". Apply the same wording to `S105.json`'s `quote` field.

---

## F3 (LOW) — S103's "Independent opening" cites a source carrying the rejected attribution

Lesson line 28: `Independent opening: build/advice/SrcRepoLayout.md and SrcPartial.md.`

`SrcRepoLayout.md:77` states: **§Design Details**, not S099's §Handling Missing Objects anchor" and quotes
the very sentence the lesson attributes to §Handling Missing Objects. The wave already adjudicated this:
`ConnPriorSources.md` D5 (do-not-act) — "S103's anchor is right; a peer's contrary note would break it …
SrcRepoLayout's section attribution is the error. Do not 'correct' S103 toward §Design Details."

Upstream re-check (plain HTTPS read of the official partial-clone page, tag-stripped, whitespace-normalised):
the sentence occurs **1×**, and its position lies between the `§ Handling Missing Objects` heading and the
next h2 — i.e. the lesson's anchor is correct and `SrcRepoLayout.md`'s is the rejected one.
`SrcPartial.md:35,51` carries the correct anchor.

Minimal correction: cite `SrcPartial.md` as the independent opening (it is the one with the correct anchor),
and either drop `SrcRepoLayout.md` from that list or annotate it — "cited for the `.promisor` sidecar fact only;
its §Design Details attribution of that sentence is the rejected one (ConnPriorSources D5)".

---

## F4 (LOW) — "PM02 is the negative control" lacks a shipped-pair receipt

Lesson row 1, Fix cell: `... PM02 is the negative control for the rejected blanket rule`.

PM02's role is real and correctly named: `build/out/MutationOracle/mutation-inventory.json` /
`MutationOracle.md` define `PM02 blanket-unknown-refusal` over rows PG22–PG25, PG29, PG30, PG33, PG34,
PG37, PG41, PG42, PG47, with exactly the rejected blanket-rule semantics. The row's *Evidence* cell
(`preregistration.json` expected_after[3]; CritScores' spliced-hash/errata witness; original tool
contract:12–19) is independently sourced and correct.

What the row does not say is the **evidence status** of that control:

```
$ python3 (mutation-inventory.json vs shipped pair)                          # exit 0
inv grid_sha256            b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa   (== shipped grid)
inv candidate_auditor_sha  ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220   (== shipped auditor)
shipped grid sha           b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa
shipped auditor sha        ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220

$ python3 (sensitivity-promisor-grid.json)
sens baseline_mode True | grid .../build/out/GridOracle/promisor-grid.py   # sha 5e96fa60..., NOT the shipped b034e159
sens pristine_unmet_cells ['PG15-missing-lane-tree-promisor','PG16-missing-lane-tree-plain',
                           'PG19-missing-fleet-tree-promisor','PG20-missing-fleet-tree-plain',
                           'PG46-opaque-tree-hides-cited-blob']
sens killed_ids [... 'PM02-blanket-unknown-refusal' ...]
```

The only PM02 kill receipt in the wave is that **baseline-mode** run: it used the superseded grid copy
(`5e96fa60…`, not the shipped `b034e159…`) and had a pristine with **5 unmet cells**. Under the shipped
runner's own rule (`promisor-mutants.py:82-84` and the code at `:711-716`: *"the pristine candidate must meet
the grid; otherwise no mutant can be attributed and nothing is credited"* → `could-not-evaluate`, exit 2), that
same run would credit **no** kill at all. `MutationOracle.md` §9.1 states the situation plainly: against the
integrated pair (`ea51bc35…` / `b034e159…`) the run "should exit 0 with nine kills and one survivor (PM07) …
This is the re-run I did not make after the repair".

Minimal correction: qualify the Fix cell — "PM02 is the designated negative control for the rejected blanket
rule (role from the mutation inventory); its kill is evidenced only in the baseline-mode sensitivity run
against the superseded grid copy `5e96fa60…` with a failing pristine; the shipped-pair re-run was not made
(MutationOracle §9.1)". The control designation itself needs no change.

---

## HOLD — claims attacked and found sound (no correction needed)

| Lesson claim | Verification | Result |
|---|---|---|
| Round base `0df800e…`; preregistration landed `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d` | `git rev-parse d1b9d95` = full sha; `git show 0df800e:tools/report-landing-audit.py:12-19` = the two defect definitions quoted by row 1 | holds |
| "the47 expected cells remain byte-identical to the frozen44 plus the independently filed3-cell supplement" | 44/44 byte-identical; extras exactly PG46/47/48; supplement `expected_exit` = manifest `amended.exit` (2/2/0); base-auditor sha pin | holds |
| "original expectation bytes remain filed" | manifest sha `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` == the sha recorded in `GridOracle.md` | holds |
| Consumer-reconciliation table (11 rows, old→new used-by) | every old value matches the base/ed1cc3a row, every new value matches HEAD; only field index 10 changed for S001–S104; HEAD has 105 rows incl. S105 | holds (11/11) |
| "S095's immutable rejected teaches cell is not rewritten" | S095 `teaches` and `anchor` byte-identical base→HEAD; status stays `rejected`; S105 records the explicit rejection; S096 stays the narrowed positive replacement | holds |
| S102 quote + anchor | upstream `git-rev-list` official page, tag-stripped: plain sentence occurs 1× and sits after the `--missing=<missing-action>` heading; the "documents encountered-missing output, not a numeric exit policy" scope statement is the lane's own inference and is labelled as such | holds |
| S103 quote + §Handling Missing Objects anchor | upstream official page: 1× occurrence inside that section (heading boundaries checked) | holds (anchor only; see F3 for the cited opening) |
| S104 `mark_object` lines143–149 quote and "returns before checking HAS_OBJ" | retained copy `build/out/SrcFsck/fsck-builtin.c` sha `d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35` == upstream `v2.56.0 builtin/fsck.c`; in the retained file the `is_promisor_object` early `return 0;` precedes the `HAS_OBJ` check | holds |
| S105 negative counts 0/0/0 over the pinned reader snapshot | recomputed: `[0, 0, 0]`; snapshot sha matches S105.json | holds (quote form: see F2) |
| r23 lineage rows: lesson:178 "68 reports" vs 69 durable reports; 73 seats / 4 dead; 56 vs 40 vs 19 identity rows; T01 vs F23 fixture split (`:195-213`, `:596-602`) | r23 lesson:176-179 reads "73 seats dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty …"; `ls .ufo/waves/round-23/falsify/advice/ | wc -l` = 70 entries, of which one is `swarm-registry.json` → 69 reports; LOG.md:1417-1418 "69 durable lane reports, not 68" and "40 of the 56 killed FIFO-process identities were retained"; LOG.md:1439-1443 "Only 19 retained rows could be linked to FIFO fixtures"; `repo-state-grid.py:195-213` = `f_promisor_pack` (`--no-checkout`, asserts a reachable blob absent) and `:596-602` = `t_blobless` (clone then checkout ⇒ hydrated) | holds |
| Round-24 continuation rows 2–5 (vacuous fixture / 39-hex splice; cross-repo survivor; hidden cited blob; twin-mismatch ordering) | `GridOracle.md:272` `extra = [] if expect.get("errata") else []` — always empty; `:281` the 39-hex splice; Corrections 3 (341) and 4 (417) exist as cited; `proxy-run-r23-grid.json` lists `PM05-ignore-second-repo` as surviving; shipped grid computes `twin_equal` (1014) **before** adding twin-mismatch rows to `live_fail`/`frozen_fail` (1020-1028); shipped runner drops both `opaque_tree` and `hidden_blob` and asserts absence in both repos; shipped auditor reports raw vs uncorrected defects separately | holds |
| "The Git>=2.45 prerequisite is explicitly not approved or repaired: R23-H2 is carried as the round24 L0 question" | `CritScores.md` S2 (H2 unchanged, not discharged); `SCORECARD.md` round-24 section: the Git>=2.45 prerequisite remains an unresolved R23-H2 operator decision | holds |
| "Numeric score calibration 7→7 is not an admission or claim that operability harm was waived" | consistent with the round-23 closure ruling `rejected-harmed` recorded in `ConnClosure.md:5` | holds |
| Residual-debt identifier list (RowF12 … N01/N02/N03/D02/D03) | every identifier appears in `ConnClosure.md` (including `CritTradeoffHarm H2`, `SentinelDoSW2`, `ConnSiblingTools`); `uncommitted-draft-uses-now` and `inherited-GIT_DIR-untouched` selftest expressions byte-identical base→HEAD | holds |

---

## Residual risk / not verified here

- `MANIFEST rounds[428]` is an **outside-closure** artifact; it is not in this repository (only
  `corpus/QUALITY.md` / `corpus/README.md` reference `rounds[428]`). I corroborated its content through the
  wave's own `build/advice/ConnClosure.md:5` (`admitted false`, `verdict rejected-harmed`) rather than the
  outside file itself. Unverified directly: the outside MANIFEST's own `verification.spotcheck` text.
- I did not execute the r23 grid, the mutation runner, or any candidate; all mutant/pristine statements above
  are read from retained receipts, not re-measured.
- Whether "L1 inspection" in the lesson was intended as "L1 inspection of candidate source" or "L1 inspection
  of the frozen oracle" is not decidable from the text; F1 is written to be valid under either reading.
- The production tree's appended `## Round24 falsification erratum` block (another lane) was not audited;
  my findings target the pinned revision's rows, which that block does not alter.

---

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/DocLesson.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocLesson/evidence.json`
  (command/exit-code/finding token pairs, machine-readable)

No production file was edited by this lane.

Report: .ufo/waves/round-24/falsify/advice/DocLesson.md
