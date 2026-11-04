#!/usr/bin/env python3
"""Build the round-79 wave-1 spec (one v1 wave, 14 seats) from the frozen claims plan.

Every prompt is absolute-path scoped to the lane and carries the same hard rules block.
Run: python3 .ufo/waves/round-79/build-spec.py  -> writes w1-spec.json beside this file.
"""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
WAVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79"
SCRATCH = "/fast/scratch/hyaku/kama-r79"
BASE = "ee53f1a25eab93a8ab55bbb877e49e2e731df535"
FREEZE = "331037039c30909aa2163b2d1de22a7964f90420"
SEALED = "7a3cd98243b69fcbee0cc9e31878782bd8459320"

CONTEXT = f"""# Goal
kama lane, round 79: ONE v1 wave of 14 seats (build + attack) against the frozen claims in
{LANE}/plans/round-79-claims.md — read that file in full before your item and treat its
blockquote predicates, fact value strings and target lines as frozen text. Base revision {BASE};
the freeze commit is {FREEZE} (the commit adding the plan and the C1 counter). The sealed revision
C1 grades is {SEALED} (round 78's tip). Lane tip is read with
`git -C {LANE} rev-parse master` (git HEAD is detached; never `@{{u}}` or `--abbrev-ref HEAD`).

# Write scope (hard)
You may write ONLY inside {LANE} plus your own seat directory under {WAVE}/w1/<YourSeatName>/.
Never touch the fleet root /home/vgpnk/Projects/shokunin (no MANIFEST.json, templates/, scripts/,
.ufo/state/, .ufo/watchdog.log, .scratch/, l0-questions.md), never a sibling repo, never
/home/vgpnk/Projects/shokuknow. An item that names no repository path is read-only outside its seat dir.

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
(trap 'rm -rf -- "$S"' EXIT; Python: finally: shutil.rmtree) after copying receipts into the wave dir.
A seat that leaves its tree reports that as its own defect. Never mirror the whole lane into a wave build dir.

# Absolute paths
Your tools start at the fleet root, not the lane. Every path you read or write must be absolute under
{LANE}. Every `Report:` trailer path the dispatch shows is relative to {LANE} — write it at
{LANE}/<that path>.

# Tooling authorization (operator, 2026-10-19)
You may install or upgrade tools that help the task: read /home/vgpnk/.omp/agent/RULES.md first
(official channels, update-safety gate; record tool/version/channel/reason in your report). All pacman
transactions are PAUSED host-wide (orchestrator ruling 2026-10-20): install via `uv tool`, `npx`, or an
official binary into ~/.local/bin; never -Sy/-Syu/-U/-R, never restart a host service. Named items
require no installs.

# Claims (frozen; do not edit the plan)
C1 calibration: `python3 tools/round79-selfrecord-round78.py --repo .` must print
`SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0`, exit 0. Pre-freeze: `SELFRECORD_R78_ENUM
claims=6 stale=2 corrected=0`, exit 1; the two stale facts are F5 (tip accounting names 22cce544,
not the sealed tip) and F6 (the pre-correction run is prose, no committed receipt).
C2 operability: `python3 tools/pre-report-gate.py --selftest` must print `PRE_REPORT_SELFTEST pass=26
fail=0` and a scored run at the round-79 tip must print `PRE_REPORT round=79 arms=10 failed=0
uncommitted=0`. Base: 9 arms, `pass=22`.
C3 coverage: `python3 tools/round79-unregistered-census.py --repo .` must print one
`UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` line, exit 0, where
`bash tools/kama-probe.sh listeners` classifies a serving listener by whether the registry declares its
port (`registered` column `yes`/`no`/`-`; summary keys `governed`/`unregistered`). Base: no class column.

# Seat rules
You are a leaf. An executor may spawn at most one read-only labrat probe; no other role spawns anyone
and no seat runs a swarm. Never message agent://all; message nothing outside your item. Do not commit,
do not edit another seat's files, do not run pre-report-gate.py in scored mode (L1 does). A dead seat
stays dead in the evidence: report every failure with its last error text, never fabricate a run.
Report every receipt path as an absolute path plus its command and exit code.
Sibling seats run at the same time: it is normal for a module you need to be missing at your start.
Attack seats poll for it (`sleep 30`, up to 25 minutes) before grading, and report honestly if it never
lands. Never edit a file another seat owns — write the finding in your report instead.
"""

