# SB02QualityDraft - round 64 wave b, kama - QUALITY criteria draft (mistake mining)

Seat: SB02QualityDraft (scribe-type draft item; leaf, no dispatch). Axis judged: calibration.
Milestone: draft QUALITY criteria. Drafts only: no edit to `corpus/QUALITY.md`, `corpus/lessons/`, `SCORECARD.md`, `tools/` or any lane file; no commit; the L1 integrates.
Freeze read first: `.ufo/waves/round-64/controls/freeze.txt` (base `0c1eff3c`, freeze commit `f6a4ea9a`). The base and the freeze commit differ only in `corpus/SOURCES.md`, `tools/kama-completion-live.py`, `tools/round64-c1-counter.py` and round-64 control/source files (`git diff --stat 0c1eff3 f6a4ea9`): `SCORECARD.md`, `tools/round42-selfdesc-reconcile.py` and `corpus/QUALITY.md` are byte-identical across both, so the reconciler and pointer observations below hold at the freeze commit too.

## Result

Drafts are in `.ufo/waves/round-64/b/out/SB02QualityDraft/`:
- `QUALITY-KQ107-KQ111.md` - five proposed rows (KQ107–KQ111) in the existing four-column format, under a round-64 heading.
- `lesson-round-64-mistakes.md` - three proposed `## Mistakes` rows (class | evidence | captured-by | fix) for `corpus/lessons/round-64.md`, plus three drafter notes.
- `receipts/` - reconciler outputs from a scratch clone, with `commands.txt` giving the exact invocations.

The mined class is a counter that binds the wrong object, plus a calibration cell left stale because the reconciler had no conjunct for it. Each draft row names its evidence path.

## Findings the drafts rest on (each re-read or re-run by this seat)

F1 - **calibration cell stale, and the reconciler cannot see it.** `SCORECARD.md:18` (calibration row) reads "latest outside closure `corpus/lessons/round-57-verifier-spotcheck.md` (rejected-honest-stop), including round 57". The newest closure on the tree is `corpus/lessons/round-63-verifier-spotcheck.md` (closures 56–63 exist; `ls corpus/lessons/round-*-verifier-spotcheck.md`). Scratch clone at `0c1eff3c`, `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip HEAD` prints `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=63 met=True` (`receipts/reconcile-base.out`).

F2 - **the reconciler is blind to a stale-but-existing pointer.** Planted fixtures (single occurrence replaced in `SCORECARD.md`, committed in the clone, reconciler run at that commit):
- round-58 (exists, stale): `mismatches=0 met=True` (`receipts/reconcile-planted-r58.out`);
- round-63 (correct): `mismatches=0 met=True` (`receipts/reconcile-planted-r63.out`);
- round-99 (absent): `r41=1 ... mismatches=1 met=False`, detail `r41 calibration dead path corpus/lessons/round-99-verifier-spotcheck.md` (`receipts/reconcile-planted-r99.out`).
So the only thing the reconciler catches is a dead path, and only through the imported r41 counter. `tools/round42-selfdesc-reconcile.py` checks the calibration row's `rel` needle (`verifier-spotcheck`) and nothing about the pointer's value. This is the mined defect: the r63 verifier's routed item 2 ("make the reconciler fail on it") has no conjunct to satisfy it.

F3 - **the pointer claim lives in counters outside the closure chain.** `tools/round58-c2-counter.py:33-34` and `tools/round59-c2-counter.py:14` carry the "latest outside closure" regex. `tools/round63-c2-counter.py` has no `spotcheck`, `closure` or `pointer` reference (`grep -n -i` empty), and the round-63 C2 counter runs `tools/round42-selfdesc-reconcile.py` as its only self-description check (`round63-c2-counter.py:471`). So the round-63 C2 "reconciled" claim could pass with the stale cell present, which is what the r63 verifier recorded (`corpus/lessons/round-63-verifier-spotcheck.md` §2 "New observation").

F4 - **C2 (r63) certified tip-tree tools by running them.** KR03DoNothing S1 (`round42-selfdesc-reconcile.py:269` `mism = sum(c.values())` → `mism = 0`) and S2 (SCORECARD head-only edit) print `met=True` (`.ufo/waves/round-63/w1/KR03DoNothing.md` lines 15–16, 42–43). MT21C2SelfdescSkip mutant A (drop the `selfdesc == 0` conjunct) and mutant B (reconciler nonzero exit read as 0) both print `met=True` (`.ufo/waves/round-63/w1/MT21C2SelfdescSkip.md` lines 13–14). The r63 counter takes the reconciler's count from stdout with no pin and no planted regression.

F5 - **C2 (r63) binds a reused work tree.** `checkout_tip` returns any existing `work/tip` regardless of revision (`tools/round63-c2-counter.py:479-483`; RV03C2CounterCode F1). A second run on the same `--work` with another tip executes the first tip's tools. Not reproduced by this seat (no run needed for a draft row; the row's Check asks for the two-run test).

F6 - **C2 (r63) host-busy pid binding.** `tools/round63-c2-counter.py:336-337, 352, 364` accept `host-busy` when pgrep is non-empty before and after, with disjoint pid sets (RV03 F2, quoted there with `before=[111] after=[222]` accepted). Drafted as KQ108.

