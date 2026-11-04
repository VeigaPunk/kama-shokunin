#!/usr/bin/env python3
"""Build .ufo/waves/round-75/w1-spec.json (one v1 wave, 13 seats)."""
import json

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
R = ".ufo/waves/round-75/w1"
GODSPEED = (
    "/skill:godspeed\nYou are a Godspeed-enabled subagent.\n\n"
    "1. **Name the axes.**\n2. **Iterate cheap, in parallel.**\n"
    "3. **Keep moves that improve any axis and harm none.**\n"
    "4. **Don't aim \u2014 let the frontier walk itself.**\n\n"
    "## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches.\n\n"
)

CONTEXT = """# Goal
kama lane, round 75: ONE v1 wave of 13 seats (build + attack). The round's three claims are FROZEN in
@@LANE@@/plans/round-75-claims.md — read it in full before your item. Predicates, counters, kill rules and
the control receipts are fixed there. A rule changed after a seat has scored is not the claim's rule: report
a disagreement in your report; never edit the freeze, a byte-frozen tool, or another seat's file.

Lane repo: @@LANE@@. Base revision dc58e51315e79d36df5fc530c95fbd3aecbf7593; freeze commit
0908bab5cbf0ab6b435144fc525a3e18443dc08f. Every path you write is absolute and under that repo unless your
item says otherwise. Every `Report:` trailer path a tool renders for you is relative to
@@LANE@@ — write your report at @@LANE@@/<that path> (e.g. @@LANE@@/.ufo/waves/round-75/w1/<Seat>/report.md).

# Bounds
- Write ONLY the files your item names plus your own report. Never edit @@LANE@@/plans/round-75-claims.md; never
  edit a byte-frozen tool (tools/round42-selfdesc-reconcile.py, tools/round72-*.py, tools/round73-*.py,
  tools/append-only-audit.py); never touch another seat's file. tools/round74-*.py is editable ONLY by the
  seat whose item names it.
- Never run a mutating git or jj command in the lane repo (no add/commit/push/fetch/checkout/reset/stash/
  switch/pull; no jj commit/new/describe/squash/rebase/abandon/bookmark/undo). Read-only git (log, show,
  diff, status, rev-parse, ls-files, cat-file, merge-base) is fine. Any fixture repo is
  `D=<scratch>/fixture && mkdir -p "$D" && git -C "$D" init -q`, every later git call names -C "$D", and
  `git -C "$D" rev-parse --show-toplevel` must equal $D before the first commit. Never `git commit` or `jj`
  anywhere else.
- Never write to the fleet repo (/home/vgpnk/Projects/shokunin outside kama-shokunin), to sibling lanes, to
  .ufo/state/, .ufo/watchdog.log, .scratch/, MANIFEST.json, templates/ or scripts/.
- Scratch root: /fast/scratch/hyaku/kama-r75/<your-seat-name>/ — mkdir -p it, pass it explicitly (TMPDIR=…,
  --work, mkdtemp(dir=…)), never rely on an inherited TMPDIR. /tmp only for files under 50 MB, never cited as
  evidence. Delete your scratch dir before you yield (trap 'rm -rf -- "$S"' EXIT / finally: shutil.rmtree)
  after copying receipts into your report dir; a seat that ends with its tree on disk reports that as its own
  defect. One live clone per seat: `git clone --shared @@LANE@@ <scratch>/clone`.
- You are a leaf: no swarm and no task call. Only an executor may spawn one read-only labrat probe, and none
  of these items needs one.
- Tooling authorization (operator 2026-10-19): you may install or upgrade tools that help the task — read
  /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate; record tool/version/channel/
  reason in your report). pacman guard (orchestrator ruling 2026-10-20): all pacman transactions are PAUSED
  host-wide — no pacman -S/-Sy/-Syu/-U/-R/-Sy <pkg> or any partial upgrade; install via uv tool / npx / an
  official binary in ~/.local/bin, or report the need instead.
- Never message agent://all; message only your L1 by id (KamaR75), and only when blocked.
- Honesty: an unrun check has not passed. Report the exact command, its exit code and the output line you
  rely on; name dead ends and disagreements.
"""


