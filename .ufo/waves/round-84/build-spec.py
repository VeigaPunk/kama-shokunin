#!/usr/bin/env python3
"""Build the round-84 w1 wave spec (12 seats, one v1 wave, band 8-16)."""
import json
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OUT = f"{LANE}/.ufo/waves/round-84/w1/out"
SCRATCH = "/fast/scratch/hyaku/kama-r84"
BASE = "aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0"
FREEZE = "2d49bf705a2f2f8b45da973407cbb0b2ce2f8fd2"
CONTROLS = "eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85"
SEALED = "ae4323171596126a9265f7f6c8af4164d499ba09"
GODSPEED = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.
"""

CONTEXT = f"""# Goal
kama lane, round 84: ONE v1 wave of 12 seats (build + attack) against the frozen claims in
{LANE}/plans/round-84-claims.md — read that file in full before your item and treat its
blockquote predicates, fact table, fixture spec and control receipts as frozen text.
Base revision {BASE} (round-83 non-author closure tip); freeze commit {FREEZE}
(plan + fixture + before receipts); controls commit {CONTROLS}. Sealed revision C2 grades {SEALED}
(the round-83 lane tip its report cites). Lane tip: `git -C {LANE} rev-parse master`.
# Contract (every seat)
- Write ONLY inside your own directory {OUT}/<YOUR-NAME>/ (create it). Never edit any other
  path in the lane checkout: the L1 is the single integration owner and lands every file.
- Seats NEVER commit, push, stash, or run any mutating git/jj command in
  {LANE} or the fleet repo /home/vgpnk/Projects/shokunin. For any test-run that needs a
  committed tree, work in your own scratch clone:
  S={SCRATCH}/<YOUR-NAME>; mkdir -p "$S" && git clone --shared {LANE} "$S/wt"
  and name every later git call `git -C "$S/wt" …`. Verify `git -C "$S/wt" rev-parse --show-toplevel`
  equals "$S/wt" before any local commit there; local commits in YOUR clone are fine.
- Scratch discipline: every clone/fixture/work dir lives under {SCRATCH}/<YOUR-NAME>/;
  remove it before you yield (`trap 'rm -rf -- "$S"' EXIT`); copy receipts into your out dir
  first. /tmp is for files under 50 MB only; committed tools must honor TMPDIR/--work and
  never hardcode /tmp. A /tmp path is never citable evidence.
- Every `Report:` trailer path is relative to {LANE} — write it at
  {LANE}/<that path> (inside your own out dir).
- Read-only seats (scout, reviewer, critic, connector, labrat, mutation-tester) return
  findings and files; they never make production edits anywhere.
- Tooling authorization (operator, 2026-10-19): you may install/upgrade tools that help the
  task; read /home/vgpnk/.omp/agent/RULES.md first (official channels; record
  tool/version/channel/reason in your report). pacman is PAUSED host-wide: never run any
  pacman transaction; install via uv tool / npx / an official binary in ~/.local/bin.
- Network: read-only GETs only, and only where your item names them (upstream document
  fetches, tag lists). No service, config, credential or systemd changes. No agent://all.
- You are a leaf: no delegation, no background swarm. (An executor may spawn one read-only
  labrat probe for a falsifiable hypothesis; nothing else spawns.)
- Report honestly: an unrun check has not passed; name every command you ran with its true
  exit code; never fabricate output.
"""

PRED_C1 = ("`python3 tools/pre-report-gate.py --repo . --round 84 --tip master` prints "
           "`PRE_REPORT round=84 arms=13 failed=0 uncommitted=0` and exits 0, and on the same tree "
           "`python3 tools/round81-append-debt.py --repo . --round 84` prints `bad_rows=0 unaccepted=0` exit 0 "
           "while `python3 tools/round81-append-debt.py --repo . --round 84 --late "
           ".ufo/waves/round-84/fixtures/late-wrong-subject.tsv` prints exactly one "
           "`APPEND_DEBT_FINDING note-wrong-deletion-round` line and exits 1.")
PRED_C2 = ("`python3 tools/round84-selfrecord-round83.py --repo .` prints "
           "`SELFRECORD_R83 claims=8 mismatches=0 corrected=6 unbacked=0`, exits 0, and `--selftest` prints "
           "`SELFRECORD_R83_SELFTEST pass=N fail=0` with N>=10, exit 0.")
PRED_C3 = ("`python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv "
           "--rows registry/pin-recheck-rows.tsv` prints `PIN_RECHECK rows=5 graded=5 ungraded=0 bad=0` and "
           "exits 0, with the held verdict mix whatever the committed bytes derive.")

def item(name, role, axes, title, body):
    return {"name": name, "role": role, "axes": axes, "milestone": "kama r84 w1",
            "prompt": GODSPEED + f"# {name} — {title}\n\n" + body}

items = [
item("EX01DebtBinding", "executor", ["operability"], "subject-round note binding in the debt counter (C1a)",
f"""Claim C1 predicate (frozen): {PRED_C1}
Your slice is C1 work item (a) only: the binding in the tool, not the registers, not the gate.