ITEMS = [
    ("EX01C1Facts", "executor", ["calibration"], f"""
# EX01 — independent re-derivation of the six round-78 facts (executor)
Build an independent derivation harness at {WAVE}/w1/EX01C1Facts/rederive.py that does NOT import the
lane counter: read the round-78 record with `git -C {LANE} show {SEALED}:SCORECARD.md`, parse the six
facts exactly as {LANE}/plans/round-79-claims.md §C1 states them (F1 lowest-axis, F2 population,
F3 wave shape, F4 dead seats, F5 tip accounting, F6 pre-correction receipt), and print per fact
`EX01 <Fk> declared=<value> observed=<value> match=yes|no`. Write the output to
{WAVE}/w1/EX01C1Facts/rederive.out with its command and exit code. Then check the lane counter
`python3 tools/round79-selfrecord-round78.py --repo . --enumerate` agrees on the stale set, and report
any disagreement as a finding with both value strings. Do not edit tools/.
"""),
    ("EX02GateArm", "executor", ["operability"], f"""
# EX02 — wire the three round-78 instruments into the pre-report gate as arm 10 (executor)
You own exactly one file: {LANE}/tools/pre-report-gate.py.
Implement the frozen C2 predicate: a tenth arm named `round78-instruments` after `round77-instruments`,
running `round78-selfrecord-round77.py --selftest`, `round78-append-registers.py --selftest` and
`round78-live-reconcile.py --selftest` from <repo>/tools (or --tools-dir), each required to exit 0 and
print a final `*_SELFTEST pass=N fail=0` summary; absent, red or malformed fails the arm closed naming
it (`missing <script>` for absence). Update PREDICATE, the module docstring arm list and the historical
`arms=` prose so the shipped text matches the module, and extend `--selftest` with exactly four new
cases, so the tally moves 22 -> 26: (v) red round78 stub fails the arm naming its instrument;
(w) absent round78 module fails the arm naming `missing <script>`; (x) green round78 stubs yield a
scored `arms=10` verdict; (y) a malformed summary line (no `pass=N fail=0`) fails the arm. Keep
existing cases green (update their expected verdict lines to `arms=10` where they assert the count) and
keep the wave-dir `uncommitted` case red-capable. Run the selftest and write its full output plus the
final line to {WAVE}/w1/EX02GateArm/gate-selftest.out. Do not run the scored gate.
"""),
    ("EX03ProbeClass", "executor", ["coverage"], f"""
# EX03 — add the unregistered-serving-listener census class to the probe (executor)
You own exactly one file: {LANE}/tools/kama-probe.sh.
In `listeners` only: read the registry's declared baseURL ports (registry TSV column 4, tolerant of a
missing/unreadable registry: class stays `-` with a warning, never a probe error), append one last
table column `registered` (`yes` when a model-API listener's port is declared by a registry row, `no`
when it answers a model surface but no row declares it, `-` for non-model listeners), add per-row
`"registered": "..."` to the JSON and summary keys `governed`/`unregistered` after `model_loading`.
Do not change the verdict vocabulary, exit codes, or any other subcommand. Prove it with a scratch
registry and a fake JSON responder on an ephemeral loopback port under your scratch root: capture the
same listener as `registered=no` (registry without the port) and `registered=yes` (registry with it) to
{WAVE}/w1/EX03ProbeClass/probe-class.out, with `bash -n` clean and the command/exit recorded. Do not
edit tools/round79-unregistered-census.py (EX04 owns it).
"""),
    ("EX04CensusCounter", "executor", ["coverage"], f"""
# EX04 — build the C3 counter against the frozen class contract (executor)
Create {LANE}/tools/round79-unregistered-census.py. Frozen contract: `--repo` (default .), `--probe`
(default <repo>/tools/kama-probe.sh), `--selftest`, `--work`; it starts the lane-owned pinned
llama-server (~/.local/opt/llama-b11755/llama-server with ~/.cache/kama-shokunin/models/stories260K.gguf)
on a free loopback port that is neither a registered consumer port nor listening, writes two scratch
registries (one without the fixture port, one declaring it), runs `<probe> listeners --json --registry
<scratch>`, and prints one `UNREGISTERED_CENSUS port=<p> unregistered=<u> governed=<g>
class_missing=<c> rows=<n>` line with exit 0 only when u=1, g=1, c=0; a probe whose output lacks the
`registered` class prints class_missing=1 and exits 1; a probe error is exit 2. Add `--selftest` arms
proving: class-missing probe red, absent probe exit 2, both registry legs, and teardown (port closed).
Use TMPDIR/--work for scratch and never write the lane registry. Write the module's own selftest output
to {WAVE}/w1/EX04CensusCounter/selftest.out. EX03 owns kama-probe.sh; if the class is not yet present,
test against a stub probe of your own under your seat dir and say so.
"""),
    ("SC01Sources", "scribe", ["coverage"], f"""
# SC01 — source row, Gate block and census receipts (scribe)
Draft the round-79 SOURCES append block in {WAVE}/w1/SC01Sources/sources-append.md: one row for the
llama.cpp router `GET /models` surface at commit 39febd2adb947b70da35e95f9351b3bf58ad170a
(https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md),
kind docs, tier A, scope limited to "router model list is an inventory: unloaded models are listed and
each carries status.value", anchor "§Router mode, GET /models note 1, line 2227", status mined,
opened 2026-11-04, recheck on-release, used-by corpus/knowledge/unregistered-listener-census.md.
Re-open the URL yourself this round, record HTTP status, bytes and sha256, and put the located
<=25-word quote plus its line number in a `## Gate` block text. Check for duplicate-id and duplicate-URL
collisions against {LANE}/corpus/SOURCES.md (0-3 leading spaces pattern) and report the next free S-id.
Do not edit corpus/SOURCES.md; the L1 appends. Also record the round-79 census before/after counts with
their command and exit in the same file. Never invent a quote: a fetch failure is an honest stop.
"""),
    ("SC02Knowledge", "scribe", ["coverage"], f"""
# SC02 — knowledge entry draft: the unregistered-listener census class (scribe)
Draft {WAVE}/w1/SC02Knowledge/unregistered-listener-census.md in the lane's entry shape: `source:`,
`verified-at:`, `recheck:` first, then: what the class is (a serving listener that answers a model API
and whose port no registry row declares), the exact probe surface (`registered` column values, summary
keys `governed`/`unregistered`), why a model list is inventory not readiness (cite the S-row SC01
drafts and the round-78 live observation {LANE}/.ufo/waves/round-78/measured/observation/unregistered-1234.out
if you re-read it), what it does NOT claim (no loaded model, no consumer readiness, no registry row),
and the live-host reading rule. Keep it under 90 lines, absolute-path free in prose, and add the
coverage-map row text for {LANE}/corpus/README.md in a fenced block at the end. Do not edit
corpus/knowledge/; the L1 lands the entry.
"""),
    ("SC03Lesson", "scribe", ["calibration"], f"""
# SC03 — round-79 lesson draft: Gate, Mistakes, Corrections (scribe)
Draft {WAVE}/w1/SC03Lesson/round-79.md with: an opening that names the three claims and the wave; a
`## Gate` section recording the round's candidates (the llama.cpp router row admit with URL, access
date and <=25-word located quote; a rejected candidate with reason and flip; the own-work instrument
class note); a `## Mistakes` row for the round-78 "tip" wording (class `stale-premise` or `number-drift`
as you judge, evidence {LANE}/corpus/lessons/round-78-verifier-spotcheck.md §1 defect 1 and
{LANE}/SCORECARD.md §Round 78 §Gate and tip state, captured-by the new F5 fact, fix the correction);
and a `## Corrections` section with exactly two blocks in the frozen shape, F5 and F6, at={SEALED}
date=2026-11-04, old values exactly the plan's declared strings, new values
`tip-accounting=rev:22cce544/is-tip:false` and
`c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/c1-pre-correction.out`. Do not edit
corpus/lessons/; the L1 lands the file.
"""),
    ("SCT01Recon", "scout", ["calibration"], f"""
# SCT01 — read-only reconnaissance: does the C1 fact set catch a do-nothing round? (scout)
Read {LANE}/plans/round-79-claims.md §C1 and {LANE}/tools/round79-selfrecord-round78.py. Re-derive each
of the six facts by hand from committed bytes at {SEALED} (git show only) and write
{WAVE}/w1/SCT01Recon/facts.md: per fact, the command, its output, and whether the counter's value string
matches. Then build the cheapest do-nothing control yourself in a scratch clone: a round-79 tree with no
corrections at the tip, run through the counter, and report the exact line, exit, and whether it can
ever reach the target. Name any fact the counter would accept without the record actually saying it
(vacuity), and any fact whose declared parse would survive a wrong record value (insensitivity).
Read-only: no lane writes.
"""),
    ("SCT02Source", "scout", ["coverage"], f"""
# SCT02 — open the cited source and grade the quote (scout)
Fetch https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
(read-only network), record HTTP status, byte count and sha256, then verify: (1) the quote
"If a model is not running, it will be added or updated according to the source" is present verbatim at
the line number SC01 claims; (2) the surrounding section is the router `GET /models` surface; (3) the
`status.value` vocabulary (loaded/loading/unloaded/sleeping) is documented there; (4) whether the same
URL is already held by an existing SOURCES row and at which scope. Write
{WAVE}/w1/SCT02Source/source-check.md with command, output, exit. If the network fails, record the
failure and the sha256 of any retained local copy under /home/vgpnk/src/llama.cpp, marking it as a
local-copy check, not an opened URL.
"""),
    ("CN01Connector", "connector", ["adjacency"], f"""
# CN01 — sibling-overlap scan for the three claims (connector)
Read {LANE}/plans/round-79-claims.md and scan the sibling lanes' repos at /home/vgpnk/Projects/shokunin
(read-only: */PROVINCE.md, */SCORECARD.md newest round sections, */tools names). Report at
{WAVE}/w1/CN01Connector/overlap.md: for each claim, which sibling owns adjacent ground (e.g. kumitate
route/registry mechanisms, kengaku eval, tameshi/tsukuroi gates, chousa pinning method), whether our
change takes any of it, and the exact file:line evidence for each overlap or non-overlap. Flag any
sibling that already ships an equivalent gate arm or listener census class, with its path, so the L1
can name the boundary in the report. Do not write outside your seat dir.
"""),
    ("RV01Reviewer", "reviewer", ["operability"], f"""
# RV01 — independent verification of the three controls (reviewer)
Verify, from committed bytes and your own runs, that each claim's control cannot reach its target:
C1 — run `python3 tools/round79-selfrecord-round78.py --repo . --enumerate` and the scored form at the
current tip; C2 — run `python3 tools/pre-report-gate.py --selftest` and record arm count, tally and each
new case; C3 — run `python3 tools/round79-unregistered-census.py --repo .` (or a base copy) and record
whether `class_missing` moves. Also verify the two corrections the L1 appends are value-bound (old
re-derives at {SEALED}, new re-derives at tip) and the F6 receipt really carries `mismatches=1`. Write
{WAVE}/w1/RV01Reviewer/verify.md with every command, output, exit, and a per-claim
agree/disagree verdict with reasons. Poll up to 25 minutes for modules that are not yet present; report
honestly if they never land.
"""),
    ("CR01Critic", "critic", ["calibration"], f"""
# CR01 — falsify C1 and C2 (critic)
Attack the frozen predicates in {LANE}/plans/round-79-claims.md. For C1: can a do-nothing round reach
`mismatches=0 corrected=2`? Can a correction with a plausible-but-wrong `new` pass? Does the counter
read the record at the sealed revision or leak the worktree? Do the six facts cover the round-78
defects they claim (R78V1/V2) and could a seventh obvious falsehood pass ungraded? For C2: does the new
arm actually execute the three instruments (not a stub), does an absent module fail closed, does the
selftest tally move for the right reason, and does the SKILL row have to agree at the tip? Write
{WAVE}/w1/CR01Critic/attack.md with each attack, the command you ran, its output and a
survived/killed verdict. Never edit lane files.
"""),
    ("CR02Critic", "critic", ["coverage"], f"""
# CR02 — falsify C3 (critic)
Attack the census class: (a) does a registered port ever read `registered=no`? (b) does a non-model
listener get counted `unregistered`? (c) does the counter's two-registry leg prove classification or
just echo the registry file? (d) can the counter pass with a probe that prints the summary keys but no
column, or vice versa? (e) does the class leak into the verdict vocabulary or a registry write? (f) is
the sourced rule actually implied by the cited quote, or does the entry claim more than the source
says? Write {WAVE}/w1/CR02Critic/attack.md with each attack, the command, output and
survived/killed verdict, plus the exact fix you would require. Never edit lane files.
"""),
    ("MT01Mutation", "mutation-tester", ["operability"], f"""
# MT01 — mutation-test the new class and the new gate arm (mutation-tester)
Build mutants in a scratch clone ({LANE} copied with `git clone --shared` under your scratch root):
(1) probe mutant A: `registered=yes` for every model listener (drops the registry relation);
(2) probe mutant B: summary keys present but the column omitted; (3) probe mutant C: registry port
extraction reads column 3 instead of 4; (4) gate mutant: arm 10 runs only the first instrument;
(5) gate mutant: arm 10 treats a nonzero instrument exit as pass. Each mutant must be *caught* by the
shipped counter/selftest for its owner (C3 counter for 1-3, gate selftest scored fixtures for 4-5);
report any survivor with its command and output. Write {WAVE}/w1/MT01Mutation/mutants.md with the
mutant diff, killer command, output line and killed/survived per mutant. Never mutate the lane repo.
"""),
]


