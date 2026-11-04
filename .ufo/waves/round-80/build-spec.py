#!/usr/bin/env python3
"""Build the round-80 wave-1 spec (one v1 wave, 13 seats) from the frozen claims plan.

Every prompt is absolute-path scoped to the lane and carries the same hard-rules block.
Run: python3 .ufo/waves/round-80/build-spec.py  -> writes w1-spec.json beside this file.
"""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
WAVE = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80"
SCRATCH = "/fast/scratch/hyaku/kama-r80"
BASE = "c45fc7d1a8427e9c98a9dd7befa542c7b5caed38"
SEALED = "a9b4543f14625d0f37daa42ef664ee6f6ea975ea"

GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim \u2014 let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
kama lane, round 80: ONE v1 wave of 13 seats (build + attack) against the frozen claims in
{LANE}/plans/round-80-claims.md — read that file in full before your item and treat its
blockquote predicates, fact value strings and target lines as frozen text. Base revision {BASE};
the sealed revision C1 grades is {SEALED} (the round-79 record tip). Lane tip is read with
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
C1 calibration: `python3 tools/round80-selfrecord-round79.py --repo .` must print
`SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, exit 0. The six facts F1–F6 and their
value strings are tabulated in the plan; F4/F5/F6 are stale at the base and the three corrections
(`corrected F<n> old=… new=… at={SEALED} date=2026-11-04`) live in `corpus/lessons/round-80.md`
§Corrections.
C2 freshness: `python3 tools/round80-engine-pin-relations.py --repo .` must print
`PIN_RELATIONS engines=3 refs=5 unexplained=0`, exit 0, over `registry/engine-pin-relations.tsv`
(llama.cpp b11755 / 39febd2a / b7200, sglang v0.5.22, vllm v0.32.0).
C3 operability: `python3 tools/round80-ollama-census.py --repo .` must print one `OLLAMA_CENSUS
port=<p> engine=ollama unregistered=1 governed=1 class_missing=0` line, exit 0, against the pinned
Ollama v0.40.11 child, and `--audit` must print `CLASS_ENGINES engines=2 verified=2 stale=0`, exit 0.

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


def item(name, role, axes, prompt):
    return {"name": name, "role": role, "axes": axes, "milestone": "kama r80 w1",
            "prompt": GODSPEED + prompt}


ITEMS = [
    item("EX01C1Rederive", "executor", ["calibration"], f"""# EX01 — independent re-derivation of the six round-79 facts (executor)
Write `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/EX01C1Rederive/rederive.py`:
it must NOT import or read `tools/round80-selfrecord-round79.py` (open it only after your own values
are fixed). Re-derive each of the six facts of the round-79 self-record independently from
`git -C {LANE} show {SEALED}:…` and `git -C {LANE} show <tip>:…`:
F1 the lowest assigned axis (calibration 7) from the sealed `## Axes` table over the assigned pair
operability + calibration; F2 `population=sources:293,knowledge:52` (source-row count with
`grep -cE '^\\|[[:space:]]*S[0-9]{{3,}}[[:space:]]*\\|'`; knowledge blobs minus the two filtered
`engine-sides`/`processes`); F3 the wave shape from `.ufo/waves/round-79/w1-spec.json` (14 seats, role
counts, attack = reviewer+critic+mutation-tester = 4/14); F4 the C2 verdict the record declares
(`**verified**` / banner "C2 operability verified") against what
`.ufo/waves/round-79/measured/after/c2-gate.out` actually prints; F5 the C2 before cell
(`PRE_REPORT_SELFTEST pass=26`) against `.ufo/waves/round-79/measured/before/c2-gate-arms.out`; F6 the
LOG sentence "all verified on their receipts" against F4's receipt verdict.
Emit one JSON receipt `EX01.json` into your seat dir with, per fact, `declared`, `observed_sealed`,
`observed_tip`, `match`, plus a top-level `stale` list; then compare with the lane counter (run
`python3 tools/round80-selfrecord-round79.py --repo {LANE}` once it exists; if it does not exist after
25 minutes, report that) and state `agreement` or the exact disagreement. Copy your receipt and script
into `{WAVE}/w1/EX01C1Rederive/` before you yield."""),

    item("EX02C2TagList", "executor", ["freshness"], f"""# EX02 — live upstream tag lists and the pin arithmetic (executor)
