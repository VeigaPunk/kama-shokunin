#!/usr/bin/env python3
"""Build the round-83 wave-1 spec (one v1 wave, 15 seats) from the frozen claims plan.

Every prompt is absolute-path scoped to the lane and carries the same hard-rules block.
Run: python3 .ufo/waves/round-83/build-spec.py  -> writes w1-spec.json beside this file.
"""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
WAVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83"
SCRATCH = "/fast/scratch/hyaku/kama-r83"
BASE = "30d8eac394a8714fad3dc792b74a45a25b4366a2"
SEALED = "b1ba614b51255a3dcfe3e0946f32f8e31bd65c09"
PLAN = f"{LANE}/plans/round-83-claims.md"

GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
kama lane, round 83: ONE v1 wave of 15 seats (build + attack) against the frozen claims in
{PLAN} — read that file in full before your item and treat its
blockquote predicates, fact tables, target lines and control lists as frozen text.
Base revision {BASE} (round-82 non-author closure tip); the sealed revision C2 grades is {SEALED}
(the round-82 lane tip its report cites). Lane tip is read with `git -C {LANE} rev-parse master`
(git HEAD is detached after the first helper commit; never `@{{u}}` or `--abbrev-ref HEAD`).

# Round state (as dispatched)
C1 operability has three legs over `tools/round81-append-debt.py`: leg A (default register path)
prints `unaccepted=8` at the freeze tip, leg B (`--late registry/append-only-late.tsv`) prints
`late=0 unaccepted=23 bad_rows=103` because the tool never binds a caller-supplied register path, and
leg C is a new `tools/round83-pending-falls.py` that must show round 82's `pending=8` falling.
C2 calibration is a new `tools/round83-selfrecord-round82.py` grading six facts of the round-82
record (F1 `log82-c1-selftest=18`, F2 `sc82c1-selftest=22`, F3 `calib82-selftest=22` are stale against
`c1-selftest.out`'s 23; F4 `log82-c2-debt-selftest=25`, F5 `log82-frontier-rows=305`,
F6 `log82-late-delta=15` hold). C3 freshness is a new `tools/round83-pin-rechecks.py` over
`registry/pin-recheck-rows.tsv`, keyed to `registry/engine-pin-relations.tsv` (5 rows: four gradable,
`llama.cpp b7200` ungraded). Never edit any module or register: the L1 files every production change.

# Write scope (hard)
You may write ONLY inside your own seat directory under {WAVE}/w1/<YourSeatName>/.
The lane tree {LANE} is READ-ONLY for every seat this round: the L1 owns every production file
(tools/, registry/, corpus/, SCORECARD.md, LOG.md, SKILL.md, plans/). Draft the complete file an item
asks for inside your seat dir (a full replacement module, byte-complete, ready to `cp`); the L1 files
it. Never touch the fleet root /home/vgpnk/Projects/shokunin (no MANIFEST.json, templates/, scripts/,
.ufo/state/, .ufo/watchdog.log, .scratch/, l0-questions.md), never a sibling repo, never
/home/vgpnk/Projects/shokuknow. An item that names no path is read-only outside its seat dir.

# VCS rules (hard)
Never run git commit/push/stash/checkout/switch/reset/pull in the lane, never any mutating jj command,
never `git add`; the L1 is the only committer. Read-only git in the lane (log/show/diff/status/ls-files/
rev-parse/merge-base/ls-tree/blame/cat-file) is fine. Any fixture or clone repo is created under your
scratch root as `D=$(mktemp -d -p "$S") && git -C "$D" init -q` / `git clone --shared {LANE} "$S/clone"`,
and every later git call names `-C "$D"`; verify `git -C "$D" rev-parse --show-toplevel` equals `$D`
before any use. `git checkout`/`commit`/`push` are allowed ONLY inside such a scratch clone of the lane
or a fixture — never in {LANE}. Proving a module's behaviour on a patched copy requires exactly such a
scratch clone: copy the current module in, overwrite it with your draft, commit inside the clone, run.

