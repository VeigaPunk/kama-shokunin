#!/usr/bin/env python3
"""Build the round-82 wave-1 spec (one v1 wave, 14 seats) from the frozen claims plan.

Every prompt is absolute-path scoped to the lane and carries the same hard-rules block.
Run: python3 .ufo/waves/round-82/build-spec.py  -> writes w1-spec.json beside this file.
"""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
WAVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82"
SCRATCH = "/fast/scratch/hyaku/kama-r82"
BASE = "aaf974dbd3b6adb2ef914dc7293cda92b4e05551"
SEALED = "1b64f66ddea89c57b71165eacd14b0e1d6f24e11"

GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
kama lane, round 82: ONE v1 wave of 14 seats (build + attack) against the frozen claims in
{LANE}/plans/round-82-claims.md — read that file in full before your item and treat its
blockquote predicates, fact value strings, target lines and control lists as frozen text.
Base revision {BASE} (round-81 non-author closure tip); the sealed revision C1 grades is {SEALED}
(the round-81 record tip). Lane tip is read with `git -C {LANE} rev-parse master` (git HEAD is
detached after the first helper commit; never `@{{u}}` or `--abbrev-ref HEAD`).

# Round state (as dispatched)
C1's counter `tools/round82-selfrecord-round81.py` is committed at the tip; it prints
`SELFRECORD_R81_ENUM claims=6 stale=5 corrected=0` (exit 1) at the freeze tip and must print
`SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0` (exit 0) once the lesson's five
corrections and the appended record blocks land. C2's leg 1 `tools/round82-late-delta.py` prints
`LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0` (exit 0); leg 2 is
`tools/round81-append-debt.py --repo . --round 82`, whose round-82 commit repaired its late-row
introduction resolution from the register's first-add commit to each ROW's introducing commit
(`git blame`) — the disclosed repair is in its docstring and the red-before receipt is
{WAVE}/measured/defects/c2-debt-register-level-before.out. Never edit those modules; attack them.

# Write scope (hard)
You may write ONLY inside your own seat directory under {WAVE}/w1/<YourSeatName>/.
The lane tree {LANE} is READ-ONLY for every seat this round: the L1 owns every production file
(tools/, registry/, corpus/, SCORECARD.md, LOG.md, SKILL.md, plans/). Draft what an item asks you to
draft inside your seat dir; the L1 files it. Never touch the fleet root /home/vgpnk/Projects/shokunin
(no MANIFEST.json, templates/, scripts/, .ufo/state/, .ufo/watchdog.log, .scratch/, l0-questions.md),
never a sibling repo, never /home/vgpnk/Projects/shokuknow. An item that names no path is read-only
outside its seat dir.