For each engine in `{LANE}/registry/engine-pins.tsv`, run
`git ls-remote --tags <repo>` (network; the mechanism `tools/pin-watch.py` uses) and write the raw
output to `{WAVE}/measured/after/c2-tags/<engine>.txt` (create the directory). Then compute, with your
own script `{WAVE}/w1/EX02C2TagList/pinmath.py`, for each of these five refs:
llama.cpp `b11755` (tag), llama.cpp `39febd2adb947b70da35e95f9351b3bf58ad170a` (commit anchor, S553),
llama.cpp `b7200` (tag, kengaku S178), sglang `v0.5.22` (tag), vllm `v0.32.0` (tag):
newest release tag of that engine, `newer` count of release tags with a greater version key, and for a
tag ref its peeled commit oid; for a commit anchor whether it equals any tag's peeled oid. Write
`EX02.tsv` (engine, ref, kind, newest, newer, peeled, is_tag_tip) and a receipt `EX02.json` with the
commands and exit codes. Also run `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`
and copy its output into `{WAVE}/measured/before/c2-pinwatch.out`. Do not write anything under
`registry/` (the L1 owns the register)."""),

    item("EX03C3Precheck", "executor", ["operability"], f"""# EX03 — Ollama v0.40.11 fixture precondition and capture (executor)
Prove the lane-owned Ollama child runs on this host and capture what the census class will read.
Start `$HOME/.local/opt/ollama-v0.40.11/bin/ollama serve` with `OLLAMA_HOST=127.0.0.1:<free port>`,
`HOME=$S/home`, `OLLAMA_MODELS=$S/models`, on a port that is neither a registry-declared consumer port
(`{LANE}/registry/endpoint-consumers.tsv`) nor currently listening. Create one model from
`$HOME/.cache/kama-shokunin/models/stories260K.gguf` via `ollama create <nonce> -f <Modelfile>`; capture
`GET /api/version`, `GET /api/tags`, `GET /v1/models`, `GET /api/ps` (status, bytes, sha256, verbatim
body) into `{WAVE}/w1/EX03C3Precheck/captures/`; tear the child down and prove the port is closed. Grade
whether `/v1/models` answers with a model array (the probe `{LANE}/tools/kama-probe.sh listeners` only
reads `/v1/models`). Write `EX03.json` with the lifecycle, command lines, exit codes and the
`/v1/models` verdict. Never write under `~/.config`, `~/.omp`, systemd, or the lane; the child's HOME is
your scratch dir. If a prerequisite is absent, record the exact error and exit 2 — never fabricate."""),

    item("EX04Defects", "executor", ["operability"], f"""# EX04 — routed-defect repairs with red-before/after receipts (executor)
Two round-79 routed defects, both in lane files you own for this item:
(1) `{LANE}/tools/round78-live-reconcile.py` `--selftest` writes its receipt to
`{LANE}/.ufo/waves/round-78/measured/after/cl3-selftest.json|out` regardless of cwd, so every scored
pre-report gate run dirties two tracked files after the cleanliness arm has passed. Make the selftest
write under `TMPDIR` (honour `--scratch`/`--work` if the module has one) and never into a committed
wave dir; keep the `LIVE_RECONCILE_SELFTEST pass=N fail=0` summary and the four arms intact. Show
red-before: run the base module (`git -C {LANE} show {BASE}:tools/round78-live-reconcile.py` into your
scratch) and record `git -C {LANE} status --porcelain` before/after; show the fixed module leaves the
tree clean.
(2) `{LANE}/tools/pre-report-gate.py` docstring: R79V7 — its "Arms, in fixed order" list numbers 11
arms including a `round76-instruments` entry that `ARM_ORDER` does not contain, while `SKILL.md` and
the verdict line say ten arms. Fix the prose only (no behaviour change: docstring/PREDICATE wording),
and align `{LANE}/tools/round79-selfrecord-round78.py`'s `Facts` docstring list (R79V3: F1 is the
lowest-axis fact, F2 the population fact) with its code.
Write `EX04.json` with every command, exit code and the two receipts; never touch any other tool."""),

    item("SC01Lesson", "scribe", ["calibration"], f"""# SC01 — draft `corpus/lessons/round-80.md` (scribe)
