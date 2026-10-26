# X1Docs — round-49 documentation drift audit (lane kama, seat X1Docs)

**VERDICT: 20 documentation sites at the build tip still describe the three instruments the build
changed as they were at the round-48 closure — 19 caused by a build commit that touched code and
`corpus/SOURCES.md` only, and one (KQ75's two replay pointers) standing since the base. All are
documentation drift, not counter defects. The graded instruments themselves behave
as the frozen counters expect (audit `AOA_SELFTEST pass=30 fail=0` and lane exit 0;
`fixture=1 lane=1 scenarios=8/8 met=True`; replay `KLR_SELFTEST pass=22 fail=0`, `compare
match=True`). Nothing was edited in place: four appended-correction blocks and two patches are
drafted in `X1Docs/` (two more blocks are redundant with integration text that landed during the
work and are marked as such).**

Audited revision `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (build), base
`438127bc01ff3b99f98468549d58046f932490ef`, on my own `git clone --shared` at
`/fast/scratch/hyaku/kama-r49/X1Docs/lane` (toplevel asserted; lane left untouched). The four
docs were byte-identical between the lane's live tree and the tip when the audit started; **during
the audit the live tree moved** — other round-49 seats landed a round-49 `SKILL.md` registry
(`:1486-1504`), criteria KQ76–KQ79, a `## Frontier disposition — round 49`, a knowledge append, a
contract re-anchor and a replay-selftest witness case. Line numbers below are the tip's. The
consequence is recorded in §6: my `SKILL.md` blocks (§1) and the knowledge block (§4) are
now redundant with that landing, while the KQ70/KQ71/KQ72/**KQ75** and `corpus/README.md`
corrections are not covered by it (re-checked in the live tree at the end of the audit).

## 1. Evidence — every command, exit code, key output

All run from the clone at `74558c71` with `TMPDIR` under my scratch. Raw outputs in
`X1Docs/evidence/`.

| # | command | exit | key output (file) |
|---|---|---|---|
| 1 | `git show --stat 74558c71` | 0 | 4 files: `corpus/SOURCES.md`, `tools/append-only-audit.py`, `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py` — no `.md` tool description updated |
| 2 | `python3 tools/append-only-audit.py --selftest --scratch $S/st` | 0 | `AOA_SELFTEST pass=30 fail=0`; cases `launder-through-head` and `binding-v4` are new (`evidence/aoa-selftest.out`) |
| 3 | same selftest for the base tool (`git show 438127bc:tools/append-only-audit.py`) | 0 | `AOA_SELFTEST pass=28 fail=0` — the two new cases are the v4 definition (`evidence/aoa-base-selftest.out`) |
| 4 | `python3 tools/append-only-audit.py --repo <clone> --to 74558c71 --contract registry/append-only-contract.tsv --json` | 0 | `schema append-only-audit/v3`, **`definition v4`**, `commits=319 files=92`; events `0718b6ab SCORECARD.md deleted=2421 graded=2356 ungraded=65 restored`; `summary … ungraded_lines=82 regressed=0 vanished=0 bad_declarations=0` (`evidence/aoa-lane.json`) |
| 5 | same command, text mode | 0 | identical counts; `summary commits=319 files=92 events=5 restored=5 … ungraded_lines=82 …` (`evidence/aoa-lane.txt`) |
| 6 | base tool (v3) on the same clone and tip | 0 | `ungraded_lines=89`, event `graded=2349 ungraded=72` — the 7-line regrade the C2 claim names (`evidence/aoa-base-lane.txt`) |
| 7 | `python3 tools/round49-append-audit-v4-check.py --repo <clone> --tip 74558c71 --scratch $S` | 0 | `fixture=1 lane=1 scenarios=8/8 met=True`; `substring`/`negated`/`wildcard-self` → `bad_declarations 1` exit 1; `word-token`/`wildcard-named` → 0; `lane … ungraded_lines 82`, `0718b6ab ungraded 65 <= natively exempt 65` (`evidence/c2-counter.out`) |
| 8 | `python3 tools/kama-live-replay.py --selftest --scratch $S/rs` | 0 | `KLR_SELFTEST pass=22 fail=0` (`evidence/klr-selftest.out`) |
| 9 | `python3 tools/kama-live-replay.py --compare receipt-1.json receipt-2.json` | 0 | `compare match=True mismatches=0` (`evidence/klr-compare.out`) |
| 10 | `… --receipt receipt-1.json --work $S/w --out $S/j.json --witness-dir $S/does-not-exist` | **2** | `kama-live-replay.py: error: --witness-dir must be an existing directory` (`evidence/klr-baddir.out`) |
| 11 | `python3 tools/kama-llamacpp-live.py --selftest` | 0 | `selftest: ok` (includes `_provenance_selftest`, which asserts all seven archive/member refusals, `tools/kama-llamacpp-live.py:1387-1400`) (`evidence/ll-live-selftest.out`) |
| 12 | `python3 tools/append-only-audit.py … --threshold 1` | 1 | `events=100 restored=18 partial=4 unrestored=59 ungraded=19 ungraded_lines=187` (`evidence/aoa-t1.txt`) |
| 13 | `.ufo/waves/round-47/w1/out/S9Quality/heading-census.py --repo <clone> --head 74558c71` | 0 | `headings=21 covered=18 uncovered=3`; uncovered `SKILL.md:1434`, `:1444`, `:1465` (`evidence/headings.out`) |
| 14 | `.ufo/waves/round-48/w1/out/S9Quality/receipt-provenance-check.py receipt-{1,2,3}.json` | 0 | `receipts=3 bound=1`, every field 1 (`evidence/receipt-prov.out`) |
| 15 | token diff base→tip (`grep -o 'provenance-[a-z-]*'`) | 0 | new: `archive-not-regular`, `archive-too-large`, `archive-too-many-members`, `member-size-mismatch`, `member-sparse`; none removed (`evidence/{base,tip}-tokens.txt`) |
| 16 | `git rev-parse HEAD` in the clone after `git checkout -q 74558c71` | 0 | `74558c71…` (fixture-toplevel asserted first) |
| 17 | base `tools/kama-live-replay.py` `:154-176`, `:394-399`; `grep -n 'def compare\|"--compare"'` | 0 | projection starts `:164`, `compare()` `:194`, `--compare` `:435` — KQ75's two pointers (`:154-175`, `:397`) were already off at the base, so that defect predates the build |
| 18 | live-tree re-diff of eight files (`SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/llamacpp-loading-lifecycle.md`, `registry/append-only-contract.tsv`, all three `tools/*.py`) against the tip | 0 | all eight changed during the audit (integration in flight); the stale doc pointers this report names are still present in the live tree (`evidence/live-tree-rediff.out`) |

No counter, preregistration or control was run to a different answer: rounds 49's counters are
outside this seat's scope and the L1's dry run stands.

## 2. Drift, by class (full machine table: `X1Docs/drift-table.tsv`, 20 rows)

The classes overlap by design — a wrong line pointer usually sits inside a sentence that is also
out of date — so the per-class counts below sum above the row count; the table is authoritative.

**2.1 Stale code pointers (9 sites).** Every `tools/append-only-audit.py:NNN` citation in the
docs was taken against the round-48 tool; the v4 docstring (+21 lines) and new functions moved the
code, so the pointers now land on unrelated lines. KQ75's two `tools/kama-live-replay.py` pointers
are a standing defect of the same kind (wrong since the base).

| doc site | cites | is now | should be |
|---|---|---|---|
| `corpus/README.md:809` | `:184` (file-set expansion) | contract header check | `:277` (expansion), `:194-196` (rule validation) |
| `corpus/README.md:965` | `:147-151` (region grammar) | `_git` | `:171-175` (`parse_region`) |
| `corpus/README.md:966` | `:231-239` (no section before first `## `) | `binds`/`line_at` | `:265-272` (`sections`) |
| `corpus/README.md:979` | `:396` (threshold) | blank line | `:452` (filter), `:961` (default 20) |
| `corpus/README.md:984` | `:119` (negation list) | docstring | `:141` (`NEGATIONS`), `:212-213` (`NEG_WINDOW`) |
| `corpus/README.md:991` | `:171-174` (rule cell) | region parsing | `:194` |
| `corpus/QUALITY.md:397` (KQ70) | `:203` (hunk-count raise) | `row_token` docstring | `:456` |
| `corpus/QUALITY.md:408` (KQ72) | `:190-199` declaring line; `:210-229` region pointer | `parse_contract`; `binds` | `:249-259`; `:255-259` |
| `corpus/QUALITY.md:411` (KQ75) | replay `:154-175` projection; `:397` `--compare` | `evaluated`/`_get`/start of `projection`; a selftest negative case | docstring `:17-26`; `projection()` `:168-196`; `compare()` `:198`; option `:446` |

**2.2 False or incomplete semantic claims (4).**

1. `corpus/README.md:983-989` — "the path token is a bare substring match (`:180-199`) … the
   negation list is four contiguous phrases (`:119`)". At the tip the token must be a whole word
   (`tools/append-only-audit.py:233`), a negation within three words unbinds (`:212-213`,
   `:226-227`), and a wildcard row is not bound by a covered file's self-declaration (`:231-233`).
   Measured (row 7 above): the named `LOG.md isn't append-only.` / `changelog` fixtures now report
   `bad_declarations 1`, exit 1.
2. `corpus/README.md:807-810` — "the tool never reads `rule`, `declared_at` or `note` … the
   declaring-line check lives only in the round-47 counter". Since v3 the tool binds `declared_at`
   and region pointers (`:249-259`) and `--json` prints `declarations`.
3. `corpus/README.md:926-931`, `:954-960` and `corpus/QUALITY.md:408` — exemption "while the
   section is not gutted" with mass `2349`/`72`/`89`. v4 adds the origin condition (`:423-441`,
   `:469-477`); the same tree now reads `graded=2356 ungraded=65`, `ungraded_lines=82` (rows 4–6),
   event still `restored`, exit 0.
4. `corpus/README.md:1006-1011` — record time "hashed the archive, the archive member and the
   model". It now first refuses an archive that is not a regular file, >1 GiB or >4096 entries, and
   a member that is sparse or size-mismatched (`tools/kama-llamacpp-live.py:212-263`).

**2.3 Stale pinned values (3).** `SKILL.md:1473` (`AOA_SELFTEST pass=28` → 30; lane `90 files`,
`ungraded_lines 89` → `92`/`82`); `corpus/QUALITY.md:398` (KQ71's check now prints
`headings=21 covered=18 uncovered=3`, and `files=92` at the tip); `SKILL.md:1452`'s
`KLR_SELFTEST pass=13` (the round-48 row already says 22, measured 22).

**2.4 Capability omissions (7).** `SKILL.md:1474` (five new setup tokens, the bounds, and the whole
`--witness-dir` capability plus the `witness` receipt block); `SKILL.md:1475` (usage lacks
`--witness-dir`/`--witness-timeout`, exit map lacks the witness path and the added output field);
`SKILL.md:1452` (output field list omits `notes` and `witness_dir`); `SKILL.md:1465` (registry
heading now the third uncovered heading in the KQ71 census); `registry/append-only-contract.tsv:3`
(note still "(round 48, v3 region)" and "ungraded while they are not gutted");
`corpus/knowledge/llamacpp-loading-lifecycle.md:442,444-451` (replay invocation and "what the
replay cannot show" predate the witness and the bounds); `tools/kama-live-replay.py:36-38` (its own
output contract omits `witness_dir`, which `:279` writes).

**2.5 Closed frontier presented as open (2).** `corpus/README.md:1030-1039` ("witnesses no
process") and `:1064-1066` (frontier "An execution witness in the replay leg"): closed at this
build by `--witness-dir` (ready.json + hold until release, receipt `witness`, replay `witness_dir`).
`corpus/QUALITY.md:408`'s "binding test a denial cannot pass" is narrowed, not closed (the rule is
still lexical and the counter reimplements it).

## 3. Defects with a command and a proposed fix

**D1 — `corpus/QUALITY.md:398` (KQ71) states a check result the check no longer produces.**
Command: `python3 .ufo/waves/round-47/w1/out/S9Quality/heading-census.py --repo <clone> --head
74558c71` → `headings=21 covered=18 uncovered=3` (evidence row 13), not `13/11/2`; the extra
uncovered headings are `SKILL.md:1444` and `SKILL.md:1465`. Fix: append the correction block in
`X1Docs/appended-corrections.md` §2 (disposition both as topic labels, like `:1434`).

**D2 — `tools/kama-live-replay.py:36-38` omits an output field it writes.**
Command: `grep -n witness_dir tools/kama-live-replay.py` → `:279 res["witness_dir"] = …`, while the
docstring's `Writes J:` list (`:36-38`) does not name it. Fix: `X1Docs/replay-docstring.diff`
(one added clause, no behaviour change).

**D3 — `corpus/README.md:983-989` asserts a binding behaviour the tool no longer has.**
Command: `python3 tools/round49-append-audit-v4-check.py …` → `substring: bad_declarations 1 want 1`
(and `word-token: 0`); plus `tools/append-only-audit.py:233`'s `(?<![a-z0-9_])…(?![a-z0-9_])`.
Fix: appended correction §3 bullet 2 (the round-48 sentence stays as history).

**D4 — `registry/append-only-contract.tsv:3`'s note contradicts the grading that runs.**
Command: `python3 tools/append-only-audit.py --repo <clone> --to 74558c71 --contract
registry/append-only-contract.tsv --json` → `definition v4`, event `ungraded 65`; the note still
says "ungraded while they are not gutted (round 48, v3 region)". Fix: `X1Docs/contract-note.diff`.
**Authority:** the contract is the lane's declaration, not prose; the L1 decides whether a `note`
cell may be rewritten in place, which is why this is a patch and not an appended block.

**D5 — `corpus/QUALITY.md:411` (KQ75) cites two replay-tool lines that do not hold the code it
describes.** Command: `grep -n 'def compare\|add_argument("--compare"' tools/kama-live-replay.py`
→ `198 def compare`, `446 --compare`; the stable projection is the docstring list at `:17-26` and
`projection()` at `:168-196`, while `:154-175` is `evaluated`/`_get`/the start of `projection` and
`:397` is a selftest negative case. Evidence row 17: the same pointers were already wrong at the
base (`:194`, `:435`), so the row was mis-cited at integration rather than moved by this build.
Fix: the KQ75 bullet in `X1Docs/appended-corrections.md` §2.

## 4. Lines audited and found accurate (no correction)

- `SKILL.md:1475` self-test cell `KLR_SELFTEST pass=22 fail=0` — measured 22 (row 8).
- `SKILL.md:1473` event/summary line shapes and exit map 0/1/2; `SKILL.md:1474` "as v4" exit map;
  `corpus/README.md:954-960` and `:1026-1028` (round-48 pins), `:906-908` (build/base commits).
- `corpus/QUALITY.md:387` (KQ67), `:409` (KQ73), `:410` (KQ74): commands still exit as stated at
  this tip (`"regressed": 0`; `receipt-provenance-check.py` → `receipts=3 bound=1`, row 14).
- `corpus/knowledge/llamacpp-loading-lifecycle.md:434-441` (round-47/48 observations).

## 5. Risks and limits of this audit

- **The build is code-only, so nothing forced the docs to move.** The most load-bearing omission is
  `SKILL.md`'s silence on `--witness-dir`: an operator following the registry verbatim replays
  without a witness, and the replay still exits 0 and matches — the witness is recorded, never
  compared, so `released: false` (a forgotten `release` file) also matches. Only the C1 counter's
  live leg makes a witness evidence. The drafted rows say exactly that.
- **The witness has no selftest case in the live tool.** `grep witness tools/kama-llamacpp-live.py`
  reaches only the docstring, argparse and `hold_for_witness`; `_selftest` does not call it
  (evidence row 11). At the tip the replay's own selftest (22 cases) also has no witness case; the
  live tree has since gained a `witness-passthrough` case in `tools/kama-live-replay.py`'s selftest
  (a sibling's landing, visible in the re-diff, not measured by me). At the audited revision the
  witness path's only automated coverage is the round-49 C1 counter; I did not re-run C1 (network,
  3 servers) — the L1's dry run stands.
- **The additive `definition: "v4"` key is unannounced.** The schema string deliberately stays
  `append-only-audit/v3`; nothing in `tests/` asserts the JSON key set (checked), so no test breaks,
  but a consumer keyed on the old shape learns about v4 only from the docstring until the registry
  row lands.
- **My pointers resolve at `74558c71`, not at whatever integration commits.** The live tree has
  changed eight files since the build, including both tools, so a drafted correction's `:NNN`
  must be re-resolved against the integration tip (`git show <tip>:tools/append-only-audit.py`)
  before it lands; I did not re-derive them against a moving target.
- **Pointer drift is mechanical and will recur.** Nine of the twenty sites are bare `:NNN`
  citations into a tool whose docstring grows every round; the appended blocks correct today's
  numbers but do not stop the mechanism (a stable anchor, e.g. function name rather than line, is a
  drafting choice for the L1, not something I changed).
- **`corpus/lessons/round-49.md` is not at the tip** (it exists only in the live tree), so I did not
  audit it; the lesson/SCORECARD/LOG entries remain the scribe items named in the assignment.

## 6. Deliverables and hygiene

Written (nothing else touched; no tool installs; no service started; no llama-server of mine left
running — `pgrep -f llama-server` shows only peer scratch):

- `.ufo/waves/round-49/w1/out/X1Docs.md` (this report)
- `.ufo/waves/round-49/w1/out/X1Docs/appended-corrections.md` — four appended blocks (two of them
  redundant with the in-flight landing, marked) and the two patch descriptions, in append-only
  form, each naming the superseded lines
- `.ufo/waves/round-49/w1/out/X1Docs/drift-table.tsv` — 20 drift sites, claim/measurement/class
- `.ufo/waves/round-49/w1/out/X1Docs/contract-note.diff`
- `.ufo/waves/round-49/w1/out/X1Docs/replay-docstring.diff`
- `.ufo/waves/round-49/w1/out/X1Docs/evidence/` — the 17 command outputs cited above
  (`kq75-pointers.out`, `live-tree-rediff.out` back evidence rows 17 and 18)

Status of the six drafted items at hand-off: §1 (`SKILL.md` registry rows) and §4 (knowledge append) are
redundant with integration text that landed in the live tree while this seat worked and should not
be applied twice; §2 (KQ70/KQ71/KQ72/KQ75) and §3 (`corpus/README.md` pointers and the substring
sentence) are still owed — the live tree re-check shows the six `append-only-audit.py:NNN`
citations and KQ75's two replay pointers unchanged; §5 (contract note) and §6 (replay docstring)
are still owed.