def sub(text):
    return text.replace("@@LANE@@", LANE).replace("@@R@@", R)


def item(name, role, axes, prompt):
    return {
        "name": name,
        "role": role,
        "axes": axes,
        "milestone": "kama r75 w1",
        "prompt": GODSPEED + sub(prompt),
    }


items = []

items.append(item("EX01Pins", "executor", ["calibration"], """# C1 build — @@LANE@@/tools/round75-interpretation-pins.py

Read @@LANE@@/plans/round-75-claims.md section C1 in full; its predicate blockquote is frozen and must appear
verbatim as the module's `PREDICATE` constant.

## Target
Build the counter that binds the lane's two routed interpretation debts to boundary fixtures with kill arms.

## Steps
1. Read @@LANE@@/tools/round74-selfdesc-canon.py (`total = set(canon_names) | demonstrated`; `resolve()`),
   @@LANE@@/tools/round74-receipt-claim-binding.py (`REVISION_RE`, `_claim_pass_v2`, its `Fixture` helper),
   and @@LANE@@/.ufo/waves/round-74/w1/CRT01Claims/attack.md §F2c for the `nc2_recorded_at_hex` record shape.
2. P1 (older-demonstrated): build a SCORECARD text in `--work` with a bold canon heading at round 71 carrying
   three capability rows and a round-60 table carrying those three names plus two more. Run the committed
   `round74-selfdesc-canon.py` result over it (import it, never edit it): declared reading `total=3`.
3. P1 mutant: copy `tools/round74-selfdesc-canon.py` into `--work`, patch it so names carried only by tables
   strictly older than the canonical round join `total` (the patch in
   @@LANE@@/.ufo/waves/round-75/controls/mutation-control.py `C1_MUTANTS["c1_f1b_older_union"]` is the exact
   text; reuse it, do not invent a different one), and require the mutant to score `total=5`.
4. P2 (revision-mention context): rebuild the `nc2_recorded_at_hex` fixture (receipt header names c0; record
   paragraph `probe recorded at <c1> naming \`r.out\` (content id, not a run revision)`) with the module's own
   fixture/git-init pattern; the committed module must grade it exit 0. Copy + patch the module's
   `REVISION_RE` to the any-hex form (same patch as `C1_MUTANTS["c1_f2c_literal_hex"]`) and require the mutant
   to exit 1 with a `stale-revision` finding.
5. Output: one line `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0`, exit 0 iff both pins'
   declared values are produced by the committed module and both mutants differ (naming each
   `INTERPRETATION_PINS_FINDING <pin> declared=<x> mutant=<y>` on exit 1); exit 2 on could-not-evaluate (a
   module absent beside the counter, fixture build failure, CLI misuse). Support `--repo`, `--work`
   (default `tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))`), `--keep`, `--json`, `--selftest`.
6. `--selftest` must include a cheat arm: a counter variant whose pin accepts the mutant's value as the
   declared value must be reported `escaped` and exit 1 — the selftest proves the counter can fail.
7. Run it against the real lane: `python3 @@LANE@@/tools/round75-interpretation-pins.py --repo @@LANE@@` and put
   the exit code + line in your report. Run `--selftest` too.

## Acceptance
The tool exists, is executable, runs green on the real lane, its selftest passes with the cheat arm red, its
PREDICATE constant normalizes to the plan's blockquote, and no file outside `tools/round75-interpretation-
pins.py` and your report/receipts changed. Report: @@R@@/EX01Pins/report.md."""))