# Scratch (hard)
Every clone, fixture, work tree or scratch register lives under $S = {SCRATCH}/<YourSeatName>/
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
C1 operability — (A) `python3 tools/round81-append-debt.py --repo . --round 83` must print
`APPEND_DEBT round=83 base=30d8eac394a8 events=76 accepted=53 late=35 pending=<p> unaccepted=0
bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0; (B) the same command with
`--late registry/append-only-late.tsv` must print the SAME summary, exit 0; (C)
`python3 tools/round83-pending-falls.py --repo . --round 83` must print
`PENDING_FALLS round=83 from=82 declared=8 window=8 accepted=8 unaccepted=0 falls=yes`, exit 0.
C2 calibration — `python3 tools/round83-selfrecord-round82.py --repo .` must print
`SELFRECORD_R82 claims=6 mismatches=0 corrected=3 unbacked=0`, exit 0; `--enumerate` prints
`stale=3` exit 1 and `--no-corrections` prints `mismatches=3` exit 1 at the tip.
C3 freshness — `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv
--rows registry/pin-recheck-rows.tsv` must print
`PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0`, exit 0.

# Seat rules
You are a leaf. An executor may spawn at most one read-only labrat probe; no other role spawns anyone
and no seat runs a swarm. Never message agent://all; message nothing outside your item. Do not commit
in the lane, do not edit a production file, do not run `tools/pre-report-gate.py` in scored mode (the L1
does). Sibling seats run at the same time: a file an item needs may be absent at your start — poll for
it (`sleep 30`, up to 25 minutes) before grading, and report honestly if it never lands. A dead seat
stays dead in the evidence: report every failure with its last error text, never fabricate a run.
Report every receipt as an absolute path plus its command and exit code. Keep prose tight: a `.md`
deliverable is at most 90 lines unless the item says otherwise.
"""


def item(name, role, axes, prompt):
    return {"name": name, "role": role, "axes": axes, "milestone": "kama r83 w1",
            "prompt": GODSPEED + prompt}


ITEMS = [
    item("EX01LateBinding", "executor", ["operability"], f"""# EX01 — bind the `--late` register path to a per-row introduction (executor)

Deliver a byte-complete replacement for `{LANE}/tools/round81-append-debt.py` at
`{WAVE}/w1/EX01LateBinding/round81-append-debt.py`, plus receipts.

Defect (round-82 divergence 1, `{LANE}/corpus/lessons/round-82.md` §Freeze divergences 1): with
`--late FILE` the tool sets `late_intro=None` and `row_marks=None`, so every row reports
`unbound-register`. Base state:
`python3 tools/round81-append-debt.py --repo <lane> --round 83 --late registry/append-only-late.tsv`
→ `APPEND_DEBT round=83 base=30d8eac394a8 events=76 accepted=53 late=0 pending=0 unaccepted=23
bad_rows=103 bad_declarations=0 out_of_population=0`, exit 1, 103 `unbound-register` findings.

Required behaviour (exactly this, nothing wider):
1. A caller-supplied `--late PATH` must resolve to a repository-relative path inside the audited
   working tree: realpath the path, compare it to `git -C <repo> rev-parse --show-toplevel`, derive the
   repo-relative path, and require that path to be committed at the audited revision (`git cat-file -e
   <to>:<relpath>`). A path outside the repo, or a path untracked at `<to>`, is `could-not-evaluate`
   printed to stderr with exit 2 — never a per-row verdict.
2. For an in-repo path, resolve the register's file introduction at `<to>` (`git log --diff-filter=A`)
   and each row's introduction with the existing `blame_rows(<to>, <relpath>)`; grade the rows with the
   unchanged `grade()` rule. `--late <default path>` must produce byte-identical output to the default
   path (no `--late` at all).
3. Keep every existing rule sentence, the PREDICATE docstring's meaning, and the `--register`,
   `--audit-json`, `--json`, `--selftest` flags unchanged in behaviour. Extend the docstring with a
   ROUND-83 PATH-BINDING paragraph naming the three new arms.
4. Add selftest arms, each red-capable and named exactly: `late-path-outside-repo`,
   `late-path-untracked`, `late-path-bound` (an in-repo register whose rows' introductions are resolved
   and whose grading equals the default-path result). Keep all 25 existing arms green.

Prove it: `git clone --shared {LANE} "$S/clone"`, `git -C "$S/clone" checkout -q {BASE}`, copy your
draft over `tools/round81-append-debt.py`, `git -C "$S/clone" -c user.name=probe -c user.email=p@p
commit -qm probe -- tools/round81-append-debt.py`, then run leg A, leg B, `--selftest`, and the two
refusal controls; capture each command, its full stdout, and its exit code.
Deliver `EX01.json` ({{"arms": [...], "tallies": {{...}}, "legA": "...", "legB": "...", "controls": [...]}})
and `EX01.md` (≤40 lines). Copy every verbatim output into your seat dir."""),

    item("EX02LateRows", "executor", ["operability"], f"""# EX02 — generate the round-83 late rows for round 82's eight events (executor)

Deliver `{WAVE}/w1/EX02LateRows/late82-rows.tsv` — the 20 data rows (six LF TSV cells each, no header)
that accept the eight round-82 record-edit events — plus receipts.

Use the frozen generator, never hand-written cells:
`python3 {LANE}/tools/round81-late-rows.py --help` first; then run its `generate` mode against a
scratch clone of the lane at `{BASE}` for the undeclared deletion events committed after
`aaf974dbd3b6adb2ef914dc7293cda92b4e05551` and at or before `{BASE}`. The window is exactly:
`962bd251` (SCORECARD 1), `a251cbab` (SCORECARD 1), `0d7c7c3e` (SCORECARD 10), `7ad14e6c`
(SCORECARD 1 + corpus/lessons/round-82.md 1), `6a160310` (SCORECARD 2), `8a3e8af2` (SCORECARD 3),
`9efa6f1c` (SCORECARD 1) — 8 events, 20 lines, 20 rows.

Each row's note must use the register convention `round-83 accepts round-82 "<commit subject>"` plus a
short acceptance reason, with the accepting round greater than the deletion round; the deletion round
is the round named by the event commit's own subject (all eight are `round-82 …`). Cells: exact
`line_sha256`, exact `count`, the class the audit reports. No literal tab inside a note.

Prove it end to end: take a `git clone --shared` of the lane at `{BASE}`, append the 20 rows to
`registry/append-only-late.tsv`, commit inside the clone, and run
`python3 {LANE}/tools/round81-append-debt.py --repo "$S/clone" --round 83` (the frozen plan declares
base {BASE}, so the clone's tip may be its own commit). Expected: `events=76 accepted=53 late=35
pending=0 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0. If `accepted` or
`events` differ, report the real numbers — do not adjust the rows to a number.
Deliver `EX02.json` ({{"rows": 20, "events": 8, "appended_sha256": "...", "run": "..."}}) and `EX02.md`
(≤35 lines) with the generator command, the verbatim summary line and its exit."""),

    item("EX03SelfRecord", "executor", ["calibration"], f"""# EX03 — the round-82 self-record counter (executor)