# VCS rules (hard)
Never run git commit/push/stash/checkout/switch/reset/pull in the lane, never any mutating jj command,
never `git add`; the L1 is the only committer. Read-only git in the lane (log/show/diff/status/ls-files/
rev-parse/merge-base/ls-tree/blame/cat-file) is fine. Any fixture or clone repo is created under your
scratch root as `D=$(mktemp -d -p "$S") && git -C "$D" init -q` / `git clone --shared {LANE} "$S/clone"`,
and every later git call names `-C "$D"`; verify `git -C "$D" rev-parse --show-toplevel` equals `$D`
before any use. `git checkout`/`commit`/`push` are allowed ONLY inside such a scratch clone of the lane
or a fixture — never in {LANE}.

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
C1 calibration: `python3 tools/round82-selfrecord-round81.py --repo .` must print
`SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, exit 0. The six facts F1-F6 and their
tokens are tabulated in the plan; five are stale at the base and their corrections
(`corrected F<n> old=<token> new=<token> at={SEALED} date=2026-11-04 fix=<path>`) live in
`corpus/lessons/round-82.md` §Corrections with appended `#### round-82 correction` record blocks.
C2 operability: `python3 tools/round82-late-delta.py --repo . --round 82` prints
`LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0`, exit 0, AND
`python3 tools/round81-append-debt.py --repo . --round 82` prints
`APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=<p> unaccepted=0
bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0, over `registry/append-only-late.tsv`
(88 carried + 15 new rows over the five round-81 events).

# Seat rules
You are a leaf. An executor may spawn at most one read-only labrat probe; no other role spawns anyone
and no seat runs a swarm. Never message agent://all; message nothing outside your item. Do not commit
in the lane, do not edit a production file, do not run pre-report-gate.py in scored mode (the L1 does).
Sibling seats run at the same time: a file an item needs may be absent at your start — poll for it
(`sleep 30`, up to 25 minutes) before grading, and report honestly if it never lands. A dead seat stays
dead in the evidence: report every failure with its last error text, never fabricate a run. Report every
receipt as an absolute path plus its command and exit code.
"""


def item(name, role, axes, prompt):
    return {"name": name, "role": role, "axes": axes, "milestone": "kama r82 w1",
            "prompt": GODSPEED + prompt}


ITEMS = [
    item("EX01FactRederive", "executor", ["calibration"], f"""# EX01 — independent re-derivation of the six round-81 facts (executor)
Do NOT open `tools/round82-selfrecord-round81.py` until your six values are fixed in a file; it is the
object under test. From committed bytes only (`git -C {LANE} show {SEALED}:<path>` and `git -C {LANE}
show <TIP>:<receipt>` where TIP is `git -C {LANE} rev-parse master`):
F1 the §Round 81 C2 row's `-> exit 0` cell `pending=` value vs
`.ufo/waves/round-81/measured/after/debt-green.out` (`pending=`); F2 the `LOG.md` §Round 81
`Frontier: registry 297 -> <n> rows` vs your own count of registry rows in `corpus/SOURCES.md`
(lines matching 0-3 spaces, a pipe, an S-id cell); F3 the `SKILL.md` pre-report-gate row's `(ten arms,`
vs `.ufo/waves/round-81/measured/after/gate.out` (`arms=`); F4 the `## Axes` calibration row's "newest
non-author closure" vs the newest `corpus/lessons/round-*-verifier-spotcheck.md` at the tip; F5 the
`LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=<n>` line vs the same debt receipt; F6 the
§Round 81 C1 row's `pass=<n> fail=0` vs `.ufo/waves/round-81/measured/after/c1-selftest.out`.
Write `$S/rederive.py` + `EX01.json` (per fact declared, observed, stale) + `EX01.md` (≤30 lines).
Then, and only then, run the lane counter and record whether its six verdicts agree with yours
(`SELFRECORD_R81 ...` line, exit code); any disagreement is your headline finding. Also scan the whole
§Round 81 section and the appended corrections for a SEVENTH declared numeric fact that is stale
against its receipt — name it with the exact lines if one exists. Copy everything into
{WAVE}/w1/EX01FactRederive/."""),

    item("EX02LatePopulation", "executor", ["operability"], f"""# EX02 — independent re-derivation of C2's population and row ancestry (executor)
Do NOT open `tools/round82-late-delta.py` or `tools/round81-late-rows.py` until your numbers are fixed.
With `python3 {LANE}/tools/append-only-audit.py --repo {LANE} --json > $S/audit.json` and plain
`git -C {LANE}` calls only:
1. Enumerate every audit event with `undisclosed` lines and `status != restored` whose commit is
   ancestral to {BASE} (`git merge-base --is-ancestor <c> {BASE}`). Report events and line counts.
2. Split them by the two committed registers at the tip (`git -C {LANE} show master:registry/
   append-only-late.tsv`): rows whose (commit,file,hash) the register carries, and rows it does not.
   Report carried rows, missing rows, distinct events in each set.
3. For the rows the register carries, resolve each row's introducing commit with
   `git -C {LANE} blame --line-porcelain master -- registry/append-only-late.tsv` and check for every
   row that its introducing commit is a strict descendant of the row's event commit
   (`git merge-base --is-ancestor`), with the exact count of violations. Report the register's own
   first-add commit (`git log --diff-filter=A --format=%H master -- registry/append-only-late.tsv`) and
   whether it alone would satisfy the rule (it must not — that is the disclosed round-82 repair).
4. Confirm each missing row's event subject names the deletion round and that the row's note (when it
   exists in your generated set) would name accepting round 82 > deletion round.
Write `$S/population.tsv`, `EX02.json`, `EX02.md` (≤35 lines). Copy into {WAVE}/w1/EX02LatePopulation/."""),

    item("EX03ReceiptReplay", "executor", ["freshness"], f"""# EX03 — receipt-revision replay for every round-82 receipt (executor)
This is the class R81V2 named: a receipt's `# rev:` header must be able to print the receipt's own
content. For every committed file under {WAVE}/measured/ that carries a `# rev: <40-hex>` or
`# cmd:` header:
1. Create ONE scratch clone `git clone --shared {LANE} "$S/clone"`, verify `rev-parse --show-toplevel`,
   and for each receipt: `git -C "$S/clone" checkout --detach <rev>` (allowed in the clone), copy the
   lane's current `tools/` and `registry/` files that are needed? NO — do not copy: the receipt must be
   reproducible from the tree AT its named rev. Run the receipt's `# cmd:` from the clone root, capture
   output and exit, and compare it with the committed receipt body (ignore the `# rev:`/`# cmd:` header
   lines and the `EXIT=` line for the comparison; report both).
2. Classify each receipt: `reproduces` (body identical), `differs` (body differs; show the first
   differing line from each side), `unrunnable` (the named rev lacks the command or a needed file; name
   it). Include {WAVE}/measured/defects/c2-debt-register-level-before.out and state whether its rev
   really prints `bad_rows=15` (the red-before claim).
3. Report the lane tip you used and whether any receipt's named rev is not an ancestor of it.
Write `EX03.json` + `EX03.md` (≤40 lines) with a per-receipt table. Copy into {WAVE}/w1/EX03ReceiptReplay/."""),

    item("EX04GateArm", "executor", ["operability"], f"""# EX04 — the vacuous-green control and the round-82 gate arm proposal (executor)
1. In a scratch clone at {BASE} (`git clone --shared {LANE} "$S/clone"`; `checkout --detach {BASE}`),
   run the frozen round-81 chain as the base control: copy nothing from the working tree; use the clone's
   own files. Record (a) `python3 tools/round81-append-debt.py --repo . --round 82` — if the round-82 plan
   is absent at {BASE}, say so and instead run `--round 81` and record its line; (b) an EMPTY late
   register fixture: write `$S/empty.tsv` with only the header and run
   `python3 tools/round81-append-debt.py --repo . --round 81 --late "$S/empty.tsv"` — record the exact
   finding class it emits (the round-81 `--late` path is unbound); explain in one paragraph why neither
   run can be green without the late rows.
2. At the lane tip, propose the exact arm-12 spec for `tools/pre-report-gate.py`: which commands
   (`tools/round82-selfrecord-round81.py --selftest`, `tools/round82-late-delta.py --selftest`,
   `tools/round81-append-debt.py --round 82`), the expected verdict lines, the ARM_ORDER position, and
   the one-line SKILL.md registry edit. Verify your proposal by reading the gate's `ARM_SPECS`,
   `ARM_ORDER` and the red-test harness (`--selftest`) at the tip; name every place that must change and
   any arm-count assertion that would break. Do not edit the gate.
Write `EX04.json` + `EX04.md` (≤40 lines). Copy into {WAVE}/w1/EX04GateArm/."""),

    item("SC01Lesson", "scribe", ["calibration"], f"""# SC01 — draft `corpus/lessons/round-82.md` (scribe)
Draft at {WAVE}/w1/SC01Lesson/round-82.md (the L1 files it under {LANE}/corpus/lessons/round-82.md).
Sections, in this order:
1. `## Gate` — one row per source candidate: URL, access date 2026-11-04, a ≤25-word located quote
   (line number), admit/reject, reason, flip. Open EVERY URL yourself with
   `curl -sS -w '%{{http_code}} %{{size_download}}' -o $S/<name>` and record status, bytes, sha256.
   Candidates: (a) `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md`
   — the newest llama.cpp tag's server README, the pinned-document side of a `behind` relation;
   (b) `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md` — the lane's
   own pin (`registry/engine-pins.tsv`), to diff against (a); (c) one SGLang or vLLM page at its newest
   tag (`v0.5.23` / `v0.33.0`) that you can anchor a ≤25-word quote in; (d) one REJECT candidate you
   open yourself (a release-notes page is the expected reject: a newer release is a recheck trigger, not
   knowledge). State for (a)-(b) whether the anchored statement survived the release gap or moved.
2. `## Corrections` — the five backticked `corrected F<n> old=... new=... at={SEALED} date=2026-11-04
   fix=...` lines byte-exact as in the plan, plus one prose paragraph each naming the record location,
   the value it declares and the receipt value. F6 holds: state it and do NOT correct it.
3. `## Mistakes` — one row (class · evidence pointer · captured-by · fix), mined from this round: the
   round-81 late-acceptance rule resolved ONE register-wide introduction commit, so it could never
   accept an event created after the register first existed (the promise its own plan made for the next
   round). Evidence: {WAVE}/measured/defects/c2-debt-register-level-before.out (`bad_rows=15`) and the
   repaired module's selftest arms. captured-by: `none` — the round-81 control suite never built a
   post-introduction acceptance case. Fix: row-level `git blame` introduction + three selftest arms,
   shown red-capable (`row-intro-later` fails under the old resolution).
4. `## Freeze divergences` — the `--late` path left unbound, the retained successor register, the
   `pending` conventions. Do not invent.
Do not write anywhere but your seat dir."""),

    item("SC02Sources", "scribe", ["coverage"], f"""# SC02 — draft the round's SOURCES rows (scribe)
Draft at {WAVE}/w1/SC02Sources/sources-rows.md, exact 11-column contract-v1 shape
(`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`, no
`|` inside any cell, one row per line). The lane registry holds 302 rows; the next free id is S563.
Candidate rows (write only what you opened yourself this round):
- **S563** docs tier A — llama.cpp `tools/server/README.md` at tag `b12103` (newest release, raw URL);
  anchor the `/health` or `/props` section heading whose wording you locate; `teaches` names the
  recheck-trigger rule (a newer release is a trigger, never proof the held knowledge is wrong); status
  `mined`; used-by `corpus/knowledge/pin-recheck-trigger.md`.
- **S564** docs tier A — the same file at the lane's pin `b11755`, only if you diff it against S563 and
  can state one located difference or one located sameness in `teaches`; status `mined`; used-by
  `corpus/knowledge/pin-recheck-trigger.md`.
- **S565** docs tier A — one SGLang or vLLM page at its newest tag, anchored with a ≤25-word quote;
  `teaches` says what the newest-tag document states about the surface the lane probes; status `mined`;
  used-by `corpus/knowledge/pin-recheck-trigger.md`.
- **S566** REJECTED — a release-notes/tag page you opened; `teaches` reads
  `REJECTED: <reason>; flip: <what would change the verdict>`.
Fetch every URL yourself; record status, bytes, sha256 and the anchor line number in `curl.txt`. Also
write `search-log.md` (bounded-search paragraph: question, where, date, identified/screened/included/
excluded, stop rationale). No quote you did not fetch."""),

    item("SC03Knowledge", "scribe", ["coverage"], f"""# SC03 — draft the pin-recheck knowledge entry, coverage row and QUALITY criterion (scribe)
Draft at {WAVE}/w1/SC03Knowledge/:
1. `pin-recheck-trigger.md` — a `corpus/knowledge/` entry opening with `source: S563` (citing S564/S565
   in the body), `verified-at: 2026-11-04`, `recheck:` a command; ≤70 lines covering: what
   `registry/engine-pin-relations.tsv` binds (`behind` = how many releases sort above the pin, `newest`
   = the tag observed); that a `behind` row is a recheck TRIGGER, not drift; the only test of drift is
   re-opening the pinned document at its own ref and locating the anchored statement; that the
   newest-tag document may differ (name one located difference you verified) without the held knowledge
   being wrong; and the boundary (the relation register says nothing about model quality or served
   behavior).
2. `readme-row.md` — one coverage-map table row for `corpus/README.md` in the appended-round style.
3. `quality-criterion.md` — one `KQ` row for `{LANE}/corpus/QUALITY.md` (next free number after KQ133;
   read the tail) for the mined class "a rule's prose names the row's introducing commit while the code
   resolves one commit for the whole register", citing `corpus/lessons/round-82.md`.
Open every URL you cite yourself (curl + sha256 in your seat dir); the L1 re-fetches every anchor."""),

    item("SK01PinRecon", "scout", ["freshness"], f"""# SK01 — pin-watch recon and pinned-document anchors (scout, read-only)
1. Run `python3 {LANE}/tools/pin-watch.py check --repo {LANE}` (record the exact verdict line and exit;
   if it needs network and fails, record the failure verbatim).
2. For each row of `{LANE}/registry/engine-pin-relations.tsv`, fetch the pinned document at its own ref
   where one exists: llama.cpp `tools/server/README.md` at `b11755` and at `b12103`
   (`https://raw.githubusercontent.com/ggml-org/llama.cpp/<tag>/tools/server/README.md`), and the SGLang
   and vLLM docs at their newest tags if you can identify the file from the lane's corpus rows
   (`grep -rn 'sglang\\|vllm' {LANE}/corpus/SOURCES.md`). For each fetch: HTTP status, bytes, sha256,
   and the `/health`, `/props` or `/slots` heading line numbers. Diff `b11755` vs `b12103` for the
   server README only (`diff -u`), and report every hunk that touches a health/readiness section, plus
   whether the anchored statements the lane holds at `b11755` still exist at `b12103`.
3. State, per relation row, whether a recheck row could now be written mechanically from your receipt,
   and what an honest `recheck` column value would be (date + trigger + verdict vocabulary
   holds/reworded/moved/drifted).
Write `SK01.md` (≤40 lines) + raw fetch log. Copy into {WAVE}/w1/SK01PinRecon/. Never claim a fetch
you did not perform."""),

    item("SK02RecordScan", "scout", ["calibration"], f"""# SK02 — completeness scan of the round-81 record's stale facts (scout, read-only)
C1 grades six named facts; this item asks whether six is the right population. Read `{LANE}/SCORECARD.md`
§Round 81 (from the `## Round 81 —` heading to the next `## ` heading), the whole `{LANE}/LOG.md`
§Round 81 section and its appended `LOG-CORRECTION` entries, `{LANE}/SKILL.md`'s pre-report-gate row, and
`{LANE}/corpus/lessons/round-81.md`, all at the sealed revision
`git -C {LANE} show {SEALED}:<path>`.
For every numeric or noun claim in those sections (tallies, counts, arm counts, row counts, paths,
receipt revisions, wave/seat counts, registry counts, capability counts), re-derive the value from the
receipt or tree it names and record `holds|stale` with the exact command. Use
`{LANE}/.ufo/waves/round-81/w1-results.json` to check the wave/seat claim; use
`{LANE}/.ufo/waves/round-81/measured/after/*.out` for tallies; use
`git -C {LANE} ls-tree -r --name-only {SEALED} corpus/lessons/` for the closure pointer.
Deliver: a table with one row per claim (location, claimed, observed, verdict, command), the count of
stale claims, and the list of stale claims NOT covered by the plan's five corrections (the F6 holding
fact excluded). Name any claim you could not re-derive and say why. Copy `SK02.md` + `scan.tsv` into
{WAVE}/w1/SK02RecordScan/. Do not open `tools/round82-selfrecord-round81.py` until your table is written."""),

    item("CN01SiblingScan", "connector", ["adjacency"], f"""# CN01 — sibling-overlap scan for the round's surfaces (connector, read-only)
