#!/usr/bin/env python3
"""Build the round-81 wave-1 spec (one v1 wave, 14 seats) from the frozen claims plan.

Every prompt is absolute-path scoped to the lane and carries the same hard-rules block.
Run: python3 .ufo/waves/round-81/build-spec.py  -> writes w1-spec.json beside this file.
"""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
WAVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81"
SCRATCH = "/fast/scratch/hyaku/kama-r81"
BASE = "e7d2fd729cf8204c89c32534303bc9f2a97fcee4"
SEALED = "a2af1af59faf6cf66fe854559293c4e4b441aff3"

GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
kama lane, round 81: ONE v1 wave of 14 seats (build + attack) against the frozen claims in
{LANE}/plans/round-81-claims.md — read that file in full before your item and treat its
blockquote predicates, fact value strings, target lines and control lists as frozen text.
Base revision {BASE} (round-80 closure tip); the sealed revision C1 grades is {SEALED}
(the round-80 record tip). Lane tip is read with `git -C {LANE} rev-parse master` (git HEAD is
detached after the first helper commit; never `@{{u}}` or `--abbrev-ref HEAD`).

# Write scope (hard)
You may write ONLY inside your own seat directory under {WAVE}/w1/<YourSeatName>/.
The lane tree {LANE} is READ-ONLY for every seat this round: the L1 owns every production file
(tools/, registry/, corpus/, SCORECARD.md, LOG.md, plans/). Draft what an item asks you to draft
inside your seat dir; the L1 files it. Never touch the fleet root /home/vgpnk/Projects/shokunin
(no MANIFEST.json, templates/, scripts/, .ufo/state/, .ufo/watchdog.log, .scratch/,
l0-questions.md), never a sibling repo, never /home/vgpnk/Projects/shokuknow. An item that names no
path is read-only outside its seat dir.

# VCS rules (hard)
Never run git commit/push/stash/checkout/switch/reset/pull, never any mutating jj command, never
`git add`; the L1 is the only committer. Read-only git (log/show/diff/status/ls-files/rev-parse/
merge-base/ls-tree/cat-file) is fine. Any fixture or clone repo is created under your scratch root as
`D=$(mktemp -d -p "$S") && git -C "$D" init -q` / `git clone --shared {LANE} "$S/clone"`, and every later
git/jj call names `-C "$D"`; verify `git -C "$D" rev-parse --show-toplevel` equals `$D` before any use.
Never run a git write in the lane.

# Scratch (hard)
Every clone, fixture, work tree or scratch registry lives under $S = {SCRATCH}/<YourSeatName>/
(mkdir -p it; export TMPDIR=$S). /tmp is for files under 50 MB only. Delete $S before you yield
(trap 'rm -rf -- "$S"' EXIT; Python: finally: shutil.rmtree) after copying receipts into your seat dir.
A seat that leaves its tree reports that as its own defect. Never mirror the whole lane into a wave dir.

# Absolute paths
Your tools start at the fleet root, not the lane. Every path you read or write must be absolute under
{LANE} or your seat dir. Every `Report:` trailer path the dispatch shows is relative to {LANE} — write
it at {LANE}/<that path> (that is, under {WAVE}/w1/<YourSeatName>/).

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task: read /home/vgpnk/.omp/agent/RULES.md first
(official channels, update-safety gate; record tool/version/channel/reason in your report). All pacman
transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via `uv tool`, `npx`, or an
official binary into ~/.local/bin; never -Sy/-Syu/-U/-R, never restart a host service. Named items
require no installs.