Deliver a complete `{WAVE}/w1/EX03SelfRecord/round83-selfrecord-round82.py` (model it on
`{LANE}/tools/round82-selfrecord-round81.py`: same CLI shape `--repo`, `--enumerate`,
`--no-corrections`, `--selftest`, `--json`), plus receipts.

Implement exactly the C2 predicate in `{PLAN}` §C2: six facts F1–F6 read with `git show <rev>:<path>`
at the sealed revision {SEALED}, the fact's tip witness re-derived from the committed tree/receipts, and
one `corrected F<n> old=… new=… at=… date=… fix=…` block per stale fact in
`corpus/lessons/round-83.md` `## Corrections` (heading must be exactly `## Corrections`).
Witnesses: F1/F2/F3 → `SELFRECORD_R81_SELFTEST pass=23 fail=0` in
`{LANE}/.ufo/waves/round-82/measured/after/c1-selftest.out`; F4 →
`APPEND_DEBT_SELFTEST pass=25 fail=0` in `…/c2-debt-selftest.out`; F5 → the `corpus/SOURCES.md` row
count at the plan's declared population revision {SEALED} (305; the counter must read the sealed
revision's file, never the graded tip, and its selftest must prove a tip with more rows does not move
the witness); F6 → `LATE_DELTA … new=15 bad=0` in `…/c2-late-delta.out`.

Two new fix-leg clauses (they are the round's point — round-82's leg only checked containment):
- `lesson-only-token`: a `new` token whose only tip occurrence is under `corpus/lessons/` is `unbacked`.
- `token-only-in-correction-region`: a `new` token present in the named `fix` path only inside a
  `#### round-<N> correction` block or a `LOG-CORRECTION` line is `unbacked`.
Keep round-82's clauses: whole-token right boundary, `fix` never a `corpus/lessons/` path, exact
`## Corrections` heading, wrong-`at`/wrong-`old`/duplicate/holding-fact rejections.

Selftest must include, each red: `honest` (green), `correction-outside-container`, `wrong-at`,
`wrong-old`, `wrong-new`, `fix-without-token`, `near-token-new`, `fix-self-referential`,
`near-corrections-heading`, `duplicate-correction`, `correction-for-holding-fact`, `unknown-fact`,
`no-corrections`, `lesson-only-token`, `token-only-in-correction-region`, and the F5
`registry-base-bound` arm. State every arm's expected `(mismatches, unbacked, corrected)`.

Prove it in a scratch clone at `{BASE}`: copy the draft in, append the three correction blocks and the
two record blocks (LOG-CORRECTION line + SCORECARD `#### round-83 correction` block carrying the
tokens) to your clone, commit, and run `--enumerate` (before the blocks), `--no-corrections`, the
honest run (after the blocks) and `--selftest`. Deliver `EX03.json`, `EX03.md` (≤45 lines) and the full
verbatim outputs of all five runs."""),

    item("EX04PendingFalls", "executor", ["operability"], f"""# EX04 — the pending-fall leg (executor)