items.append(item("EX02Survivors", "executor", ["operability"], """# C2 build — @@LANE@@/tools/round75-survivor-probe.py + two arms in tools/round74-receipt-claim-binding.py

Read @@LANE@@/plans/round-75-claims.md section C2 in full; its predicate blockquote is frozen and must appear
verbatim as the probe's `PREDICATE` constant.

## Measured before (at the freeze, receipt @@LANE@@/.ufo/waves/round-75/measured/before/control.out)
Five source mutants of `tools/round74-receipt-claim-binding.py` were applied to a shared clone and graded by
the module's own `--selftest`: `c2_case_hex`, `c2_kind_boundary`, `c2_paragraph_scope` are KILLED;
`c2_conflict_off` (the `if len(set(revs)) > 1:` check removed) and `c2_header_window` (`HEADER_WINDOW = 5`
narrowed to 3) ESCAPE at `pass=9 fail=0`. The module docstring declares both behaviours.

## Steps
1. Add two selftest arms to `@@LANE@@/tools/round74-receipt-claim-binding.py` — this seat owns that file for
   the round:
   - `conflicting-headers`: a fixture whose receipt carries two different `rev=<40hex>` headers inside the
     first five lines must grade `unbound` (a finding), never crash; assert the failure kind and exit.
   - `header-window-fifth-line`: a fixture whose receipt names its revision on line 5 of the header block
     (`HEADER_WINDOW = 5`) must still bind; assert exit 0.
   Re-run the module selftest: it must stay green (all arms), and the two mutants above must now be caught.
   Do not weaken any existing arm; do not change the module's grading behaviour on real records.
2. Build `@@LANE@@/tools/round75-survivor-probe.py`: five named source mutations (the exact patches are in
   @@LANE@@/.ufo/waves/round-75/controls/mutation-control.py `C2_MUTANTS`; reuse them), each applied to a copy
   of the committed module in `--work`, each copy's selftest run and required RED, the pristine module's
   selftest required GREEN, and the failing arm named per mutant.
3. Output: one line `SURVIVORS2 mutants=5 killed=5 escaped=0`, exit 0 iff pristine green and all five mutants
   red; exit 1 naming `SURVIVORS2_FINDING <mutant> mutant_exit=<n> arm=<name|none>`; exit 2 on
   could-not-evaluate. Flags: `--repo`, `--work`, `--keep`, `--json`, `--selftest`.
4. `--selftest` cheat arm: a probe whose mutant list is empty (printing killed=5) must be reported red.
5. Decision to record in your report (plan §C2): the same-line inherited kind already has its fixture
   (`same-line-stale-claim`, r74 arm 6) and the probe certifies it load-bearing via `c2_kind_boundary`; no new
   fixture is added for that class.
6. Run `python3 @@LANE@@/tools/round75-survivor-probe.py --repo @@LANE@@` and the module selftest; put exit codes
   and lines in your report.

## Acceptance
Probe green on the real lane (`mutants=5 killed=5 escaped=0`), module selftest green with the two new arms,
the two former escapes now killed, no file outside `tools/round74-receipt-claim-binding.py`,
`tools/round75-survivor-probe.py`, receipts and your report changed.
Report: @@R@@/EX02Survivors/report.md."""))