def main() -> None:
    items = [{"name": name, "role": role, "axes": axes,
              "milestone": "kama r79 w1",
              "prompt": f"/skill:godspeed\nYou are a Godspeed-enabled subagent.\n\n"
                        "1. **Name the axes.**\n2. **Iterate cheap, in parallel.**\n"
                        "3. **Keep moves that improve any axis and harm none.**\n"
                        "4. **Don't aim \u2014 let the frontier walk itself.**\n\n"
                        "## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls "
                        "concurrently in large batches. Do not serialize what can run in "
                        "parallel. Do not output philosophical reasoning or verbose plans. Act "
                        "directly via tool calls.\n" + prompt.strip() + "\n"}
             for name, role, axes, prompt in ITEMS]
    spec = {"wave": "w1", "milestone": "kama r79 w1",
            "reportDir": ".ufo/waves/round-79/w1", "maxLanes": 16,
            "axes": ["calibration", "operability", "coverage"],
            "context": CONTEXT, "items": items}
    out = Path(__file__).with_name("w1-spec.json")
    out.write_text(json.dumps(spec, indent=2) + "\n")
    roles = {}
    for item in items:
        roles[item["role"]] = roles.get(item["role"], 0) + 1
    attack = sum(v for k, v in roles.items()
                 if k in ("reviewer", "critic", "mutation-tester", "labrat"))
    print(f"items={len(items)} roles={roles} attack={attack}/{len(items)}")
    print(out)


if __name__ == "__main__":
    main()