Deliver a complete `{WAVE}/w1/EX04PendingFalls/round83-pending-falls.py` (~120–200 lines), plus receipts.

Frozen output: one line
`PENDING_FALLS round=83 from=82 declared=8 window=8 accepted=8 unaccepted=0 falls=yes`, exit 0.
It reads the round-82 final-gate receipt `{LANE}/.ufo/waves/round-82/measured/after/gate.out`, extracts
the `APPEND_DEBT round=82 … pending=<n>` number and the `base=<12-hex>` it carries (that is the round-82
base `aaf974db`), recomputes the population itself by running
`python3 {LANE}/tools/append-only-audit.py --repo <repo> --json` (population = events with undisclosed
lines whose status is not `restored`), takes the window of events committed after that base and at or
before the round-83 plan's declared base (read base from `plans/round-83-claims.md` with the same
`Base revision `<40-hex>`` rule the other counters use), and counts how many window events are
covered by a committed `registry/append-only-late.tsv` row at the graded tip (a row whose
`(commit, file, line_sha256)` triple is present for every undisclosed line of the event). `declared`
is the receipt's number, `window` the recomputed window size, `accepted` the covered window events,
`unaccepted = window - accepted`; `falls=yes` only when `declared == window`, `unaccepted == 0`; the
line prints `falls=no` and exits 1 otherwise. A receipt naming another round, or a missing receipt, is
`could-not-evaluate` exit 2. Add a `--json` and a `--selftest` with arms, each red:
`declared-mismatch`, `window-uncovered`, `receipt-wrong-round`, `receipt-missing`, `falls-green`.

Prove it in a scratch clone at `{BASE}` with no round-83 rows (expect `accepted=0 unaccepted=8
falls=no`, exit 1) and with the 20 rows from EX02 (poll for
`{WAVE}/w1/EX02LateRows/late82-rows.tsv`; if it never lands, generate the rows yourself with the frozen
generator) appended and committed (expect `falls=yes`, exit 0). Deliver `EX04.json`, `EX04.md` (≤35
lines), both verbatim runs and the selftest output."""),

    item("EX05PinRechecks", "executor", ["freshness"], f"""# EX05 — the pin-recheck counter (executor)

Deliver `{WAVE}/w1/EX05PinRechecks/round83-pin-rechecks.py` plus a draft
`{WAVE}/w1/EX05PinRechecks/pin-recheck-rows.tsv`, and receipts.

Frozen output: `PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0`,
exit 0. Register schema (LF TSV, header row exactly):
`engine\tref\tnewest\tverdict\tdate\tquote_pin\tline_pin\tquote_newest\tline_newest\textract_pin\textract_newest\tnote`
Rules (implement exactly the C3 predicate in `{PLAN}` §C3):
1. One row per data row of `registry/engine-pin-relations.tsv`, keyed `(engine, ref)`; a missing key, a
   duplicated key and an unknown key are `bad`.
2. Each extract path is repo-relative, must exist, and its first line must be
   `# url=<https-url> sha256=<64-hex> ref=<ref> lines=<a>-<b>`; the counter recomputes the file's
   SHA-256 (of the bytes after the header line) and requires it to equal the header digest and the
   row's `newest`/`ref` to agree with the header `ref`.
3. `holds` ⟺ `quote_pin` occurs verbatim in the newest extract; `reworded`/`moved`/`drifted` ⟺ it does
   not occur there and `quote_newest` is non-empty and different. A declared verdict that contradicts
   the byte comparison is `bad` (`verdict-contradicts-bytes`).
4. `quote_pin`/`quote_newest` ≤25 words; the pin quote must occur at its declared `line_pin` in the pin
   extract (same for newest); a violation is `bad`.
5. `ungraded` requires `note` naming the missing document and never counts as `graded`.
Exit 1 with one `PIN_RECHECK_FINDING <class> <detail>` line per finding, 2 when a register is absent
(`could-not-evaluate: no <path>`), and add `--selftest` with arms, each red: `missing-row`,
`duplicate-row`, `unknown-row`, `holds-but-absent`, `drifted-but-present`, `quote-26-words`,
`quote-not-at-line`, `digest-mismatch`, `ungraded-without-note`, `verdict-vocabulary`; and a green
honest fixture.

Draft the five rows from `{LANE}/.ufo/waves/round-82/w1/SK01PinRecon/SK01.md` §7 (relation 1, 2, 4, 5
graded `holds`; relation 3 ungraded) and build small extract fixtures in your seat dir for the
selftest. Do NOT fetch anything for the real register — SK01SourceOpen owns the real extracts; your
job is the counter plus a fixture-proven run. Deliver `EX05.json`, `EX05.md` (≤50 lines) and the
selftest output."""),

    item("SC01Sources", "scribe", ["coverage"], f"""# SC01 — the six `corpus/SOURCES.md` rows for round 83 (scribe)