items.append(item("EX03Accepted", "executor", ["freshness"], """# C3 build — @@LANE@@/tools/round75-append-accepted.py + registry/append-only-accepted.tsv + the contract declaration fix

Read @@LANE@@/plans/round-75-claims.md section C3 in full; its predicate blockquote is frozen and must appear
verbatim as the counter's `PREDICATE` constant.

## Measured before (receipt @@LANE@@/.ufo/waves/round-75/measured/before/control.out)
`python3 tools/append-only-audit.py --repo .` exits 1 with `unrestored=53 ... bad_declarations=5`. Its own
disclosure ledger accepts only commits preceding its introduction (round 51), so all 53 undisclosed events
are post-ledger and cannot be disclosed there.

## Steps
1. Read @@LANE@@/tools/append-only-audit.py's `--json` output shape (docstring lines 1-150, the `undisclosed`
   records, `declarations`, `summary`) and @@LANE@@/registry/append-only-contract.tsv.
2. Write `@@LANE@@/registry/append-only-declarations.md`: one line per contract row that does not bind today
   (`SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`),
   each line naming the path token and saying append-only, with a one-line reason. Re-point those five
   `declared_at` cells in `@@LANE@@/registry/append-only-contract.tsv` at the new file:line. Verify
   `python3 tools/append-only-audit.py --repo . --json` now reports `bad_declarations=0` and every contract
   row `ok=True`.
3. Generate `@@LANE@@/registry/append-only-accepted.tsv` mechanically from the audit JSON: header
   `commit<TAB>file<TAB>line_sha256<TAB>count<TAB>class<TAB>note`, one row per `undisclosed` entry of every
   event (`count` = that entry's count, `class` = the entry's mechanical class), `note` =
   `<commit subject>; <why it is accepted history>`. The note must come from
   `git -C <repo> log -1 --format=%s <commit>` plus a reason table: the largest event
   (`ea33a78f2b0b`, 639 deletions, round-65 S537 LF re-land) is a CRLF->LF normalization class and its note
   cites `S547` (gitattributes(5) "Line endings are normalized to LF in the index every time the file is
   checked in", opened this round); the rest are in-place header/prose edits superseded by the round that
   followed. Commit no reasoning into any historical file: the register is the ledger.
4. Write `@@LANE@@/tools/round75-append-accepted.py`: reads the frozen audit's JSON (subprocess, exit code
   tolerated 0 and 1, its output parsed, never edited), grades the register, prints
   `APPEND_ACCEPTED events=<e> accepted=<a> unaccepted=<u> bad_rows=<r> bad_declarations=<d>`, exit 0 iff
   every undisclosed event is covered by hash-matching rows and bad rows and bad declarations are 0; exit 1
   naming `APPEND_ACCEPTED_FINDING <unknown-event|hash-mismatch|count-short|class-mismatch|restored-event|
   duplicate|bad-declaration> <detail>`; exit 2 on could-not-evaluate. Flags `--repo`, `--audit-json`,
   `--register`, `--json`, `--selftest`.
5. `--selftest` with three negative controls, each red: a register row with a wrong `line_sha256`; a row
   naming a restored event; a row whose class differs from the event's mechanical class. Plus a `wc -l`
   cheat arm (53 rows, no hashes) that must be rejected.
6. Run on the real lane and put the line + exit code in your report.

## Acceptance
`APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0` exit 0 on the real lane;
`append-only-audit.py` bytes unchanged (sha256 before/after in your report) and still reporting
`unrestored=53`; selftest green with the four negative arms red. Report: @@R@@/EX03Accepted/report.md."""))

items.append(item("SCR01Sources", "scribe", ["freshness", "expansion"], """# Frontier — SOURCES row S547 (gitattributes) and its re-grounding

Read @@LANE@@/CORPUS.md (registry rules), @@LANE@@/corpus/SOURCES.md's table shape (one full row, e.g. S546) and
@@LANE@@/plans/round-75-claims.md §Frontier step.

## Target
Append exactly ONE row, S547, for `gitattributes(5)` — the id is reserved in the freeze. The row grounds
C3's largest accepted-history class.

## Steps
1. Re-open the source yourself this round: `curl -sL --max-time 60 https://git-scm.com/docs/gitattributes`
   into your scratch, record bytes + sha256 + access date. The round's retained copy is at
   @@LANE@@/.ufo/waves/round-75/w1/sources/gitattributes.html — compare your fetch against it and say whether
   they are byte-identical.
2. Locate the quote inside the `text` attribute paragraph (end-of-line conversion): the located fragment is
   `Line endings are normalized to LF in the index every time the file is checked in` (16 words, ≤25). Give
   the section/anchor you found it under.
3. Write the row in the exact 11-column schema used by S546 (id, title — URL, kind, tier, teaches, anchor,
   quote-grounding, status, opened date, recheck, used-by). Tier A; status `mined`; used-by names
   `corpus/knowledge/append-only-accepted-history.md` (SCR03 writes that entry with `source: S547` this round).
4. Before appending, run the scratch-mirror census gate exactly as round 74 did: copy `corpus/` to your
   scratch, add your row to the mirror, run
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <scratch>/corpus/SOURCES.md` and
   require exit 0 (warnings allowed) BEFORE the real append. Commit the pre-append receipt and the post-append
   census into your report dir.
5. Append-only: never rewrite an existing row line; your row is appended at the table's end.

## Acceptance
`corpus/SOURCES.md` carries S547 exactly once, the census (`sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama`) exits 0, and the row's quote, anchor, date and used-by are re-derivable
from your receipt. Report: @@R@@/SCR01Sources/report.md."""))