Deliver a byte-complete replacement for `{LANE}/tools/round81-append-debt.py` at
{OUT}/EX01DebtBinding/round81-append-debt.py, changing ONLY:
1. `grade()` gains a keyword parameter (e.g. `subject_rounds`) — a callable commit->int|None —
   and, in the late-rows loop after the `same-round` check, refuses a row whose note deletion
   round differs from the event commit's own subject round:
   class `note-wrong-deletion-round`, detail naming the note round and the subject round.
   A `None` subject (no `round-<N>:` prefix in the commit subject) leaves the row's grade
   unchanged — never an invented refusal. `continue` after a finding, like its sibling checks.
2. `main()` builds the callable from `git -C <repo> log -1 --format=%s <commit>` parsed with
   `^round-([0-9]+):`, cached per commit; pass it into `grade()`.
3. `selftest()` gains exactly two arms appended after the existing row-introduction arms:
   `note-subject-mismatch` (late row note `round-81 accepts round-78` over an event whose
   subject declares round 79 -> exit 1, class `note-wrong-deletion-round`) and
   `note-subject-unresolvable` (subject None -> row grades normally, exit 0). All 29 existing
   arms stay green and byte-identical in intent; print the new total.
Every git fact stays an injectable callable; the module stays pure. Run `--selftest` in your
scratch clone (the clone HEAD already contains the committed fixture
`.ufo/waves/round-84/fixtures/late-wrong-subject.tsv`): prove the new file grades that fixture
with exactly one `note-wrong-deletion-round` finding (exit 1) via
`python3 tools/round81-append-debt.py --repo . --round 84 --late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv`
run inside "$S/wt", and that the REAL register leg still prints the current summary there.
Save both receipts plus the pre-fix receipt
{LANE}/.ufo/waves/round-84/measured/before/red-debt-fixture.out (copy) into your out dir with
a README naming every command and exit code. Also run a diff of your file against HEAD's
`tools/round81-append-debt.py` and save it — the L1 verifies the delta touches nothing else.
"""),
item("EX02Registers", "executor", ["operability"], "stale-row rotation, disclosure, and the round-83 acceptance row (C1b/c)",
f"""Claim C1 predicate (frozen): {PRED_C1}
Your slice is C1 work items (b) and (c): the register data, not the tool, not the gate.
Work in your scratch clone; the audit there sees the committed history.

1. In "$S/wt", verify the current defect: `python3 tools/round81-append-debt.py --repo . --round 84`
   prints `events=76 … bad_rows=10` and ten `unknown-event` findings for late lines 105-114
   (event `0d7c7c3e…` `SCORECARD.md`); run `python3 tools/append-only-audit.py --repo . --json`
   and confirm that event's status is `restored` (its lines are held again at the tip), which is
   why it left the population. Save both outputs.
2. Build the rotation: `registry/append-only-late-r83-restored.tsv` = the late register's exact
   header line plus exactly those ten data rows byte-identical (history, disclosed, never
   re-graded); `registry/append-only-late.tsv` = header plus the remaining 113 data rows plus
   ONE new appended row accepting the round-83 event the audit holds:
   run the audit JSON, find the event with commit starting `96e28374` and file `SCORECARD.md`,
   and append `<commit>\tSCORECARD.md\t<line_sha256>\t<count>\t<class>\t<note>` where note is
   `round-84 accepts round-83 "round-83: reconcile the self-description (49 capabilities, round-82 closure pointer, round-84 plan), the R82 defect dispositions and the province note"; accepted round-83 record edit superseded by the round that followed`
   (the quoted text must equal that commit's actual subject — verify with
   `git -C "$S/wt" log -1 --format=%s 96e28374…` and paste both).