# Claims (frozen; do not edit the plan)
C1 calibration: `python3 tools/round81-selfrecord-round80.py --repo .` must print
`SELFRECORD_R80 claims=6 mismatches=0 corrected=6 unbacked=0`, exit 0. The six facts F1–F6 and their
value strings are tabulated in the plan; all six are stale at the base and their corrections
(`corrected F<n> old=… new=… at={SEALED} date=2026-11-04`) live in `corpus/lessons/round-81.md`
§Corrections with the appended `#### round-81 correction` record block.
C2 operability: `python3 tools/round81-append-debt.py --repo . --round 81` must print
`APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=<p> unaccepted=0
bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0, over `registry/append-only-late.tsv`
(88 rows over ten round-79/80 events) and the re-pointed pre-report gate arm 8.

# Seat rules
You are a leaf. An executor may spawn at most one read-only labrat probe; no other role spawns anyone
and no seat runs a swarm. Never message agent://all; message nothing outside your item. Do not commit,
do not edit a production file, do not run pre-report-gate.py in scored mode (the L1 does). Sibling seats
run at the same time: a module an item needs may be missing at your start — poll for it (`sleep 30`, up
to 25 minutes) before grading, and report honestly if it never lands. A dead seat stays dead in the
evidence: report every failure with its last error text, never fabricate a run. Report every receipt as
an absolute path plus its command and exit code.
"""


def item(name, role, axes, prompt):
    return {"name": name, "role": role, "axes": axes, "milestone": "kama r81 w1",
            "prompt": GODSPEED + prompt}


ITEMS = [
    item("SC01DebtInventory", "scout", ["operability"], f"""# SC01 — independent inventory of the round-79/80 append-only debt (scout)
Do not read `tools/round81-append-debt.py` or `tools/round81-late-rows.py` if they exist (they are the
objects under test). From committed bytes only:
1. Run `python3 {LANE}/tools/append-only-audit.py --repo {LANE} --json > $S/audit.json` (exit code
   matters; it exits 1 with findings). From that JSON, enumerate every event with `status=unrestored`
   whose commit is ancestral to {BASE} (`git -C {LANE} merge-base --is-ancestor <c> {BASE}`), and for
   each: commit, file, the `undisclosed` entries' `line_sha256`, `count` and `classes`, and the commit
   subject (`git -C {LANE} log -1 --format=%s <c>`).
2. Write `$S/inventory.tsv` (one row per undisclosed line: commit, file, line_sha256, count, class) and
   `$S/INV.json` with the per-event totals and the grand total of lines.
3. If `{LANE}/registry/append-only-late.tsv` exists when you finish, diff its rows against your
   inventory cell-by-cell (commit, file, hash, count, class) and report `match` or every mismatch.
4. Report which commits/events the frozen `registry/append-only-accepted.tsv` already covers and why the
   remainder is exactly ten events, and whether any event has more than one mechanical class (that would
   make a single `class` cell ambiguous).
Copy `inventory.tsv`, `INV.json` and your audit command/exit receipt into {WAVE}/w1/SC01DebtInventory/."""),

    item("EX01FactRederive", "executor", ["calibration"], f"""# EX01 — independent re-derivation of the six round-80 facts (executor)
Write `$S/rederive.py`; do NOT open `tools/round81-selfrecord-round80.py` until your six values are
fixed. Re-derive each fact of the round-80 self-record from `git -C {LANE} show {SEALED}:<path>` and the
receipts at the sealed revision:
F1 §Round 80 C1 row's declared selftest tally vs `.ufo/waves/round-80/measured/after/c1-selftest.out`;
F2 C3 row's tally vs `…/measured/after/c3-selftest.out`; F3 the `## Axes` calibration row's tally vs the
C1 selftest receipt; F4 the `LOG.md` §Round 80 C1 bullet's tally vs the C1 receipt; F5 the coverage row's
last-change cell vs that same row's evidence cell (which round does the evidence name?); F6 the
calibration row's "newest non-author closure" claim vs the newest `corpus/lessons/round-*-verifier-spotcheck.md`
committed at the tip (`git -C {LANE} ls-tree -r --name-only master corpus/lessons/` plus `git log -1
--format=%s -- <path>`).
Emit `EX01.json` with per fact `declared`, `observed`, `match`, plus `stale` and `agreement` against the
lane counter (run `python3 tools/round81-selfrecord-round80.py --repo {LANE}` once it exists; if absent
after 25 minutes say so). Look for a seventh stale fact the record declares; name it if one exists.
Copy the script and JSON into {WAVE}/w1/EX01FactRederive/."""),

    item("EX02CutoffProbe", "executor", ["operability"], f"""# EX02 — executable proof of C2's premise: the frozen acceptance rule cannot be satisfied (executor)
Prove, with a fixture, that `tools/round75-append-accepted.py`'s rule rejects any row for an event made
after the register's introduction, and that the disclosure ledger cannot bless it either.
1. Clone the lane into `$S/clone` (`git clone --shared {LANE} "$S/clone"`, `git -C "$S/clone"
   rev-parse --show-toplevel` must print `$S/clone`).
2. Choose one of the ten unaccepted events the audit reports at {BASE} in `$S/clone` (e.g.
   `4af44f78303f04a6ea32ea62cac586f89688d73a` on `corpus/lessons/round-79.md`). In the fixture, append a
   syntactically perfect row for one of its undisclosed lines to `registry/append-only-accepted.tsv` in a
   NEW commit (`git -C "$S/clone" commit -m "fixture: accept"`), then run
   `python3 "$S/clone/tools/round75-append-accepted.py" --repo "$S/clone"` and record the exact
   `APPEND_ACCEPTED_FINDING post-introduction …` line and exit code.