items.append(item("SCR02QualityMap", "scribe", ["calibration", "coverage"], """# Duties 1 and 2 — the coverage-map row for round 74 and three QUALITY.md criteria

Read @@LANE@@/corpus/README.md's `## Coverage map — round 73 addition` block (the shape to follow) and
@@LANE@@/corpus/QUALITY.md's criterion rows (KQ numbering, the last row's number).

## Target
Close round-74 routed defects 1 and 2.

## Steps
1. Coverage map: append a new `## Coverage map — round 74 addition (2026-11-04)` section at the END of
   `corpus/README.md` (never insert; no existing line moves). Before appending, measure
   `ls corpus/knowledge/*.md | wc -l` and `grep -c '^| \`knowledge/' corpus/README.md`, and state how many
   files remain unindexed after your block. The block must index
   `knowledge/host-block-base-revision.md` (what it covers, round 74) and name the remaining map gap list.
2. QUALITY.md: append three criteria, each citing `corpus/lessons/round-74.md` §Mistakes and each at the
   lane's bar (a criterion a later round can run): (a) number-drift between a wave spec's prose seat count and
   its `items` array — the count is recomputed from the items, never restated; (b) record-before-census order
   — a registry append is preceded by an exit-0 scratch-mirror census receipt, never followed by it;
   (c) concurrent writer on a seat's declared path — one file, one writer per round, and a second writer
   re-lands from the committed blob instead of rewriting. Number them after the current last KQ id (read the
   file; do not guess).
3. Both files are append-only in their declared regions: append only, never edit or reorder an existing line.

## Acceptance
`corpus/README.md` has the round-74 block with the measured before/after counts; `corpus/QUALITY.md` has three
new criteria with distinct KQ ids citing round-74's lesson; `git diff --numstat` for both files shows zero
deleted lines. Report: @@R@@/SCR02QualityMap/report.md."""))

items.append(item("SCR03Know", "scribe", ["freshness", "expansion"], """# Knowledge entry — corpus/knowledge/append-only-accepted-history.md

Read @@LANE@@/plans/round-75-claims.md §C3 and §Frontier step, @@LANE@@/tools/append-only-audit.py's docstring
(the disclosure rule and why post-ledger events cannot be disclosed), and
@@LANE@@/corpus/knowledge/host-block-base-revision.md as the shape to follow.

## Target
Write ONE new knowledge entry that states what the accepted-history register grades and what it does not.

## Steps
1. Required content: the audit's three classes (`restored`, `disclosed`, `undisclosed`), the ledger
   introduction cutoff that makes the 53 post-ledger events undisclosable, the register row schema
   (commit/file/line_sha256/count/class/note) and the rule that a row is machine-bound to an event the audit
   computes, the largest class (round-65 `ea33a78f2b0b` S537 CRLF->LF re-land, 639 deletions) with its reason
   and the `S547` gitattributes quote, and the limit: the register never lowers the audit's `unrestored`
   count and never re-stamps a historical receipt.
2. Frontmatter/header must carry `source: S547` (the row SCR01 appends this round; the id is reserved in the
   freeze) plus the section's usual provenance fields — copy the field shape from a recent entry.
3. If `registry/append-only-accepted.tsv` is not yet on disk when you write, derive the numbers from
   `python3 tools/append-only-audit.py --repo @@LANE@@ --json` yourself and say which revision you measured;
   never invent a count.
4. Append-only entry: no existing file is edited.

## Acceptance
Entry exists, ≤ ~120 lines, every number re-derivable by the audit command you name, `source: S547` present,
its claims consistent with the register/tool as landed. Report: @@R@@/SCR03Know/report.md."""))