F7 - **C1 (r63) binds the socket and a helper from the tree under judgment.** `tools/round63-c1-counter.py:358` (`listener_owned` from `live_mod.port_owned_by`), `:365-368` (`load_live_mod` loads `kama-llamacpp-live.py` from the tool's directory), `:656-661` (copies the tip blob of that helper into the scratch tree). Forgeries A and B pass (`.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out`, `sleeper.out`, both `met=True` 44/44). MT15 recorded the helper-provenance point as [INFERENCE] and did not test it; this seat did not test it either, it reads the code only.

F8 - **the round-64 C1 counter at `f6a4ea9` (for L1's KQ107 check).** `tools/round64-c1-counter.py` makes no call to `port_owned_by` or to any function of the staged helper in its decisions (`git show f6a4ea9:tools/round64-c1-counter.py | grep -n "port_owned_by\|hold_for_witness\|live_mod\."` is empty; the only `live_mod`-prefixed matches are the string `live_model`). `listener_holders_pinned` is computed from the counter's own `collect()` and `/proc` reads. It does stage the tip's `kama-llamacpp-live.py` into the scratch tree at `:1429-1432` for the tool under test, and the tool imports that helper (`tools/kama-completion-live.py:71, 352, 598`). That is the correct direction for C1 (the tool is the thing judged), but it is the reason KQ107 asks for a planted-helper check rather than a reading: a helper that lies is only harmless if no decision reads it. Shown by reading, not by a run.

F9 - **corrections to the freeze's own wording (drafter's notes).** The freeze says the stale pointer was "five closures stale". Closures newer than round 57 at base are 58, 59, 60, 61, 62 and 63: six. The freeze's "five" appears to count before the round-63 closure landed; the drafted Mistakes row says "closures exist through round 63" to avoid the miscount. The verifier's "reconciler reports 0" is consistent with base (`mismatches=0`); RV04/KR03 saw `mismatches=8` at amendment tip `03a6a1d`, a different tip.

## Draft rows (summary; full text in out dir)

| ID | Mined class | Lesson evidence | Proposed captured-by |
|---|---|---|---|
| KQ107 | helper loaded from the tree under judgment | F7, F8; MT15 helper-provenance note | planted-helper check (wave f) |
| KQ108 | host-busy outcome bound to disjoint or non-refusal pids | F6; RV03 F2 | stubbed-pgrep row score |
| KQ109 | tip-tree tool or reconciler run and credited without pin, regression, or exit read | F4; KR03 S1/S2; MT21 A/B | one-line mutant commits must print `met=False` |
| KQ110 | calibration pointer unchecked against a stale-but-existing target | F1, F2, F3 | planted round-58 pointer must print `met=False` |
| KQ111 | reused `--work` executes an earlier tip's tools | F5; RV03 F1 | two-run `work-reused` exit 2 |

Lesson Mistakes rows drafted: `attribution` (r63 C1 socket/process; captured-by: none at r63, candidates KQ106/KQ107 and round-64 `listener_holders_pinned`), `calibration` (stale pointer; captured-by: none at r63; candidate KQ110), `vacuous` (r63 C2 tip-tree certification; captured-by: none at r63; candidates KQ109/KQ111 and the round-64 C2 counter, not yet built).

## What this seat did not do

- Did not run the round-64 C1 counter, the forgery patches, or any live server; not in this item's scope and the wave-b C1 attackers do that.
- Did not build or score the round-64 C2 counter, the reconciler conjunct, or the tally reader. The drafted KQ109–KQ111 Checks describe the tests; they are not shown able to fail. Nothing here is a claim that any criterion is admitted.
- Did not edit `SCORECARD.md:18`. The stale cell is a finding for the L1 to repoint at the round-64 closure; the drafts do not repair it.
- Did not write `corpus/lessons/round-64.md` or `corpus/QUALITY.md`; the rows are drafts for the L1.
- Did not read `/home/vgpnk/Projects/shokuknow`; no fleet-root tracked file written.

## Procedure and provenance

- Clone: `S=/fast/scratch/hyaku/kama-r64/b/SB02QualityDraft`, `D=$S/clone` via `git clone -q --shared`; `git rev-parse --show-toplevel` asserted equal to `$D`; checked out `0c1eff3c` (the do-nothing base, where the reconciler behaviour is measured). Every commit made in the clone used the seat identity (`seat <seat@seat.invalid>`), the clone was reset to `0c1eff3c` after each fixture, and the scratch root is removed before yield after the receipts were copied.
- Reconciler runs are read-only on the repo (`cat-file` at the tip); the planted fixtures are committed only in the clone.
- Wall time: 25 s base run, 19 s and 33 s for the fixture runs (per the command output).
- Tools installed or upgraded: none (no install, no upgrade, no `~/.local/bin` write).
- Mutating git: only inside the scratch clone (`commit`, `checkout`). No command against `/home/vgpnk/Projects/shokunin/kama-shokunin` mutated anything; read-only `git show`, `git diff --stat`, `git rev-parse` and `git cat-file` were used there.
- Ports: no live servers started; no listener touched.

## Limits (stated, not verdicts)

- The planted-pointer fixtures prove the reconciler's current verdict on a stale pointer; they do not prove a repaired reconciler is correct. KQ110's Check is the repaired reconciler against the same fixtures.
- F8 is a reading of code at `f6a4ea9`, not a run.
- The draft rows are not admitted; the L1 decides under the QUALITY admission rules. No outside spot-check exists for these drafts; the round-63 outside spot-check was pending in its own closure.

Receipts cited: `.ufo/waves/round-64/b/out/SB02QualityDraft/receipts/` (`reconcile-base.out`, `reconcile-planted-r58.out`, `reconcile-planted-r63.out`, `reconcile-planted-r99.out`, `commands.txt`).

Tally line (reconciler, base tip, the one counter output this item produced): `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=63 met=True` at `tip=0c1eff3cb9ac4c11402ab0124c35842f06a436fc`; planted round-58 pointer: `mismatches=0 met=True`.