1. Does any sibling lane hold an instrument in the append-only acceptance/register family whose rule
   binds a row's introducing commit (`grep -rn 'blame\\|introduction\\|append-only-late'
   /home/vgpnk/Projects/shokunin/*-shokunin/tools/ /home/vgpnk/Projects/shokunin/*-shokunin/registry/`
   and the same under `corpus/knowledge/`)? Report every hit as path:line with a one-line reading of
   whether that lane owns the same rule or a different surface; name any case where kama's repair would
   be sibling-scope absorption rather than in-province work.
2. Does any sibling cite the llama.cpp `tools/server/README.md` at `b12103` or hold a `pin-watch`
   relation register (`grep -rn 'b12103\\|engine-pin'` across sibling lanes)? Report whether kama's
   recheck ground is unique.
3. Does any sibling lane claim `git blame`-based introduction resolution (the technique, not the
   instrument)? One adjacency line for `PROVINCE.md` and one for contested scope.
Keep it to ≤30 lines with exact paths and grep commands; never edit a sibling repo; copy into
{WAVE}/w1/CN01SiblingScan/."""),

    item("RV01AttacC1", "reviewer", ["calibration"], f"""# RV01 — attack C1's counter (reviewer)
Attempt to make `{LANE}/tools/round82-selfrecord-round81.py` print
`SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, exit 0, WITHOUT the honest corrections
landing, or to make an honest set fail. Work in `$S/clone` (a scratch clone; `git checkout`/`commit`
allowed there only) or against a copy of the module, never the lane module.
Every attack is one case with: the fixture bytes, the command, the observed line/exit, and whether the
counter refused it (desired) or accepted it (escape). Cover at least: a correction block outside
`## Corrections`; a correction for the holding F6; a duplicated correction; `old` naming the witness
value instead of the declared one; `at` naming the tip instead of the sealed revision; a `fix=` path
that exists but lacks the `new` token; a lesson that deletes the `## Corrections` heading but keeps the
blocks; a fact whose declared token is a prefix of another token (e.g. `pending=1` matching `pending=12`)
— the last one checks whether the comparison is exact.
Deliver `RV01.md` (≤40 lines) with a case table and an explicit escape list (or `escapes: none`), plus
the exact commands. Copy into {WAVE}/w1/RV01AttacC1/. If you find an escape, say precisely which
line of the counter admits it."""),

    item("RV02AttacC2", "reviewer", ["operability"], f"""# RV02 — attack C2's delta check and the repaired debt rule (reviewer)
Work only on copies (`$S/clone`, or a copied module + fixture register), never the lane modules.
Part A — `tools/round82-late-delta.py`: try to make it print `bad=0` while the register is wrong:
a carried row rewritten by one byte; a new row with `count` off by one; a new row with `class`
`removal` instead of `in-place-edit`; a new row whose note says `round-81 accepts round-81`;
a new row whose note says `round-83 accepts round-81` (a later round than the graded one — should this
be refused? state the rule you infer); a register with an extra row for an event outside the
population; a duplicate row; a register whose header line is edited. For each: command, observed
line/exit, refused/accepted.
Part B — `tools/round81-append-debt.py --round 82` after the disclosed row-introduction repair:
on a similar fixture, show that (i) a row whose blame-introduced commit is an ANCESTOR of its event is
refused (`not-descendant`), (ii) a row whose introduction postdates the event is accepted, (iii) a
row with no resolvable introduction is `unbound-register`. Also determine whether the repair could
accept a row for the graded round's own events (it must not — check the `N > M` rule and the base
split) and whether `--late` still works at all (it does not bind an introduction — state that
limit precisely).
Deliver `RV02.md` (≤45 lines) with the case table and escape list. Copy into {WAVE}/w1/RV02AttacC2/."""),

    item("CR01FalsifyClaims", "critic", ["calibration"], f"""# CR01 — falsify the round's claims, predicates and controls (critic)
Read `{LANE}/plans/round-82-claims.md`, both new modules and the receipts under {WAVE}/measured/.
Answer, with commands:
1. Is each claim's target line reachable by a DO-NOTHING control? Build the cheapest control that
   skips the claimed work and score it: for C1, a lesson with no corrections (the committed
   `measured/control/c1-no-corrections.out` is the L1's; reproduce it yourself at the tip and say
   whether it is red); for C2, the same register at the base (no round-82 rows — reproduce the before
   line from {WAVE}/measured/before/ in a clone) and an empty late register.
2. Does any claim rest on an instrument the round itself modified? C2's leg 2 uses a module repaired in
   round 82 after data existed (`bad_rows=15` before, `bad_rows=0` after). Judge strictly: is the
   predicate's rule text unchanged, is the repair disclosed, does the red-before receipt reproduce at
   its named rev, and would the claim be admissible to a non-author closure? Name every risk.
3. Name any axis that is harmed by the round's committed edits (append-only files, head rows, SKILL
   row, gate arm) and cite the diff hunk.
4. State one falsifiable prediction the round's own evidence would make about round 83, and the cheapest
   command that would refute it.
Deliver `CR01.md` (≤50 lines) with verdicts per claim (verified / not verified / unprovable) and the
risks a closure must weigh. Copy into {WAVE}/w1/CR01FalsifyClaims/."""),

    item("MT01Mutants", "mutation-tester", ["operability"], f"""# MT01 — mutant battery on the round's two new modules (mutation-tester)
Prove the new selftest arms are red-capable. Work on copies under `$S`; never edit the lane modules.
1. Copy `tools/round82-selfrecord-round81.py` and `tools/round82-late-delta.py` into `$S` (plus a
   scratch git repo if a module needs one). For EACH named mutant below: apply the mutation to the
   COPY, run `--selftest`, and record pass/fail and whether at least one arm went red (desired):
   - selfrecord: delete the `at != sealed` check; delete the `fix` token check; compare tokens with
     `startswith` instead of exact equality; read corrections from the whole lesson (not the section);
     count a correction for a holding fact as valid.
   - late-delta: drop the carried-bytes comparison; accept a note whose accepting round equals the
     deletion round; skip the `extra`-row scan; compare only the first two cells.
   For each mutant state the surviving arms (if any) — a mutant that leaves every arm green is an
   escape and is the headline.
2. Also run the honest modules' `--selftest` and record their tallies, and run
   `python3 {LANE}/tools/round81-append-debt.py --selftest` (record `pass=25 fail=0`; the three
   row-introduction arms must be present — name them from the source).
Deliver `MT01.json` (mutant → red arms → escaped arms) + `MT01.md` (≤35 lines). Copy into
{WAVE}/w1/MT01Mutants/."""),
]

SPEC = {
    "wave": "w1",
    "lane": "kama",
    "round": 82,
    "policy": "v1",
    "reportDir": ".ufo/waves/round-82/w1",
    "context": CONTEXT,
    "items": ITEMS,
}

if __name__ == "__main__":
    out = Path(WAVE) / "w1-spec.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    spec = {"wave": "w1", "milestone": "kama r82 w1",
            "reportDir": ".ufo/waves/round-82/w1", "maxLanes": 16,
            "axes": ["calibration", "operability", "coverage", "adjacency"],
            "context": CONTEXT, "items": ITEMS}
    out.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {out} items={len(ITEMS)}")