Draft the round lesson at `{WAVE}/w1/SC01Lesson/round-80.md` (the L1 files it under
`{LANE}/corpus/lessons/round-80.md`). Required sections, in this order:
1. `## Gate` — one row per candidate source considered this round, with URL, access date, a ≤25-word
located quote and admit/reject + reason + flip. Candidates: Ollama `docs/api.md` at tag v0.40.11
(`https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md`, `## List Local Models` /
`GET /api/tags`); a supersession of S553 (llama.cpp router `GET /models`, anchor corrected to
`### GET /models: List available models`, note 1, line 2227); llama.cpp `docs/preset.md` (REJECT with
its flip: no claim in this round parses a preset). Open every URL yourself this round with `curl` and
record status, bytes and sha256; never copy a date or quote you did not verify.
2. `## Corrections` — exactly three backticked blocks, byte-exact:
   `corrected F4 old=c2=verified new=c2=not-verified:failed=1 at={SEALED} date=2026-11-04`
   `corrected F5 old=before-selftest=pass=26 new=before-selftest=pass=22 at={SEALED} date=2026-11-04`
   `corrected F6 old=log=all-verified new=log=c2-not-verified at={SEALED} date=2026-11-04`
   plus one prose paragraph per correction saying what the round-79 record claimed and what its own
   receipt prints.
3. `## Mistakes` — one row with class · evidence pointer · captured-by · fix, for the mined mistake:
   "the round-79 record states C2 `verified` in three places while its own cited receipt prints
   `failed=1`", captured-by the new F4/F5/F6 facts, fixed by the counter plus the KQ criterion.
Do not write anywhere but your seat dir. Do not invent a quote: every Gate row needs its own `curl`
receipt in your seat dir."""),

    item("SC02Sources", "scribe", ["coverage"], f"""# SC02 — draft the round's SOURCES rows, knowledge entry and QUALITY criterion (scribe)
Draft into `{WAVE}/w1/SC02Sources/` (the L1 files them):
1. `sources-rows.md` — three table rows in the exact 11-column contract-v1 shape used by
`{LANE}/corpus/SOURCES.md` (`| id | source | kind | tier | scope | anchor | teaches | status | opened |
recheck | used-by |`, no `|` inside a cell): **S554** Ollama `docs/api.md` at v0.40.11 `GET /api/tags`
(kind docs, tier A, status queued or mined per what you can ground, opened 2026-11-04, recheck
`on-release`, used-by the new knowledge entry); **S555** supersession row whose `teaches` opens
`supersedes S553 —` and names `### GET /models: List available models`, note 1, line 2227 as the anchor;
**S556** REJECTED row for llama.cpp `docs/preset.md` with reason and flip (no claim in this round parses
a preset; flip: a round that grades preset-inherited parameters on the fixture). Open every URL with
`curl` yourself; record status, bytes and sha256 in `curl.txt`.
2. `knowledge-unregistered-class-second-engine.md` — a `corpus/knowledge/` entry opening with
`source: S554`, `verified-at: 2026-11-04`, `recheck:`, then: what `/api/tags` is (an inventory of
locally available models), what the probe actually reads (`/v1/models`), why the `registered` class is
engine-agnostic (the class reads the registry's declared ports, not the engine's identity), and its
limit (an inventory is not a loaded-model or readiness claim). ≤60 lines.
3. `readme-row.md` — one coverage-map table row for `corpus/README.md`.
4. `quality-criterion.md` — one KQ row for `{LANE}/corpus/QUALITY.md` citing the round-80 lesson, whose
criterion is: a self-record fact is stated only in the form the receipt prints it; a claim whose own
cited receipt disagrees is unverified regardless of intent. Match the existing KQ row shape exactly
(read the last five rows of QUALITY.md first)."""),

    item("SR01ScoutPins", "scout", ["freshness"], f"""# SR01 — independent pin inventory (scout, read-only)