Deliver `{WAVE}/w1/SC01Sources/rows.md` — the exact table rows to append, in the registry's schema — and
`{WAVE}/w1/SC01Sources/coverage-row.md`.

Read `{LANE}/corpus/SOURCES.md`'s own header and an existing row (the census accepts 0–3 leading
spaces; every row is 11 columns; `recheck` is an ISO date, `NNd` or a symbolic cadence; no cell carries
a literal or escaped `|`). Then write ONE row per source below, each opened by SK01SourceOpen this round
(poll `{WAVE}/w1/SK01SourceOpen/sources.json`; if it never lands, open the URLs yourself with
`curl -sS -o file -w '%{{http_code}} %{{size_download}}'` and record sha256):

| id | URL | tier | status |
|---|---|---|---|
| S566 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md` | A | mined |
| S567 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | A | mined |
| S568 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx` | A | mined |
| S569 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` | A | mined |
| S570 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md` | A | mined |
| S571 | `https://git-scm.com/docs/git-blame` | A | mined |

`used-by` is exactly the entries that cite the row: S566/S564-side → `corpus/knowledge/pin-recheck-rows.md`;
S567/S568 → `corpus/knowledge/pin-recheck-rows.md`; S569/S570 → `corpus/knowledge/pin-recheck-rows.md`;
S571 → `corpus/knowledge/register-row-introduction.md` (the C1 rule's ground). A row whose source you
cannot locate a quote in is `rejected` with reason and flip, never `mined`. Also deliver the single
`corpus/README.md` `## Coverage map` row for the recheck-register ground (one line, same shape as the
existing rows).
Do not edit `corpus/SOURCES.md`. Report the id list, the row count and every quote's location."""),

    item("SC02Lesson", "scribe", ["calibration"], f"""# SC02 — `corpus/lessons/round-83.md` (scribe)

Deliver `{WAVE}/w1/SC02Lesson/round-83.md`, at most 120 lines, with these sections in order:

1. **Title + opening** naming the frozen plan, the base {BASE} and the sealed revision {SEALED}, the
   three claims and their axes.
2. `## Gate` — a table of the six sources S566–S571 opened this round: id, URL, HTTP status, bytes,
   anchor line, a ≤25-word located quote, verdict (admit/reject) and reason/flip. Poll
   `{WAVE}/w1/SK01SourceOpen/sources.json` for the fetched facts (status, bytes, sha256, line numbers);
   never invent one. Every row must carry today's access date 2026-11-04.
3. `## Corrections` — exactly the three `corrected F<n> old=… new=… at={SEALED} date=2026-11-04
   fix=…` lines from `{PLAN}` §C2 in a fenced block, followed by one bullet per fact naming the
   record location, the declared token and the witness command that refutes it.
4. `## Mistakes` — one table row: class · evidence pointer · captured-by (the criterion or rule that
   should have caught it, or `none`) · fix. Use the round-82 `--late` limit (class
   `caller-path-unbound`: a leg that accepts an input it cannot bind reports a per-row verdict instead
   of refusing the input; evidence `{LANE}/.ufo/waves/round-82/measured/defects/` and the round-82
   divergence 1; captured-by `none` — the round-82 control suite exercised only the default path; fix:
   the round-83 path binding plus `late-path-outside-repo`/`late-path-untracked`/`late-path-bound`,
   which the round-83 receipts show able to fail).
5. `## Frontier` — what moved (four graded rechecks, one ungraded), what stays frontier (other engines'
   docs, a live serving runtime), and `Assimilation: none` with its reason.

Do not write the corrections container anywhere else; the C2 counter reads exactly `## Corrections`."""),

    item("SC03Knowledge", "scribe", ["coverage", "freshness"], f"""# SC03 — the admitted entry, the QUALITY criterion and the command correction (scribe)

Deliver three files in `{WAVE}/w1/SC03Knowledge/`:

1. `pin-recheck-rows.md` — a `corpus/knowledge/` entry (≤60 lines) with the provenance trio header
   used by the lane's entries (`source: S567`, `verified-at: 2026-11-04`, a `recheck:` command that
   ACTUALLY runs), stating: the recheck register's schema, why a graded recheck is a byte comparison
   and not a prose judgement, the four-value vocabulary and the `ungraded` class, and the round-83
   verdicts (llama.cpp 1/2 holds at b12110 == b12103, SGLang 4 holds with `/ready` and `/ping` added,
   vLLM 5 holds byte-identical, llama.cpp 3 ungraded). Cite S566–S570 by id. Limit every claim to what
   SK01SourceOpen's fetched bytes show.
2. `kq135.md` — one `corpus/QUALITY.md` criterion row (same four columns as KQ1–KQ134): a
   caller-supplied register path must be bound to a committed identity (repo-relative path plus per-row
   introduction) or refused with exit 2, and a per-row verdict for an unbound input is a defect.
   Motivating lesson: `corpus/lessons/round-83.md` §Mistakes.
3. `pin-recheck-trigger-correction.md` — the appended `## Correction — round 83` block for
   `{LANE}/corpus/knowledge/pin-recheck-trigger.md` (≤12 lines) naming the defective line 5
   (`--repo`) and the corrected command `python3 tools/pin-watch.py check --pins
   registry/engine-pins.tsv`, with the round-82 SK01 D1 pointer.

Verify the recheck command you write by running it once (`--pins` form) and paste its first line and
exit. Do not edit the lane."""),

    item("SK01SourceOpen", "scout", ["freshness"], f"""# SK01 — open the six sources and build the anchor extracts (scout)

Read-only over the network plus writes inside your seat dir. Deliver
`{WAVE}/w1/SK01SourceOpen/sources.json` and the anchor extracts under
`{WAVE}/w1/SK01SourceOpen/anchors/`.

For each URL below: `curl -sS -o <file> -w '%{{http_code}} %{{size_download}}' <url>`, then record
status, bytes, `sha256sum`, line count, and the line number of the anchor you locate. Quote ≤25 words
verbatim. Access date 2026-11-04.

| id | URL | anchor to locate |
|---|---|---|
| S566 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md` | `### GET /health` heading + the sentence "This endpoint is public (no API key check)." |
| S567 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | the `## Health Check` section and any `/ready` or `/ping` rows it adds |
| S568 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx` | the same section at the pinned ref (whether `/ready`/`/ping` are absent) |
| S569 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` | the first sentence stating what prefix caching stores/does |
| S570 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md` | the same sentence at the pinned ref |
| S571 | `https://git-scm.com/docs/git-blame` | the sentence defining the blamed commit for a line (and `--line-porcelain` if present) |

Then produce the six extract files the C3 register reads, one per ref, each with the header
`# url=<url> sha256=<64-hex of the body bytes after this line> ref=<ref> lines=<a>-<b>` and the anchor
region verbatim (≤40 lines). Digest convention: the header's sha256 is the sha256 of the extract's own
bytes after line 1 — compute it after writing, then re-write the header and verify the counter's own
rule reproduces (write a two-line checker in your dir and run it).
Also compare S566 against S563's b12103 read (`{LANE}/.ufo/waves/round-82/w1/SK01PinRecon/raw-fetch-log.md`)
and S569 against S570: state byte-identity or the exact differing bytes.
Deliver `sources.json` ({{"rows": [{{"id","url","status","bytes","sha256","lines","anchor_line","quote"}}], "identity": {{...}}}})
and `SK01.md` (≤45 lines). No writes outside your seat dir."""),

    item("SK02Facts", "scout", ["calibration"], f"""# SK02 — independent re-derivation of the six round-83 facts (scout, read-only)

Do NOT open `{LANE}/tools/round82-selfrecord-round81.py` or any round-83 counter until your six values
are fixed in a file; the counter under test is EX03's draft. From committed bytes only
(`git -C {LANE} show <rev>:<path>`), fix in `{WAVE}/w1/SK02Facts/facts.md` before anything else:

| id | what to read at {SEALED} | what you must decide |
|---|---|---|
| F1 | `LOG.md` §Round 82 C1 bullet's `selftest `pass=<n> fail=0`` | declared n, and what `{LANE}/.ufo/waves/round-82/measured/after/c1-selftest.out` prints |
| F2 | `SCORECARD.md` §Round 82 C1 row's `selftest `pass=<n> fail=0`` | declared n vs the same receipt |
| F3 | `SCORECARD.md` `## Axes` calibration row's `--selftest` → `pass=<n> fail=0` | declared n vs the same receipt |
| F4 | `LOG.md` §Round 82 C2 bullet's `APPEND_DEBT_SELFTEST pass=22 → pass=<n>` | final n vs `…/c2-debt-selftest.out` |
| F5 | `LOG.md` §Round 82 `Frontier: registry 302 → <n> rows` | n vs the `corpus/SOURCES.md` row count at {SEALED} (and at the tip — they must be told apart) |
| F6 | `LOG.md` §Round 82 C2 bullet's `LATE_DELTA … new=<n> bad=0` | n vs `…/c2-late-delta.out` |

For each fact report: file, line number, exact declared string, witness command, witness value, and
`holds` / `stale`. Also record the exact row-count command you used for F5 and its output at both
revisions. Then, and only then, read the round-83 plan §C2 and EX03's draft if it exists, and report
any difference between your fixed values and the draft's table.
Deliver `facts.md` (≤50 lines, the table plus the commands) and `SK02.json`
({{"facts": [{{"id","declared","witness","verdict"}}], "differences": [...]}})."""),

    item("CN01SiblingScan", "connector", ["adjacency"], f"""# CN01 — sibling-overlap scan (connector, read-only)

Scan the fleet's other lane reports and lessons for claims that bind any of these three surfaces, and
say whether kama's round-83 claim is distinct. Read-only: never edit a sibling repo or the fleet root
tree; write only in `{WAVE}/w1/CN01SiblingScan/`.

Surfaces to test:
1. A register whose rows are bound to their own introduction commit (`git blame`) as an acceptance rule.
2. A graded recheck row keyed to an upstream release relation, with a byte comparison deciding the
   verdict (`{LANE}/corpus/knowledge/pin-recheck-trigger.md` is kama's held entry).
3. A self-record counter that grades a previous round's declared facts with value-bound corrections.

Search `/home/vgpnk/Projects/shokunin/.ufo/reports/round-*/` and each `*-shokunin/corpus/lessons/` for
this session's live lanes (chousa, tabi, souji, tsukuroi, kengaku, tameshi, mori, kaidoku, kasegi, mado
if present). For each hit record: lane, round, file:line, the exact claim sentence, and a verdict
`overlap` (same surface, competing owner), `adjacent` (different surface, same technique) or `none`.
A finding that a sibling binds per-row register introduction would be a contested-scope handoff: name
the lane and the artifact, do not absorb it.
Deliver `CN01.md` (≤50 lines: the table, the search commands, and a one-paragraph verdict) and
`CN01.json`."""),

    item("RV01AttacC1", "reviewer", ["operability"], f"""# RV01 — attack C1 (reviewer)

Attack the `--late` binding and the pending-fall leg. The claims are frozen in `{PLAN}` §C1; the base
state and the target lines are there. Read-only outside your seat dir; write findings in
`{WAVE}/w1/RV01AttacC1/`.

Try, with commands, at least these escapes against EX01's draft (poll for
`{WAVE}/w1/EX01LateBinding/round81-append-debt.py`; if it never lands, attack the current
`{LANE}/tools/round81-append-debt.py` and say so):
1. `--late` naming a copy of the register inside the repo but untracked → must be exit 2, not a verdict.
2. `--late` naming a symlink that resolves outside the repo → must be exit 2.
3. `--late` on a register whose rows all predate their events → must be `not-descendant`, not green.
4. `--late` on the default path with `--register` also given, and the reverse → the two paths must not
   be confused.
5. A register row copied byte-for-byte from another round's row but with the note edited to name round
   83 → must fail on the note/round cross-check the rule requires.
6. `--base` mismatching the plan → exit 2.
7. For EX04: a receipt whose `pending` is 0 while the window is 8; a window event covered by a row that
   names a different commit; a `--json` output whose `falls` disagrees with the summary.
Report each attempt as `escape` (green while it should be red) or `blocked`, with the exact command,
its output and its exit. Write the single most serious escape first. Deliver `RV01.md` (≤40 lines) and
`RV01.json`."""),

    item("RV02AttackC2", "reviewer", ["calibration"], f"""# RV02 — attack C2 and C3 (reviewer)

Attack the self-record counter's fix leg and the recheck counter's byte rule. Frozen text:
`{PLAN}` §C2 and §C3. Read-only outside your seat dir; write findings in
`{WAVE}/w1/RV02AttackC2/`.

Against EX03's draft (poll for `{WAVE}/w1/EX03SelfRecord/round83-selfrecord-round82.py`; if absent,
state that and attack the plan text's reachability instead):
1. Write the `new` token only into `corpus/lessons/round-83.md` → must be `unbacked` (`lesson-only-token`).
2. Write it only inside a `LOG-CORRECTION` line or a `#### round-83 correction` block of the fix path →
   must be `unbacked` (`token-only-in-correction-region`).
3. A correction whose `new` token is a prefix of a longer token present in the fix path
   (`…=233`) → must not back the correction.
4. A correction for F4 (which holds) or a second correction for F1 → `unbacked` + mismatch.
5. An `at=` naming the base instead of the sealed revision, and an `at=` naming a descendant → both red.
6. F5 with the tip registry (309 rows) substituted for the sealed 305 → the F5 arm must catch it.
Against EX05's draft (poll for `{WAVE}/w1/EX05PinRechecks/round83-pin-rechecks.py`):
7. An extract whose header digest matches the file but whose quote sits on a different line than
   declared; a 25-word quote passed as 26 by adding a period; an `ungraded` row counted by the
   summary's `graded`; a row whose engine/ref exists twice with different verdicts.
Report each as `escape` or `blocked` with command, output and exit; most serious first.
Deliver `RV02.md` (≤40 lines) and `RV02.json`."""),

    item("CR01FalsifyClaims", "critic", ["calibration", "operability"], f"""# CR01 — falsify the three claims as written (critic)

Read `{PLAN}` in full, then attack the PREDICATES, not the implementations: does each frozen sentence,
read literally, name a state the round can reach, and is its counting command the sentence's own?
Read-only outside your seat dir; write in `{WAVE}/w1/CR01FalsifyClaims/`.

Check at least:
1. **Reachability**: for each target line, derive the arithmetic from the tree at {BASE} — C1
   `events=76 accepted=53 late=35 pending=<p>`: is `accepted` a constant or does it move when rows are
   appended? what is `pending` at the tip and does the target's `<p>` placeholder hide a miss? C2
   `corrected=3` against six facts: is any fourth fact stale that the plan's table omits (sweep
   `LOG.md` §Round 82, `SCORECARD.md` §Round 82 and the head rows for every tallied number and compare
   each with its receipt)? C3 `rows=5 graded=4`: does the relation register have exactly five data rows
   today, and does `pin-watch` today report the same `newest` values the plan's rows assume?
2. **Literal reading**: the phrase "the same summary line as leg A" — is `pending` the same? the phrase
   "per-row introduction" — does `git blame` on a register line change under a later whitespace-only
   edit? the phrase "a token that appears only in the lesson itself" — is the EX03 reading the plan's?
3. **Causally separable**: can C2 land without C1 and C3? Name the coupling if not.
4. **Harm**: does any target require editing a file another claim's receipt measures, in a way that
   moves that receipt's numbers?
Deliver `CR01.md` (≤50 lines: findings ordered by severity, each with the file:line it reads and the
command that shows it) and `CR01.json`. A finding you cannot show with a command is labelled
`argument` and ranked last."""),

    item("MT01Mutants", "mutation-tester", ["operability", "calibration"], f"""# MT01 — mutate the new selftests and report escapes (mutation-tester)

Poll for EX01, EX03, EX04 and EX05's drafts in `{WAVE}/w1/<Seat>/`; grade whichever have landed, and
say which had not. Work only in your seat dir and a scratch clone of the lane at {BASE}.

For each landed module, apply ONE mutation at a time to the module's own source in the clone, re-run
its `--selftest`, and record which arm(s) go red. A mutant that leaves every arm green is an escape and
is the headline. Minimum mutants per module when it lands:
- EX01 `round81-append-debt.py`: (a) drop the repo-containment check; (b) bind `row_marks` from the
  register's introduction instead of blame; (c) accept an untracked path; (d) make `--late` ignore the
  flag and read the default; (e) invert the strict-descendant test.
- EX03 `round83-selfrecord-round82.py`: (a) skip the `lesson-only-token` clause; (b) skip the
  correction-region clause; (c) read F5 at the tip instead of the sealed revision; (d) accept a
  correction for a holding fact; (e) relax the `at=` check.
- EX04 `round83-pending-falls.py`: (a) print `falls=yes` when `declared != window`; (b) count a row
  covering one line of a multi-line event as full coverage; (c) read the round-83 base from the receipt
  instead of the plan.
- EX05 `round83-pin-rechecks.py`: (a) trust the declared verdict instead of the byte comparison; (b)
  skip the digest recomputation; (c) count `ungraded` in `graded`.
Record per mutant: module, mutation (one sentence), the exact re-run command, red arms, escaped arms.
Also run each honest module's `--selftest` and record its tally. Deliver `MT01.json`
({{"mutants": [{{"module","mutation","red":[],"escaped":[]}}], "tallies": {{...}}}}) and `MT01.md` (≤40
lines, escapes first)."""),
]

SPEC = {
    "wave": "w1",
    "lane": "kama",
    "round": 83,
    "policy": "v1",
    "reportDir": ".ufo/waves/round-83/w1",
    "context": CONTEXT,
    "items": ITEMS,
}

if __name__ == "__main__":
    out = Path(WAVE) / "w1-spec.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    spec = {"wave": "w1", "milestone": "kama r83 w1",
            "reportDir": ".ufo/waves/round-83/w1", "maxLanes": 16,
            "axes": ["operability", "calibration", "freshness", "coverage", "adjacency"],
            "context": CONTEXT, "items": ITEMS}
    out.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {out} items={len(ITEMS)}")