items.append(item("SC01Recon", "scout", ["freshness", "coverage"], """# Recon — the source, the audit's undisclosed set, and the surrounding surface

Read-only seat: findings only, no production edits.

## Target
Independently verify the two byte-level facts C3 and the frontier step rest on, and map the surface the
register will cover.

## Steps
1. Fetch `https://git-scm.com/docs/gitattributes` yourself (live), into your scratch. Compare digest and byte
   count against @@LANE@@/.ufo/waves/round-75/w1/sources/gitattributes.html; locate the `text`-attribute
   end-of-line quote and report the anchor and the word count of SCR01's planned fragment. Say if the page
   changed.
2. Re-derive the audit's undisclosed set independently: for each of the 53 entries `tools/append-only-audit.py
   --json` reports under `undisclosed`, check with `git -C @@LANE@@ log --format=%H --name-status`/`git show`
   that the commit really deletes lines of that file and that the count is plausible; report any event where
   the JSON and the git history disagree (that would be an instrument defect).
3. Class census: group the 53 events by file, by commit era (pre/post round 60), and by mechanical class; name
   the top three and the one event that most needs a human reason. State which events are line-ending noise
   (round-65 S537 re-land) and which are content edits.
4. Cross-check the contract: list every contract row, its `declared_at`, and whether the line binds today
   (run the audit with `--json` and read `declarations`); name the five that do not and why.

## Acceptance
A findings report with commands + exits + digests, no production edit, and an explicit list of any
disagreement between the audit's JSON and git history. Report: @@R@@/SC01Recon/report.md."""))

items.append(item("CON01Overlap", "connector", ["adjacency"], """# Sibling-overlap scan — who else grades append-only history or mutation survivors

Read-only seat: findings only, no production edits.

## Target
Name every sibling surface that already does what round 75's three instruments do, so the lane's adjacency
row and the report's cross-domain line are grounded, and so no kama claim duplicates a sibling's tool.

## Steps
1. Search the sibling lane repos under /home/vgpnk/Projects (read-only) for: an append-only/deletion audit, a
   mutation-survivor probe, an interpretation-pin counter, and an accepted-history register. Use `grep -l`
   over `tools/`, `scripts/`, `registry/` of each lane (skip huge trees; a bounded `rg -l` per repo is fine).
   Name file:line for every hit and say whether it duplicates kama's or is a different surface.
2. Read @@LANE@@/corpus/knowledge/cross-lane-scope.md and say which rows this round's instruments belong to, and
   which are contested scope to report rather than absorb (kumitate owns orchestration/gates; kotoba owns
   prompt/skill craft; tameshi owns its binding gate).
3. Mine `considerthese/` (operator-authored, read-only): list every proposal in the newest file and mark which
   are still unimplemented in the lane; name at most ONE that fits this round's claims, or say none does.
4. Report the cross-domain evidence line the round report must carry (domain + what it belongs to).

## Acceptance
A findings report with file:line hits across siblings, the cross-lane-scope row mapping, the considerthese
disposition, and one cross-domain line. No production edits. Report: @@R@@/CON01Overlap/report.md."""))

items.append(item("RV01PinsReview", "reviewer", ["calibration"], """# Attack C1 — are the two interpretation pins load-bearing?

Read @@LANE@@/plans/round-75-claims.md §C1 and the C1 predicate verbatim. Read the built counter
@@LANE@@/tools/round75-interpretation-pins.py and the two frozen modules it grades. If the counter is not on
disk yet when you start, wait for it by re-reading the path (it is the round's C1 deliverable) and otherwise
review the frozen spec and report the absence as your finding.

## Target
Try to make C1 green without the declared reading, and try to make the declared reading wrong.

## Steps
1. Build your OWN fixtures in your scratch (do not reuse the counter's): a canon at round 71 plus an older
   table with extra names; a `recorded at <hex>` paragraph. Score: does the committed module really produce
   `total=3` and exit 0? Is `total=3` the defensible reading (what would `total=4`/`5` mean for the lane's
   self-description)?
2. Attack the counter: a hardcoded print, a pin whose mutant equals its declared value, a mutant that changes
   nothing semantically, a fixture that both readings satisfy. Score each with the frozen counter and say
   whether it is caught.
3. Re-derive the plan's two control claims: the older-union mutant and the literal-hex mutant really do
   escape the base modules' selftests (re-run them yourself from a shared clone).
4. Verdict per pin: load-bearing / not / under-specified, with the command and exit that decides it.

## Acceptance
An attack report naming every attempt, its command and exit, and a per-pin verdict; no edit to the counter,
the modules or the freeze. Report: @@R@@/RV01PinsReview/report.md."""))