From live upstream data only (`git ls-remote --tags <repo>`; do not run the lane's `pin-watch.py`),
answer for the lane and for one sibling: (a) for `{LANE}/registry/engine-pins.tsv` pins — sglang
v0.5.22, vllm v0.32.0, llama.cpp b11755 — the newest release tag and how many release tags sort above
each; (b) whether `39febd2adb947b70da35e95f9351b3bf58ad170a` is any llama.cpp tag's peeled commit, and if
not, which release tags bracket it if that is derivable from the tag list alone (say plainly when the
tag list cannot bracket a commit); (c) whether kengaku's S178 pin `b7200` is a llama.cpp release tag and
its peeled commit; (d) read-only look at `{LANE}/corpus/SOURCES.md` rows S553/S554 and list every
llama.cpp ref the lane's registry and source rows name. Write `SR01.json` plus the raw `ls-remote`
outputs into your seat dir; no writes outside it."""),

    item("SR02ScoutOllama", "scout", ["coverage"], f"""# SR02 — Ollama v0.40.11 surface reconnaissance (scout, read-only)
Open, this round, with `curl` and record status/bytes/sha256: (a)
`https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md` — locate the `GET /api/tags`
section and the `GET /api/ps` section; quote ≤25 words for each with its heading and line number;
state precisely what `/api/tags` lists versus what `/api/ps` lists; (b) find whether the pinned release
documents an OpenAI-compatible `/v1/models` (search the same tree for `openai` docs paths at that tag;
report the exact path you opened, and say "not documented at this tag" if the fetch is 404 — do not
infer); (c) list the lane's existing Ollama instruments and pins
(`{LANE}/tools/kama-ollama-live.py`, `registry/ollama-live-pin.tsv`,
`{LANE}/corpus/knowledge/ollama-live-lifecycle.md`) and what each already holds, so the new census entry
does not duplicate them. Write `SR02.md` in your seat dir; never write under the lane."""),

    item("CN01Connector", "connector", ["adjacency"], f"""# CN01 — sibling-overlap scan (connector)
Read-only scan across `{LANE}` and the sibling lanes under `/home/vgpnk/Projects/shokunin/` (kengaku,
mado, tameshi, tsunagu, chousa, souji — whichever exist) for overlap with the round's three surfaces:
(1) the llama.cpp pin relation (kengaku's S178 b7200, any other lane pinning b11755/39febd2a/b7200);
(2) an Ollama `/api/tags` census class and any lane that already grades Ollama engine fixtures;
(3) engine-pin watch/relation registers. For each, name the exact file:line, whether it is duplicate
ground, contested ground, or complementary, and what the owning lane is. Then say which of the round's
three claims would be over-claimed if the sibling's ground were absorbed, and which are clean. Write
`CN01.md` in your seat dir. Never write outside it; never edit a sibling."""),

    item("RV01Review", "reviewer", ["calibration"], f"""# RV01 — adversarial review of the C1 counter's grading rules (reviewer)
`{LANE}/tools/round80-selfrecord-round79.py` is the round's C1 instrument. Poll for it (`sleep 30`, up
to 25 minutes). Then attack it with fixtures under your seat dir (`D=$(mktemp -d -p "$S")` git repos;
every git call names `-C "$D"`): can a forged correction pass (wrong `old`, `at` 41 hex, `at` an
ancestor but not the sealed revision, two blocks for one fact, `new` that does not re-derive at the
tip)? Can a fact be graded against the worktree instead of `git show <sealed>`? Can `corrected=` be
counted from prose rather than from blocks? Does the counter read the sealed revision's bytes for the
declared value and the tip's bytes for the observed value (the round-78 F2 defect)? Report each attack
as `CATCHES` / `MISSES` with the exact command and output, and name the missing selftest arm. Write
`RV01.md` in your seat dir; never edit the counter."""),

    item("CR01Critic", "critic", ["freshness"], f"""# CR01 — falsify the C2 pin-relation target (critic)
`{LANE}/tools/round80-engine-pin-relations.py` and `{LANE}/registry/engine-pin-relations.tsv` are the
round's C2 surfaces. Poll for them (up to 25 minutes). Then try to reach the target
`PIN_RELATIONS engines=3 refs=5 unexplained=0` without doing the claimed work: a register copied from
the base with no relation cells; a register whose rows name only `engine-pins.tsv` (missing b7200 and
the commit anchor); a register whose `newer`/`newest` values are stale against the committed tag lists
under `{WAVE}/measured/after/c2-tags/`; a register with a tag row for a tag that does not exist
upstream; a commit anchor that is actually a tag tip; a receipt path that does not exist. For each,
report the printed line and exit code and whether the counter caught it (`CATCHES`/`MISSES`). Also say
whether the offline `--tags-dir` path and the live path can disagree, and whether that disagreement is
graded. Write `CR01.md` in your seat dir; never edit the counter or the register."""),

    item("CR02Critic", "critic", ["operability"], f"""# CR02 — falsify the C3 second-engine target (critic)
`{LANE}/tools/round80-ollama-census.py` is the round's C3 instrument. Poll for it (up to 25 minutes).
Then attack: can the Ollama leg be satisfied by the llama.cpp fixture (same engine, different binary)?
Can a plain HTTP stub answering `{{"data":[…],"object":"list"}}` on a loopback port satisfy it (i.e. does
the counter prove an Ollama process, or only a model-API listener)? Can the two registry legs be made
to agree without the probe's class? Can `--audit` print `CLASS_ENGINES engines=2 verified=2 stale=0` with
one engine's receipt missing or with a receipt that carries `class_missing=1`? Report each as
`CATCHES`/`MISSES` with the exact command/output under your seat dir, and name the missing selftest arm.
Never edit the counter."""),

    item("MT01Mutation", "mutation-tester", ["calibration", "freshness", "operability"], f"""# MT01 — mutation-test the three round-80 instruments (mutation-tester)
Poll for `{LANE}/tools/round80-selfrecord-round79.py`, `tools/round80-engine-pin-relations.py` and
`tools/round80-ollama-census.py` (up to 25 minutes). For each, copy the module into your seat dir and
apply at least two named source mutations that should be caught by its own selftest or by a fixture it
does not cover (examples: C1 — a correction block accepted with `new` not re-derived, or `corrected`
counted from the prose; C2 — `newer` compared as strings, or a missing engine treated as covered;
C3 — the two registry legs sharing one registry, or `governed` counted without the class). Run each
mutated copy's `--selftest` and, where you built a fixture, the mutated module on it. Record, per
mutant: file, mutation, command, observed output, exit, `CAUGHT`/`SURVIVED`. A survivor is the finding
the L1 must fix or report. Write `MT01.json` in your seat dir; never edit the lane's modules."""),
]


def main():
    spec = {
        "wave": "w1",
        "milestone": "kama r80 w1",
        "reportDir": ".ufo/waves/round-80/w1",
        "maxLanes": 16,
        "axes": ["calibration", "freshness", "operability"],
        "context": CONTEXT,
        "items": ITEMS,
    }
    out = Path(__file__).with_name("w1-spec.json")
    out.write_text(json.dumps(spec, indent=1) + "\n")
    roles = {}
    for it in ITEMS:
        roles[it["role"]] = roles.get(it["role"], 0) + 1
    attack = roles.get("reviewer", 0) + roles.get("critic", 0) + roles.get("mutation-tester", 0)
    print(f"WROTE {out} seats={len(ITEMS)} roles={roles} attack={attack}/{len(ITEMS)}")


if __name__ == "__main__":
    main()