3. Diagnose the mechanism in `tools/round75-append-accepted.py` (`grade()`'s `precedes()` and how `intro`
   is resolved) and in `tools/append-only-audit.py` (the disclosure ledger's own pre-introduction rule,
   its docstring lines about "a ledger read from <to> may only disclose commits that precede its own
   introduction"): quote the code lines by number.
4. Also show the frozen register's introduction commit (`git -C "$S/clone" log --diff-filter=A
   --format=%H -- registry/append-only-accepted.tsv`) and that the ten unaccepted events are all
   descendants of it, so the frozen rule is unsatisfiable for them.
Write `EX02.json` + `EX02.md` (≤40 lines) with commands, exit codes, verbatim finding lines and the code
line numbers. Copy into {WAVE}/w1/EX02CutoffProbe/."""),

    item("EX03GateArmProbe", "executor", ["operability"], f"""# EX03 — the vacuous-green control for the gate's acceptance arm (executor)
The L1 re-points pre-report gate arm 8 from `tools/round75-append-accepted.py` to
`tools/round81-append-debt.py` and adds arm 11 `round81-instruments`. Prove the re-point cannot buy a
green by itself.
1. Capture the current gate's arm-8 line at {BASE}: `python3 {LANE}/tools/pre-report-gate.py --repo {LANE}
   --round 80 --tip {BASE}` in a scratch clone checked out at {BASE} (never in the lane; the gate writes
   nothing but the lane-scope arm reads the tree — use `git clone --shared {LANE} "$S/clone" && git -C
   "$S/clone" checkout --detach {BASE}`). Record `PRE_REPORT_ARM round75-instruments …` verbatim. If the
   clone lacks the round-80 plan at that revision, note it and grade the arm directly instead:
   `python3 "$S/clone/tools/round75-append-accepted.py" --repo "$S/clone"` and
   `python3 "$S/clone/tools/round81-append-debt.py" --repo "$S/clone" --round 81` (poll up to 25 minutes
   for the module to land in the lane, then copy it in).
2. In a second clone at the round-81 tip, run the same two counters and record both verdict lines. The
   debt counter must be red at the base (`unaccepted=10`, with an EMPTY late register either absent or
   copied from the base) and green at the tip (`unaccepted=0`).
3. State explicitly whether the arm's green is carried by the late rows (compare the two lines) or by the
   re-point, naming any case where the re-pointed arm would print green without `registry/append-only-late.tsv`.
Write `EX03.json` plus both raw outputs. Copy into {WAVE}/w1/EX03GateArmProbe/."""),

    item("SC02Lesson", "scribe", ["calibration"], f"""# SC02 — draft `corpus/lessons/round-81.md` (scribe)
Draft at {WAVE}/w1/SC02Lesson/round-81.md (the L1 files it under {LANE}/corpus/lessons/round-81.md).
Required sections in this order:
1. `## Gate` — one row per source candidate with URL, access date 2026-11-04, a ≤25-word located quote,
   admit/reject, reason and flip. Candidates: (a) the corrected Ollama OpenAI-compatibility page
   `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx` —
   supersedes S557, whose filed URL lacked `api/` and returned 404; (b) `https://git-scm.com/docs/git-merge-base`
   — the strict-ancestry test the late-acceptance rule binds rows with; (c) `https://git-scm.com/docs/git-diff-tree`
   — the `--name-status -z --no-renames` record shape the frozen audit parses; (d) a REJECT candidate you
   open yourself and ground in a ≤25-word quote (a vLLM v0.33.0 release-note page is the expected one —
   the lane's pin is behind 1, and no round-81 claim reads vLLM behavior). Also add a `### Gate erratum —
   S557` subsection recording the corrected URL, the access date and its ≤25-word quote, as routed defect
   R80V3 requires. Open EVERY url yourself with `curl -sS -w '%{{http_code}} %{{size_download}}'` and record
   status, bytes and sha256 in your seat dir; never copy a quote or date you did not fetch.
2. `## Corrections` — the six backticked blocks byte-exact as they appear in the plan's C1 section, plus
   one prose paragraph each saying what the record claimed and what its own receipt prints.
3. `## Mistakes` — one row (class · evidence pointer · captured-by · fix) for: "the round-80 record states
   post-hardening selftest tallies (`pass=9`, `pass=6`) while its own cited receipts print `pass=11` and
   `pass=12`, and its erratum asserts the tallies above are post-hardening", captured-by the F1–F4 facts,
   fixed by `tools/round81-selfrecord-round80.py` + a QUALITY criterion.
4. `## Freeze divergences` — an empty list if none; do not invent one.
Do not write anywhere but your seat dir."""),

    item("SC03Sources", "scribe", ["coverage"], f"""# SC03 — draft the round's four SOURCES rows (scribe)
Draft at {WAVE}/w1/SC03Sources/sources-rows.md, in the exact 11-column contract-v1 shape
(`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`, no `|`
inside any cell, one line per row):
- **S558** docs tier A — supersedes S557: the corrected Ollama OpenAI-compatibility URL
  (`…/v0.40.11/docs/api/openai-compatibility.mdx`), anchor `### /v1/models` with its real line numbers and
  the response-notes lines you locate; `teaches` opens `supersedes S557 —`; status `mined`; used-by
  `corpus/knowledge/unregistered-class-second-engine.md`.
- **S559** docs tier A — `git-merge-base`: the strict-ancestry test (`--is-ancestor` exit status) the
  late-acceptance rule binds rows with; anchor the option's paragraph; status `mined`; used-by
  `corpus/knowledge/late-acceptance-rule.md`.
- **S560** docs tier A — `git-diff-tree`: the NUL-delimited `--name-status -z --no-renames` record
  population the frozen append-only audit parses; anchor the option descriptions; status `mined`; used-by
  `corpus/knowledge/late-acceptance-rule.md`.
- **S561** REJECTED — the candidate you opened for the Gate reject (expected: vLLM v0.33.0 release
  notes); `teaches` reads `REJECTED: <reason>; flip: <what would change the verdict>`.
Fetch every URL yourself this round and record, per row, the HTTP status, byte count and sha256 in
`curl.txt`; the anchor line numbers must come from your own fetch, not from the plan. Also write
`search-log.md` with one bounded-search paragraph (question, where searched, date, identified/screened/
included/excluded, stop rationale) for the frontier step."""),

    item("SC04Knowledge", "scribe", ["coverage"], f"""# SC04 — draft the knowledge entry, coverage row and QUALITY criterion (scribe)
Draft at {WAVE}/w1/SC04Knowledge/:
1. `late-acceptance-rule.md` — a `corpus/knowledge/` entry opening with `source: S559` (and citing S560
   in the body), `verified-at: 2026-11-04`, `recheck:` a command; ≤70 lines covering: the frozen audit's
   event population and the two keyed ledgers (`append-only-accepted.tsv` rows, the disclosure ledger);
   why the round-75 acceptance rule's pre-introduction cutoff makes every post-introduction event
   permanently unacceptable (round-51 intent: a round must not bless its own damage); the late-acceptance
   rule (a row introduced by a LATER round, strict descendant commit, `N > M` round order, exact
   hash/count/class); what `pending` means (the graded round's own record edits are visible and are repaid
   by the next round); and the limits (a late row never restores bytes and never changes the audit's
   `unrestored` count).
2. `readme-row.md` — one coverage-map table row for `corpus/README.md` in the appended-round style.
3. `quality-criterion.md` — one `KQ` row for `{LANE}/corpus/QUALITY.md` (next free number after KQ132;
   read the file's tail to place it) for the mined class "a record cites a receipt that prints another
   tally than the record states", citing `corpus/lessons/round-81.md`.
No quotes from sources you did not open; the L1 re-fetches every cited anchor."""),

    item("SC05Fetch", "scout", ["coverage"], f"""# SC05 — external source reconnaissance for the frontier step (scout)
Read-only reconnaissance; write only `$S/` and copy receipts into {WAVE}/w1/SC05Fetch/.
1. Fetch the three admit candidates and one reject candidate:
   `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`,
   `https://git-scm.com/docs/git-merge-base`, `https://git-scm.com/docs/git-diff-tree` and a vLLM
   v0.33.0 release page (`https://github.com/vllm-project/vllm/releases/tag/v0.33.0` or the raw
   `docs` release notes for that tag). For each: HTTP status, byte count, sha256, the exact line number and
   full line of the best ≤25-word quote, and whether the anchor the plan expects exists there.
2. Prove or refute the dead S557 URL: fetch the filed URL and the corrected URL, record both statuses and
   sizes, and confirm the filed one is 404 / the corrected one is the document whose sha256 S557 states
   (`44071a12…`).
3. Report the Ollama page's real response-notes line numbers (the filed row says 293–294) and the true
   `### /v1/models` heading line.
4. For the vLLM candidate, quote why it is out of scope for round 81's claims (one line) and what flip
   would admit it.
Every claim in your report needs the command and its raw output in the seat dir."""),

    item("CN01SiblingScan", "connector", ["adjacency"], f"""# CN01 — sibling-overlap scan for the round's two surfaces (connector)
Read-only cross-lane scan; write only `$S/` and copy into {WAVE}/w1/CN01SiblingScan/.
1. Does any sibling lane cite the filed S557 URL (`…/v0.40.11/docs/api-openai-compatibility.mdx`)?
   Search `/home/vgpnk/Projects/shokunin/*-shokunin/corpus/SOURCES.md` and `corpus/knowledge/` with
   `grep -rn` for `openai-compatibility` and for `api-openai-compatibility`; report every hit with
   path:line and whether the citation is dead (fetched by the sibling or not).
2. Does any sibling lane hold an append-only acceptance/register instrument in the same family
   (`append-accepted`, `append-registers`, `append-exempt`, `append-only-audit`)? List them with
   path:line, and state whether kama's late-acceptance rule would be a sibling-scope absorption (a lane
   that owns the rule) or in-province (kama owns only its own registers).
3. Report one adjacency line each for kama's `PROVINCE.md` and any contested scope the scan finds;
   never edit a sibling repo. Keep it to ≤30 lines with exact paths and the grep commands."""),

    item("RV01C1Attack", "reviewer", ["calibration"], f"""# RV01 — attack the C1 counter and its corrections (reviewer)
Poll for `{LANE}/tools/round81-selfrecord-round80.py` (up to 25 minutes; if it never lands, report that
and the item is a dead check). Attack, with named cases:
1. Can a correction outside `corpus/lessons/round-81.md` `## Corrections` be read as a correction
   (the round-80 RV01 defect class)? Try a block under `## Mistakes` in a scratch copy of the tip.
2. Can a correction whose `new` value does not re-derive (e.g. `new=c1-selftest=pass=99`), or whose `at`
   names the tip instead of the sealed revision, pass?
3. Can a fact be answered by a correction whose `old` is not the sealed declared value?
4. Does the counter read the worktree or `git show`? Plant a worktree-only edit of `SCORECARD.md` in a
   clone and check the verdict does not move.
5. Does it grade F6 at the tip (newest closure) while F1–F5 at the sealed revision, and is that stated?
6. Does `--no-corrections` at the tip print `mismatches=6`, exit 1? Does `--enumerate` at the base print
   `SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0`, exit 1?
Write `RV01.json` with one row per attack: case, command, observed, expected, caught/escaped, and the
file:line of the counter that decides it. Copy into {WAVE}/w1/RV01C1Attack/."""),

    item("RV02C2Attack", "reviewer", ["operability"], f"""# RV02 — attack the C2 counter, the late register and the gate re-point (reviewer)
Poll for `{LANE}/tools/round81-append-debt.py` and `{LANE}/registry/append-only-late.tsv` (up to 25
minutes). Attack, with named cases and scratch fixtures:
1. **Population base.** Can the counter be fed a base that hides the ten events (e.g. an earlier base
   that excludes round-79/80 commits, or a base that is not ancestral to the audited tip)? Does it reject
   a base that is not an ancestor of the tip, and does it read the base from the frozen plan rather than
   from an argument the caller can pick?
2. **Pending class.** Can the graded round's own events be smuggled into `pending` when they are actually
   older than the base? Count `pending` at the tip: it must equal exactly the round-81 commits' undeclared
   events, not the ten.
3. **Row binding.** Do a same-commit row, a same-round row (`N == M`), a non-descendant row, a short
   count, a wrong class and a note naming no round each turn the counter red (`bad_rows`)?
4. **Row honesty.** Pick three late rows at random and re-derive their hash from the event commit's diff
   yourself (`git -C {LANE} diff-tree -r --no-renames <commit>^ <commit>` and hash the removed line); state
   whether the row names a line the commit actually deleted, with the exact bytes.
5. **Gate re-point.** Read `tools/pre-report-gate.py`'s arm 8 and PREDICATE: is the retired round-75
   member documented, is its red receipt still readable, and does `--selftest` cover the new arm 11?
Write `RV02.json` with per-case commands, observed and expected; copy into {WAVE}/w1/RV02C2Attack/."""),

    item("CR01C1Critic", "critic", ["calibration"], f"""# CR01 — falsify C1's claim that the six facts are the record's declared facts (critic)
Independent of the counter. Sweep the round-80 self-record at {SEALED} for every *checkable* declared
number or pointer and decide which are stale; name any stale fact the plan's six do not cover, and any of
the six that is not actually stale.
1. `git -C {LANE} show {SEALED}:SCORECARD.md` — walk every tally, sha256, line count and receipt pointer in
   the head rows and the §Round 80 section; re-derive each from its witness at the sealed revision with a
   one-line command.
2. `git -C {LANE} show {SEALED}:LOG.md` §Round 80 — same.
3. Decide: is the plan's `corrected=6` a complete count of the stale facts the round-80 record declares, or
   does it under- or over-count? Name every extra or wrongly-counted fact with its command and value.
4. Attack the *axis* claim: is "the record's declared facts re-derive or are answered value-bound"
   calibration (self-assessment vs observed state) per AXES.md, or is it bookkeeping that should be
   reported as no move? Quote AXES.md's calibration definition.
Write `CR01.md` (≤40 lines) with verdict per point and the commands; copy into {WAVE}/w1/CR01C1Critic/."""),

    item("CR02C2Critic", "critic", ["operability"], f"""# CR02 — falsify C2: is late acceptance honest, bounded and non-laundering? (critic)
Read the plan's C2 section, the late register when it lands, and `tools/round75-append-accepted.py` +
`tools/round81-append-debt.py`.
1. **Laundering test.** Construct the strongest abuse the rule permits: a round that deletes 500 lines
   from `SCORECARD.md` today is "accepted" by the next round with 500 mechanical rows. Does the rule put a
   bound on what a late row may accept (count, class, file population, per-round volume)? If not, is the
   capability still honest — and what must the report say so nobody reads it as more than it is?
2. **Self-blessing.** Show that `N > M` plus "strict descendant" actually prevents a round blessing its own
   edits: a round's record edits and its acceptance rows normally land in the same round — walk the
   commit order for a same-round fixture and confirm the counter's rule rejects it.
3. **The ten events.** For each of the ten, decide whether "accepted historical in-place record edit" is a
   true description or whether one is something else that should be refused (e.g. the 38-row register
   restoration at `5785cdff` — is `removal` the right class, and does the acceptance note say what
   happened?). Name any row whose acceptance you would refuse, with the reason.
4. **Gate honesty.** Does moving arm 8 to a rule the lane itself authored make the gate weaker in a way the
   report must disclose? Name the strongest counter-argument and whether the C2 evidence answers it.
Write `CR02.md` (≤40 lines) with verdicts and commands; copy into {WAVE}/w1/CR02C2Critic/."""),

    item("MT01Mutants", "mutation-tester", ["operability"], f"""# MT01 — mutate the C2 counter's rule and prove the selftest kills each mutant (mutation-tester)
Poll for `{LANE}/tools/round81-append-debt.py` (up to 25 minutes). Work on a copy under `$S`.
Mutants (each is one semantic change to the committed module; run the module's `--selftest` against the
mutant and record `MUT <id> killed|escaped` plus the failing arm's output):
M1 drop the strict-descendant test (a same-commit row accepted);
M2 drop the `N > M` round-order test (same-round blessing accepted);
M3 accept a row whose `count` is short (`count-1`);
M4 accept a row whose `class` differs from the event's mechanical class;
M5 count an out-of-population row in `accepted` (or let it change a bucket);
M6 treat `pending` as accepted (move every post-base event into `accepted`);
M7 read the base from `--base` without checking it is an ancestor of the audited tip (or without cross-checking the plan's frozen base).
If a mutant escapes, name the missing selftest arm precisely and the assertion it needs. Also run the
unmutated module's `--selftest` and confirm `pass=N fail=0`. Write `MT01.json` + `MT01.md`; copy into
{WAVE}/w1/MT01Mutants/."""),
]

SPEC = {
    "wave": "w1",
    "milestone": "kama r81 w1",
    "reportDir": ".ufo/waves/round-81/w1",
    "maxLanes": 16,
    "axes": ["calibration", "operability", "coverage", "adjacency"],
    "context": CONTEXT,
    "items": ITEMS,
}

out = Path(WAVE + "/w1-spec.json")
out.write_text(json.dumps(SPEC, indent=1) + "\n", encoding="utf-8")
print(f"wrote {out} items={len(ITEMS)}")