items.append(item("CR01Falsify", "critic", ["calibration"], """# Attack all three claims — cheapest control that meets each counter

Read @@LANE@@/plans/round-75-claims.md in full. Your job is to defeat the claims, not to confirm them.

## Target
For each of C1, C2, C3: build the cheapest artifact that skips the claimed work and score it with the frozen
counter. If any such control meets the target, the target or the counter is wrong — say so with the receipt.

## Steps
1. C1: a counter stub that prints the target line; a pin set whose mutants do not differ; a fixture that both
   readings satisfy. Score each.
2. C2: a probe whose mutant list is empty or whose mutants are no-ops; a probe that runs the selftest but
   ignores its exit; the module with the two new arms weakened while the probe stays green.
3. C3: a register of 53 rows with fabricated hashes; a register of 53 rows copied from a single event; a
   register that names restored events; a contract edit that makes a row bind by renaming the path token to a
   word the declaring line already carries (that would be a false declaration — test whether the audit
   accepts it).
4. Also test the do-nothing control: base bytes, no tools — confirm no counter can be met by inaction.
5. Verdict per claim: `holds` / `fallen` / `under-specified`, each with the control's command and exit.

## Acceptance
Every control you built is named with its command, exit and output line; no production edit; if a claim falls,
the report says which counter change would fix it. Report: @@R@@/CR01Falsify/report.md."""))

items.append(item("MT01Mutants75", "mutation-tester", ["operability"], """# Mutation test the three new instruments

Read @@LANE@@/plans/round-75-claims.md §C1-§C3 and the three tools once they land
(`tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py`,
`tools/round75-append-accepted.py`). If one is still absent when you start, mutate the ones present and
report the absent one as `not-landed` (never as passing).

## Target
≥4 behaviour-bearing mutants per landed module, with the survivor set named exactly.

## Steps
1. Work in ONE shared clone per module in your scratch; never edit the lane tree.
2. Mutant classes to cover: comparison flips on the target counters (`declared`, `killed`, `accepted`,
   `unaccepted`, `bad_rows`), exit-code flips (finding -> 0, clean -> 1), scope cuts (grade one pin/event
   instead of all, skip the mutant leg, skip the pristine leg), input-trust cuts (accept any register row,
   accept the mutant's value as declared), and selftest-oracle tampering (assert-True style).
3. For each mutant, run the module's `--selftest` AND its real-lane command; classify killed (some arm or the
   real run goes red) or escaped. For each escape, name the arm that should exist and the fixture it needs.
4. Report `MUTANTS75 <module> applied=<n> killed=<k> escaped=<e>` per module, with the escaped mutants' exact
   patches (diff text) so the L1 can decide.

## Acceptance
A mutants matrix (md) plus the raw harness output, per-mutant patch and result, no lane edit, scratch removed.
Report: @@R@@/MT01Mutants75/report.md."""))

items.append(item("SN01Register", "sentinel", ["calibration"], """# Security review — the accepted-history register and the declaration repair

Read @@LANE@@/plans/round-75-claims.md §C3 and @@LANE@@/tools/append-only-audit.py's disclosure rule (docstring
lines 1-40). Read the landed register and contract once they exist.

## Target
Show whether the register weakens the lane's append-only guarantee, and whether the declaration repair is real.

## Steps
1. Threat model: a future round deletes 100 lines of `SCORECARD.md`, then writes register rows naming them.
   Does anything in the landed tooling stop that? The audit's own rule (post-ledger deletions are restored,
   never disclosed) must stay intact; if the register can absorb a fresh deletion, that is a finding with a
   severity and a fix (e.g. the counter requires the event's commit to precede the register's introduction
   commit — test whether it does).
2. Test the counter's rejections on your own fixtures: restored event, wrong class, wrong hash, duplicate rows,
   a row for a commit the audit does not compute.
3. Declaration repair: can a row be made to bind by pointing `declared_at` at a line that happens to carry the
   token word without declaring the file append-only? Test one such line and report whether `binds()` accepts
   it (that is a pre-existing tool property, not this round's change — say which it is).
4. Check the register file itself is append-only-declared or otherwise bounded (a register that can be edited
   in place is a hole).

## Acceptance
A threat table (attack, cost, caught-by, severity, fix) with commands + exits; no production edit; an explicit
statement whether the round's change weakens the audit. Report: @@R@@/SN01Register/report.md."""))