3. Disclosure: read `registry/append-only-disclosures.tsv`'s header, append one row recording
   the rotation (what moved, why: event restored at {BASE}, rows ungradeable history, R83V3),
   matching that file's column contract exactly.
4. Verify in "$S/wt" with the CURRENT (pre-binding) tool:
   `python3 tools/round81-append-debt.py --repo . --round 84` must print
   `bad_rows=0 unaccepted=0 pending=0` and exit 0 after your register changes (the new row's
   note deletion round equals the event subject round, so the C1 binding will also accept it —
   state that identity check explicitly). Also re-run
   `python3 tools/round77-append-registers.py --selftest` and
   `python3 tools/round78-append-registers.py --selftest` (must stay `fail=0`), and try their
   live modes if they accept --repo; report exit codes.
Deliver the three changed/new TSVs byte-exact under {OUT}/EX02Registers/, plus a receipts file
with every command and exit code, plus `git -C "$S/wt" diff` of the registry changes.
"""),
item("EX03GateArm13", "executor", ["operability"], "compose pre-report-gate arm 13 (C1d)",
f"""Claim C1 predicate (frozen): {PRED_C1}
Your slice is C1 work item (d): the gate, not the debt tool, not the registers.

Deliver a byte-complete replacement for `{LANE}/tools/pre-report-gate.py` at
{OUT}/EX03GateArm13/pre-report-gate.py, changing ONLY:
1. `ARM_ORDER` gains `"round83-instruments"` after `"round82-instruments"`.
2. New `ROUND83_MODULES` constant, mirroring `ROUND82_MODULES`:
   `(("round83-pending-falls.py", "PENDING_FALLS_SELFTEST"), ("round83-pin-rechecks.py", "PIN_RECHECK_SELFTEST"))`
   — selftests only, each required to end with its OWN summary prefix, fail-closed on a red,
   malformed or absent instrument (the arms 10-12 own-summary rule, reused verbatim).