items.append(item("REV01Semantics", "revenger", ["depth"], """# Reverse-engineer the readings from committed bytes

Read @@LANE@@/plans/round-75-claims.md §C1 and §C2. Do not trust docstrings first; derive the behaviour.

## Target
An independent, byte-level statement of the two interpretation readings (F1b, F2c) and the five C2 mutant
classes, so the pins can be checked against what the code actually does rather than what it says.

## Steps
1. From `tools/round74-selfdesc-canon.py` at the freeze commit, derive: which names enter `total`, which enter
   `demonstrated`, what happens to names carried only by tables older than the canonical round, and what
   happens when the canonical round is newer than every other table. Cite line numbers.
2. From `tools/round74-receipt-claim-binding.py`: derive the exact condition under which a 40-hex token binds
   a cited receipt (the `elif rev_mentions` branch), what a `recorded at <hex>` paragraph does, and what the
   `_claim_kind` boundaries are (distances). Cite line numbers.
3. Re-derive the two F2c/F1b readings by running the modules over minimal fixtures you build; show the exact
   output lines. Compare with what the plan declares: agree/disagree per reading.
4. Derive the five C2 mutant classes from the code: for each, the smallest source edit and the code path it
   breaks, and whether a selftest arm exists for it at base (file:line).
5. Name any third reading the code leaves free (an ambiguity neither the plan nor the docstring pins), with
   the fixture that would show it.

## Acceptance
A findings report with line-cited derivations, run outputs, and an agree/disagree table against the plan; no
production edit. Report: @@R@@/REV01Semantics/report.md."""))

spec = {
    "wave": "kama-r75-w1",
    "milestone": (
        "kama r75 w1 (v1, 13 seats: 3 executor, 3 scribe, 1 scout, 1 connector, 1 revenger, "
        "1 reviewer, 1 critic, 1 mutation-tester, 1 sentinel)"
    ),
    "reportDir": R,
    "maxLanes": 13,
    "axes": ["calibration", "operability", "freshness", "adjacency", "expansion", "depth"],
    "context": CONTEXT,
    "items": items,
}

with open(LANE + "/.ufo/waves/round-75/w1-spec.json", "w", encoding="utf-8") as fh:
    json.dump(spec, fh, indent=1, ensure_ascii=False)
print("items", len(items), "roles", sorted({i["role"] for i in items}))

# Dispatch-shape check (lesson Mistakes 4): the emitted spec is the plan source, but the
# in-session dispatcher reads taskCall.context + taskCall.tasks. Assert on the loaded
# dispatch JSON, never on the emit flag.
import sys as _sys

_dispatch = _sys.argv[1] if len(_sys.argv) > 1 else ""
if _dispatch:
    _d = json.load(open(_dispatch, encoding="utf-8"))
    assert isinstance(_d, dict) and isinstance(_d.get("taskCall"), dict) \
        and isinstance(_d["taskCall"].get("tasks"), list) \
        and isinstance(_d["taskCall"].get("context"), str), \
        "dispatch %s carries no taskCall{context,tasks} (an --emit-tasks array is not a dispatch)" % _dispatch
    assert len(_d["taskCall"]["tasks"]) == len(items), "dispatch task count differs from the spec"
    print("dispatch ok", _dispatch, "tasks", len(_d["taskCall"]["tasks"]))