3. The gate docstring and every selftest fixture expectation move from `arms=12` to `arms=13`
   (stub-arm red/green cases for arm 13 included, mirroring how arm 12's stubs are built).
Run the gate `--selftest` in your scratch clone and save the full output; every fixture arm
must pass with the new count. Also run the real gate in your clone
(`python3 tools/pre-report-gate.py --repo . --round 84 --tip master`) and save it — it must
still fail at the clone state (arm 13 red: `PENDING_FALLS_SELFTEST`/`PIN_RECHECK_SELFTEST` are
green at HEAD, so arm 13 goes green only after the L1 lands the round; the debt arm stays red)
— report exactly which arms fail and why. Save `git -C "$S/wt" diff` of the file.
"""),
item("EX04Selfrecord", "executor", ["calibration"], "round84 selfrecord counter for the round-83 record (C2)",
f"""Claim C2 predicate (frozen): {PRED_C2}
Read the full fact table F1-F8 in {LANE}/plans/round-84-claims.md §C2 — it is frozen: population
8 facts, exactly 6 corrected (F1, F2, F3, F4, F5, F8) and 2 holds (F6, F7). Mirror the
architecture of `{LANE}/tools/round83-selfrecord-round82.py` (read it first): declared facts
read at the sealed revision via `git show`; receipt witnesses read at the graded tip
(`git show HEAD:<path>` — never the worktree); corrections parsed from
`corpus/lessons/round-84.md` with the same CORRECTION regex
(`corrected F<n> old=<tok> new=<tok> at=<rev> date=<iso> fix=<path>`), one dated correction per
stale fact, the fix leg binding the whole new token in the fix path's TIP bytes outside
`LOG-CORRECTION` lines and `#### round-<N> correction` blocks; holds cannot be corrected; a
correction on a hold or an unknown fact is unbacked. SEALED = {SEALED}. Exit 0 answered;
1 mismatches/unbacked; 2 unreadable evidence. Print per-fact `SELFRECORD_R83_FACT F<n>
<holds|corrected|stale> declared=… witness=…` lines and the summary line.
Selftest (target N>=10): fixture-repo attacks mirroring round-83's — missing lesson, correction
with wrong old token, correction on a hold, unbacked fix token (token only inside a
`#### round-84 correction` block), sealed-revision drift, and a clean green fixture. Build
fixtures in your scratch dir only (--work/TMPDIR; nothing under /tmp over 50 MB).
Red receipt: run `python3 tools/round84-selfrecord-round83.py --repo .` in your scratch clone
(lesson absent at HEAD) and save it: expect `mismatches=6 corrected=0 unbacked=6`, exit 1.
Deliver the tool at {OUT}/EX04Selfrecord/round84-selfrecord-round83.py plus the red receipt,
selftest output and a README naming every command and exit code.
"""),
item("EX05PinRecheck", "executor", ["freshness"], "grade every pin relation including the formerly ungraded one (C3)",
f"""Claim C3 predicate (frozen): {PRED_C3}
Read {LANE}/plans/round-84-claims.md §C3 and the anchor-extract format in the docstring of
{LANE}/tools/round83-pin-rechecks.py (header `# url=<https-url> sha256=<64hex> ref=<ref> lines=<a>-<b>`;
digest over bytes after the header; quote at upstream line L sits on body line L-a+1).

1. Open this round, by `curl -sS`, recording status, sha256, byte count for each:
   a. the llama.cpp server README at ref `b7200` — resolve the era-correct path first
      (try `tools/server/README.md`, then `examples/server/README.md`):
      `https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/<path>`. Pick a
      health-endpoint statement as the pin quote; record its upstream line.
   b. fresh reads at the current newest refs: `…/ggml-org/llama.cpp/b12111/tools/server/README.md`,
      `…/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx`,
      `…/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` — compare sha256 with the
      committed extracts under {LANE}/corpus/anchors/ (llamacpp-b12111-health.txt,
      sglang-v0.5.23-health.txt, vllm-v0.33.0-prefix-caching.txt): byte-identical or drifted,
      per document. Also run `git ls-remote --tags` against the three upstream repos and
      `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` in your scratch clone;
      if any newest tag moved past b12111 / v0.5.23 / v0.33.0, STOP that row and report —
      do not invent extracts for refs you did not fetch.
2. Build new anchor extracts under {OUT}/EX05PinRecheck/anchors/: `llamacpp-b7200-<slug>.txt`
   (new ground), plus fresh newest-side extracts only where bytes drifted. Header sha256 must
   equal the digest of the body you received.
3. Produce an updated `registry/pin-recheck-rows.tsv` (deliver byte-exact): relation 3's row
   becomes graded — fill ref `b7200`, newest `b12111`, verdict the bytes derive (pin quote
   occurs verbatim in the newest extract -> holds; absent with non-empty different newest
   quote -> your honest one-word judgment among reworded/moved/drifted), quote_pin + line,
   quote_newest + line, extract paths, note naming the b7200 URL and sha256 short form. Rows
   1/2/4/5: keep `holds` + note appended `; re-read 2026-11-04 byte-identical sha256 <16hex>`
   where the fresh read matched; if a row drifted, grade it honestly (the vocabulary's
   reworded/moved/drifted) and say so — a drifted verdict does NOT fail the claim, only
   byte-inconsistency does. Every quote stays <=25 words (quote-too-long is a bad row).
4. Verify in your scratch clone: copy the updated rows + extracts into the clone paths, run
   `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv
   --rows registry/pin-recheck-rows.tsv` and save the output: target
   `PIN_RECHECK rows=5 graded=5 ungraded=0 bad=0` exit 0. Also save its `--selftest` (fail=0).
Deliver the TSV, the extracts, all curl receipts (url, status, sha256, bytes), the run outputs
and a README with every command and exit code.
"""),
item("SCR01LessonSources", "scribe", ["calibration", "coverage"], "round-84 lesson, SOURCES append block, knowledge and record corrections (frontier)",
f"""You draft prose; the L1 integrates and lands. Read {LANE}/plans/round-84-claims.md in full
(its fact table F1-F8, Mistakes directive and frontier list are frozen) plus
{LANE}/corpus/lessons/round-83.md (the format to mirror: ## Gate table, ## Corrections code
block, ## Mistakes table with class · evidence pointer · captured-by · fix) and
{LANE}/corpus/SOURCES.md (contract v1 shape; latest row id S571 — your rows start at S572).
Deliver under {OUT}/SCR01/:
1. `round-84-lesson.md` — full draft of `corpus/lessons/round-84.md`: a `## Gate` section whose
   table carries one row per new source (S572 llama.cpp README at b7200; S573-S575 the three
   fresh newest-side reads), each with URL, status 200, byte count, the located line, and a
   <=25-word verbatim quote you verified by fetching that URL yourself this round with curl
   (paste the sha256 you received); a `## Corrections` code block with the eight correction
   lines EXACTLY in the round-83 format, one per fact: e.g.
   `corrected F1 old=r83c1-late=23 new=r83c1-late=22 at={BASE} date=2026-11-04 fix=SCORECARD.md`
   — old/new tokens MUST match the plan's fact-table tokens character-for-character
   (F1 r83c1-late=23->22; F2 r83c1-window=8->7 and r83c1-falls=yes->no as TWO tokens inside
   F2's single correction line, matching how the round-83 block packed one line per fact;
   F3 r83c1-delta=123/103/20/0->113/103/10/10; F4 r82c2-new=0->15; F5 r83c3-selftest=11->14;
   F6 hold, no correction line; F7 hold, no correction line; F8 r83-closure=round-82-verifier-spotcheck.md->round-83-verifier-spotcheck.md);
   a `## Mistakes` table with the round-83 live-cells mistake (class `number-drift`/`survivor`;
   evidence: the round-83 authority paragraph and axis rows carrying interim receipts while the
   final receipts superseded them, pointers {LANE}/.ufo/waves/round-83/measured/final/*.out vs
   SCORECARD.md head; captured-by KQ27; fix: C2's six corrections plus a new KQ criterion row —
   draft that KQ row for {LANE}/corpus/QUALITY.md too: current-evidence cells in SCORECARD head
   sections must cite the terminal receipt revision and the re-derivation command, supersession
   names the old criterion); a `## Frontier` paragraph; a `Stale-lane` note placeholder;
   an `Assimilation: none` line placeholder (the scout's fit verdict may flip it — draft both).
2. `sources-append.md` — the four SOURCES rows as an append block, 11 columns each, no `|`
   inside any cell, tier A, status mined, opened 2026-11-04, recheck per contract (ISO/cadence),
   used-by naming `corpus/lessons/round-84.md` (and
   `corpus/knowledge/runtime-health-surface-matrix.md` for the sglang row); anchors carry
   revision + line; teaches one grounded learner benefit; verify with
   `awk -F'|' '/^[[:space:]]*\\|[[:space:]]*S[0-9]/ && NF!=13 {{n++}} END{{print n+0}}'` over your
   block = 0.
3. `matrix-addition.md` — the appended dated section for
   `corpus/knowledge/runtime-health-surface-matrix.md`: SGLang `/ready` (200 ready / 503
   starting-paused-unhealthy-shutting-down) and `/ping` routes at v0.5.23 (native_api.mdx lines
   111-112), citing the new S-row, provenance trio style, explicitly documentary (no endpoint
   sampled). Verify the two lines yourself by fetching the v0.5.23 mdx.
4. `register-row-introduction-correction.md` — an appended dated correction paragraph for
   `{LANE}/corpus/knowledge/register-row-introduction.md` (R83V4): lines 10/34 mean
   last-modification attribution per git-blame, not immutable first introduction; the disclosed
   cosmetic-edit limitation stays; nothing above is edited.
5. `coverage-rows.md` — the exact coverage-table row(s) to append to
   `{LANE}/corpus/README.md`'s coverage map for the round-83 entries `pin-recheck-rows` and
   `register-row-introduction` (R83V5: real table rows, appended at the section's end, no
   mid-file insertion), plus the frontier-row updates.
"""),
item("SCO01Upstream", "scout", ["freshness"], "live upstream recon + assimilation fit verdict",
f"""Recon only; return findings, never edits. Work under {SCRATCH}/SCO01Upstream/.
1. Right now, per engine: `git ls-remote --tags` newest tag for
   github.com/ggml-org/llama.cpp (b*-style), sgl-project/sglang (v*-style), vllm-project/vllm.
   Compare with pin-watch's current read (llama.cpp newest b12111, sglang v0.5.23, vllm v0.33.0):
   moved or unchanged, per engine, with the exact tag names.
2. Fetch `https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md`
   and, if 404, `…/examples/server/README.md` (and report any path that works): status, sha256,
   byte count, the health-endpoint section's exact line numbers and a <=25-word verbatim quote.
   The round-83 relation row calls b7200 `behind 3395` releases.
3. Skim the two v0.5.23 routes SGLang documents in native_api.mdx around lines 108-115 and
   quote the `/ready` and `/ping` lines exactly (for the matrix addition).
4. Read /home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md and the newest file in
   {LANE}/considerthese/ (2026-10-26.md): one paragraph each — does any staged theme or
   still-unimplemented proposal fit THIS round's frozen claims as ordinary curation (it may
   only ride an existing claim, never widen one), or is `Assimilation: none` honest this round?
   Name the specific proposal/theme and the claim it would ride, or state none.
5. Record every command with its true exit code; save fetched bodies under your scratch and
   their sha256s in your report. Do not fetch anything else.
"""),
item("CON01Siblings", "connector", ["adjacency"], "sibling-overlap scan for the round's surfaces",
f"""Cross-axis pattern scan; return findings, never edits. Write {OUT}/CON01Siblings/overlap.md.
The round's surfaces: (1) upstream release/tag watch for the three pinned serving engines and
document rechecks (registry/engine-pin-relations.tsv, registry/pin-recheck-rows.tsv); (2)
append-only acceptance registers and their grade counters (registry/append-only-*.tsv);
(3) self-record fact grading instruments (tools/round8*-selfrecord-*.py); (4) the pre-report
gate arm composition (tools/pre-report-gate.py); (5) fetching the llama.cpp README at the
kengaku-named ref b7200 (relation 3's role cell names `cross-lane kengaku S178`).
Read {LANE}/corpus/knowledge/cross-lane-scope.md, the PROVINCE.md files of kengaku, chousa,
kumitate, tameshi, mori (…/-shokunin/ under /home/vgpnk/Projects/shokunin/), and the round-83
closure {LANE}/corpus/lessons/round-83-verifier-spotcheck.md routed defects. For each surface:
which sibling could claim it, why kama holds it (its own pins/registers/instruments), and any
contested or reportable scope — especially whether reading a document at a ref that appears in
a cross-lane relation row absorbs kengaku ground or stays kama's serving-document surface.
One ownership table + named risks. Cite file:line for every claim about a sibling.
"""),
item("RV01Claims", "reviewer", ["operability", "calibration"], "attack the three frozen claims and their counters",
f"""Attack, never edit production files; findings under {OUT}/RV01Claims/RV01.md.
Read {LANE}/plans/round-84-claims.md in full. For each claim:
1. Re-run every counting command over COMMITTED bytes in your scratch clone (clone --shared;
   work at HEAD which already contains the freeze {FREEZE} and controls {CONTROLS}):
   the three do-nothing controls
   (.ufo/waves/round-84/measured/before/ctl-gate.out, ctl-selfrecord.out, ctl-pinrecheck.out)
   and both red receipts (red-debt-fixture.out, red-debt-real.out) — confirm each receipt's
   `# cmd:` re-run reproduces its printed summary and EXIT line, and that each control FAILS
   its claim's target.
2. Predicate identity: the plan's predicate sentence, the tools' output formats and the
   receipt labels must be the same words; flag any drift (e.g. the fixture leg's
   `note-wrong-deletion-round` vs the tool's actual class string; `arms=13`; the selfrecord
   summary token order).
3. C2 fact table: for each of F1-F8 verify at the SEALED revision {SEALED} that the declared
   value is really there (`git show {SEALED}:SCORECARD.md`, the named line/section) and at HEAD
   that each witness receipt prints the witness value; flag any fact that does not re-derive.
4. C1 fixture: is one mutated note enough? Check the fixture
   (.ufo/waves/round-84/fixtures/late-wrong-subject.tsv) — exactly one note differs from the
   register's corresponding row, ten stale rows removed, header intact; the mis-noted row's
   event commit subject really declares round 79; nothing else in the fixture could trip the
   new class.
5. Delta purity: when the L1 lands the fixes, the only byte deltas for C1 must be the tool +
   registers; name what you will check. Report every command with its exit code.
"""),
item("CR01Controls", "critic", ["calibration"], "falsify: cheapest cheats against the frozen counters",
f"""Falsify the claims the others assert; findings under {OUT}/CR01Controls/CR01.md.
Read {LANE}/plans/round-84-claims.md. For each claim, build the cheapest cheat that meets the
frozen counter WITHOUT the claimed work, and score it:
- C1: can the gate print `arms=13 failed=0` without the subject-round binding (arm 13 added,
  registers rotated, but grade() untouched)? The fixture leg must then print zero
  note-wrong-deletion-round findings while exit 1 — does the predicate's conjunction
  (exactly one such finding) actually block this cheat? Verify by reasoning over the current
  tool's grade() loop at HEAD and by a scratch experiment if cheap (a hand-edited copy of the
  tool in YOUR scratch clone is allowed; never the lane tree).
- C2: game the fix leg — correction lines placed inside a `#### round-84 correction` block, or
  tokens split across lines, or the lesson carrying the witness values without correction
  blocks. Which of these does the round-83 regex design already reject, and which could slip?
  Name any gap as a finding for the L1's instrument spec.
- C3: fabricated ground — an extract whose header sha256 matches bytes the seat never fetched;
  an ungraded row hidden by hiding the relation row. Which committed checks (anchor sha256
  recompute, ungraded-documented-ref, missing-row) catch each, and which slip?
- Controls: confirm each committed control receipt genuinely fails its target (re-run them in
  your scratch clone). A control that would pass unchanged with no work invalidates its claim —
  say so loudly if found.
Report each cheat: attempt, observed result, verdict (blocked/escaped), command + exit code.
"""),
item("MT01Binding", "mutation-tester", ["operability"], "kill the subject-round binding's mutants",
f"""Mutation-run the NEW binding; findings under {OUT}/MT01Binding/mutations.md.
Wait for nothing: build your own mutants from HEAD's {LANE}/tools/round81-append-debt.py in
your scratch clone copy. After EX01's replacement lands you cannot see it — so mutate the
SPEC: first apply the delivered replacement if it already exists at
{OUT}/EX01DebtBinding/round81-append-debt.py (poll once mid-run; if absent, mutate a
hand-written minimal implementation of the spec in your scratch and say so).
Required mutants (each a minimal source edit on a copy):
M1 delete the subject-round check entirely; M2 compare the deletion round against the
ACCEPTING round instead of the subject round; M3 off-by-one (`deletion != subject` ->
`deletion < subject`); M4 drop the `continue` after the finding (double-count); M5 treat a
None subject as a mismatch (invented refusal). For each mutant run, in your scratch clone:
`python3 <mutant> --selftest` (the `note-subject-mismatch` arm must go red) and
`python3 <mutant> --repo . --round 84 --late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv`
(the finding must vanish or change). killed = the owning selftest arm goes red; escaped =
survivor with its reason. Report killed/escaped per mutant with the exact failure lines.
Copy each mutant file into your out dir. Remove your scratch tree before yielding.
"""),
item("CR02Probes", "critic", ["operability", "calibration"], "run the committed do-nothing controls and one vocabulary probe",
f"""Cheap probes only; findings under {OUT}/CR02Probes/probes.md. Never edit production
files. In your scratch clone (clone --shared; HEAD contains the controls):
1. Re-run the three control commands from the receipts
   (.ufo/waves/round-84/measured/before/ctl-gate.out, ctl-selfrecord.out, ctl-pinrecheck.out)
   and paste each output + exit; each must FAIL its claim target (gate != arms=13 failed=0;
   selfrecord file absent exit 2; pin-recheck ungraded=1).
2. Vocabulary probe on the CURRENT tool: build a two-row scratch fixture (in your scratch
   clone, committed locally there) where a late row's note deletion round is GREATER than the
   event commit's subject round (e.g. subject round-79, note `round-81 accepts round-85`):
   does the current tool accept it (bad_rows=0)? This probes whether the round-84 binding
   needs an inequality direction too, not just equality. Report the exact summary lines.
3. Time-box: if any probe exceeds ten minutes, stop it and report the partial result honestly.
"""),
]

spec = {"wave": "w1", "milestone": "kama r84 w1", "reportDir": ".ufo/waves/round-84/w1",
        "maxLanes": 16, "context": CONTEXT, "items": items}
Path(__file__).with_name("w1-spec.json").write_text(json.dumps(spec, indent=1))
print("items:", len(items))
roles = [i["role"] for i in items]
print("roles:", {r: roles.count(r) for r in set(roles)})
attack = roles.count("reviewer") + roles.count("critic") + roles.count("mutation-tester") + roles.count("labrat")
print(f"attack share: {attack}/{len(items)}")
