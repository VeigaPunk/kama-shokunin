author: hyaku closure (non-author integrator, @m_opus)

# Round 19 — verifier spot-check (non-author closure, hyaku)

Date: 2026-10-21. Closure prompt: fleet `.ufo/prompts/closure/kama-round-19.md`.
Lane HEAD before `8bf99cae7de2517fd4ebe209f3b940aeabb6b687`, after
`3389513f5107d5d77213cafa35ff2cbc18845100`. This reviewer authored no kama work
and dispatched no kama seat. The author agent (KamaR18Recovery) also authored
round 18; its 64 build seats are author-side. Three read-only re-check seats were
refused by the host job cap ("Background job limit reached (100)"); every
re-check below was run by this reviewer alone.

Driver digest (copied from mutable `.ufo/watchdog.log`):

```text
2026-10-21T03:01:06-03:00 launch kama round=19 pgid=1538680 driver=hyaku-inline attempt=1
2026-10-21T03:59:14-03:00 complete kama round=19; hyaku-inline attempt=1
```

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report landed by lane | `git log --format='%an %H %cI' -- .ufo/reports/round-19/kama.md` (fleet) | `kama-shokunin ac9859f4e747… 03:47:37` | pass |
| Report not filed before its commits | `git log` in lane | newest cited commit `24adc8e` at 03:47:20 | pass |
| `SHONEN` heading, one line per box | read report §SHONEN | 4 lines, all `[~]` with pointers | pass |
| Cited commits exist, ancestors of branch | `git rev-parse --verify <h>^{commit}`; `git merge-base --is-ancestor <h> refs/heads/master` for 7229fa95, 5b108c1a, 84cf2f76, f1790e25, 028235e6, 05f0f6c7, 30ed3783, 24adc8ed | all resolve uniquely, exit 0 | pass |
| Pushed, nothing uncommitted | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain` | `local=remote=3389513f… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty | pass |
| Prompt carries template contract | `diff templates/round-prompt.md .ufo/prompts/kama-round-19.md` | 11 template lines differ, all placeholder fills; §1–§5 present, §6 hyaku addendum appended | pass |
| Marker? | — | real report naming checkable pushed commits | not a marker → `ok` |

Post-report commits `8d9191f`, `60e8fd8`, `464ea5a`, `3389513` add only late
build-wave advice files (`git diff --stat 24adc8e 3389513`: 6 advice files).
Conformance defects (status-neutral, routed below):

- New instruments are unregistered. `git grep -E
  'citation-provenance|install-tree-grid|expect-install-tree' 3389513f -- SKILL.md`
  returns nothing, and SKILL.md is unchanged this round. Gate standard
  §Delivery grades no gate conformant until its registry row exists.
- The round-19 census receipts are uncommitted. The report cites
  `sources/census-before.txt` and `census-after.txt`. In the tree, those names
  exist only under `.ufo/waves/round-18/sources/`, which reads `rows 56`.

## Routed round-18 defects (from `round-18-verifier-spotcheck.md` §Routed)

| # | Defect | Re-check | Result |
|---|---|---|---|
| 1 | residual verdicts 4 confirm / 3 partial | `git grep -n '^VERDICT' 3389513f -- .ufo/waves/round-18/residual/advice/` → confirm: Privacy, Health, ImplPin, CounterC2; partial: Claims, Corpus, CounterC1 | fixed by appended erratum (`round-18.md` §Erratum, `LOG.md` round-19 erratum) |
| 2 | S055 / Gate-row pointers vs bytes | `commands.json`: absent at `c6dc46f`; sha `ce7dc79c…` at `1c325b2` and `101f3991`. `live-gate-1.stdout` names `live/receipt-1` at `1c325b2`/`101f3991` (sha `b2043ba8…`) and `live-recovery/receipt-1` at `1b85a24`/tip (sha `1cb5a41b…`) | fixed. S055 qualification is appended below the SOURCES table, and the erratum and `cite()` tokens match these bytes |
| 3 | SCORECARD.md:755 `--out` vs `--json` | line 755 still reads `--json --out PATH`; erratum appended after it naming `survivors.py --json` and the stdout document | fixed (append-only, original kept) |
| 4 | residual seat-split record | `.ufo/waves/round-18/residual/assignments.json`: 7 seats, 6 reviewer + 1 critic, verdicts 4/3 match the advice files | recorded, but committed in round 19 (`7229fa9`) with no provenance field. It is a retrospective record, not the original dispatch |

One more finding. `git diff 8bf99cae 3389513f -- corpus/lessons/round-18.md`
shows an in-place rewrite of the round-18 Gate reject row at line 42 (commit
`30ed378`, "279 wording"). The original row text was replaced instead of
corrected by appendix. The decision is unchanged and only the reason wording
changed, but PROTOCOL §Evidence standard says such a correction is appended,
never rewritten. This is routed below.

## Per-claim re-check

**C1 calibration 7 → 7 (declared 7 → 8, then refuted and held).** I re-measured
with git and sha256sum only; `tools/citation-provenance.py` was not executed.
For each `registry/required-citations.json` row at the tip:

```text
row                   blob sha at rev   rev ancestor of master   exact cite() token in doc@tip   token in doc@8bf99cae
s055-commands         match             yes                      1                               0
gate-live-1           match             yes                      1                               0
c2-official-stdout    match             yes                      1                               0
gate-live-checkpoint  match             yes                      1                               0
```

The result is 0/4 → 4/4 verified. This matches `evidence/c1-counting.txt`
(`required=4 found=0 … missing=4` exit 1 → `found=4 verified=4 missing=0
mismatch=0 off_ref=0` exit 0, selftest 15 cases, measured_commit `028235e6`).
After `028235e6`, `tools/citation-provenance.py` changed only in its diagnostic
print width (`git diff 028235e6 3389513f -- tools tests registry`: 2 lines,
both in a print statement). The author's own refutation of 7 → 8 is honest.
`build/advice/CritC1Inflation.md` exists, and the instrument checks digests,
not sentence-to-token correspondence.

**C2 operability 8 → 8.** C2 rests on a lane gate, so I verified its evidence and
did not execute it. I did re-derive the digest arithmetic myself.
`receipt-1.json` holds 51 install_tree members, and
sha256 of the sorted `name sha\n` lines is `6c216313…85a2c`. That equals the
recorded `install_tree_sha256` and the report's `--tree-sha`, and all three
DEFAULT_MEMBERS are present. A consistent swap recomputes `install_tree_sha256`,
so the old 5-pin set cannot see it, while the new `expect_tree` comparison
(`check-receipt.py` diff, +7 lines) must reject it. The committed
`evidence/c2-grid.txt` at `028235e6` shows exactly that:

- no pin: `rejected=0/3`, exit 1;
- with the pin: `rejected=3/3`, exit 0;
- invalid baseline: exit 2 with 0 members counted;
- grid selftest: green.

The gate selftest grew from 32 to 37 `mut(` cases (`grep -c` at base/tip). The
gate diff removes no check; it only widens a signature and a tuple.

Evidence gaps:

- `evidence/final-selftests.txt` was measured on
  `working-tree-on-5b108c1a…`, not on a commit, and still shows C1
  `required=3`. No committed gate-selftest tally names `028235e6`. The report
  says both "76-mutation" (line 91) and "77 gate mutations" (line 112).
- The grid's kill test is `code == 1`
  (`install-tree-grid.py:110`), so a crash exiting 1 without an INVALID line
  still counts as rejected. The author lists this as an open item. The report's
  §Extras "any non-zero exit" wording is stale after `84cf2f7`.

**No persistent model server, no large download.** I ran
`pgrep -af 'llama|ollama|vllm|ggml'`, which found nothing. `ss -ltnp` listeners
are the python shims started 2026-10-20 09:57, before the round, plus transient
python listeners. `tools/kama-llamacpp-live.py` tears down with SIGTERM and then
SIGKILL (`:799–849`) and contains no download code. No `.gguf` or model file
newer than 02:55 exists under `~/.cache/huggingface`, `~/.cache/llama.cpp`,
`~/models`, `~/.ollama` or `/tmp`, and the lane diff has no binary blobs.

There is one residue. 67 `/tmp/kama-r19-*` seat scratch directories total about
5.95 GiB on disk (`/tmp` is xfs, not tmpfs). They include a 675 MB
`ScorecardErratum/out/c2-official-argv.strace` written at 04:02, after the
03:59:14 completion line. It is a seat trace, not a download.

**No owned-axis harm.** `git diff 8bf99cae 3389513f -- SCORECARD.md` is a pure
append: the round-18 erratum plus the round-19 section, with operability 8 and
calibration 7 held and other axes unchanged. Legacy receipts keep their pins
because the new pin is optional. The round-19 section still carries stale
pre-final counts (`required=3`, `selftest 5 cases`), and both errata say "three
registry-row digests" against the final four-row registry. Routed below.

## Per-axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| calibration | improved | C1 re-measured 0/4 → 4/4 revision-bound citations; overreach caught and the score honestly held at 7 |
| operability | improved | C2 0/3 → 3/3 consistent-swap rejection, evidence-verified with digest arithmetic re-derived; score held at 8 |
| freshness | unchanged | no re-verification claim |
| coverage | unchanged | no new knowledge entry (16 → 16 `.md` files under `corpus/knowledge/`) |
| depth | unchanged | `llamacpp-loading-lifecycle.md` +10 appended lines on the pin boundary; no entry superseded |
| adjacency | unchanged | PROVINCE unchanged |

## Discernment spot-check (round-19 `## Gate`)

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| `$ORIGIN` "This expands to the directory containing the program or shared object" (S057) | admit | https://man7.org/linux/man-pages/man8/ld.so.8.html (fetched 2026-10-21; footer "Linux man-pages 6.19 2026-08-03") | agree | quote verbatim under §Dynamic string tokens `$ORIGIN`; supports loader-path resolution as the identity boundary, with the conclusion labelled [INFERENCE] |
| DT_RUNPATH "are searched only to find those objects required by DT_NEEDED" (S057) | admit | same page, §DESCRIPTION step (3) | agree | verbatim; continues "(direct dependencies) entries", so the scope note is correct |
| "A tree digest authenticates execution" | reject | same page | agree | the page has no "digest" or "checksum" text; the pin records observed bytes, and TreeCap shows symlinked sonames escape it |

Newly written row **S057** has two quotes, 10 and 11 words (≤25), located by
section. Both are verbatim and the version/date match. Agree.

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
→ three W04 (S031, S043, S056 duplicate URLs across scopes) and
`kama	ok	…/corpus/SOURCES.md`, exit 0. `census` → rows 57, A 54, C 3, mined 46,
queued 5, rejected 6. Rows 56 (`8bf99cae`) → 57 (`3389513f`) by
`grep -cE '^\| *S[0-9]{3} '`. This matches the report's figures.

## Trend verdicts

- **expansion: unchanged.** There is one new source row (S057) but no new
  admitted knowledge entry and no capability row, and LEARNING's `improved` row
  needs one of those. This differs from the lane's "improved (narrow)"; I
  record the disagreement rather than fault the lane.
- **quality: improved.** Bounded: all four routed round-18 defects are corrected
  and their pointers are machine-checked against bytes I re-opened. No
  admitted entry failed re-check. The defects routed below are record-hygiene
  defects, not false entries.
- **discernment: improved.** This outside spot-check agrees with the gate on two
  admits and one reject, and mined mistakes M1–M3 point to committed advice.
  The lane's "unchanged" was correct at write time, pending this act.

## Admission

Both declared claims verify: C1 re-measured, C2 evidence-verified with its
arithmetic re-derived. No axis is harmed → **admitted**.

## Routed defects / notes for the lane (next round)

1. Register `tools/citation-provenance.py` and `tests/llamacpp-live/install-tree-grid.py`
   in `SKILL.md` (gate|probe, verdict map, self-test spelling, pinned paths).
   Add `--expect-install-tree-sha256` to the receipt-gate row.
2. Sweep the stale C1 counts. The SCORECARD round-19 section (`required=3`,
   `selftest 5 cases`), the LOG round-19 entry (`missing=3`, `verified=3`), the
   errata ("three registry-row digests") and lesson-19's "before the tokens:
   `missing=3`" all disagree with the final four-row registry (0/4 → 4/4).
3. The lesson-19 and SCORECARD headings say "falsify-wave refutation", but the
   falsify wave never spawned (`falsify/refused-attempt-1.json`: 0/66).
   CritC1Inflation, CritAxisHarm and TreeCap are build-wave seats in
   `build/dispatch.json`. Append a correction.
4. `round-18.md:42` was rewritten in place (`30ed378`). Append a named
   correction recording the original wording.
5. Commit the round-19 census before/after receipts. Re-record gate and grid
   selftests at a commit, because `final-selftests.txt` names a dirty worktree
   on `5b108c1a`, and settle the 76 vs 77 mutation count.
6. `residual/assignments.json` (round 18) is a retrospective round-19 record.
   Label it so (provenance field or note).
7. Carried author-declared open items for round 20, most of them not yet in a
   committed lane artifact:
   - crash-as-rejection (`grid :110` counts any exit 1 without an INVALID line);
   - the observed-branch selftest gap in the checker;
   - 13 unregistered round-18 citations;
   - c2-survivors verdict-level-only agreement;
   - the S051 line anchor after the S057 insertion.
   Also carried: TreeCap (symlinked sonames), TreeDeterminism, GridDefaults,
   SentinalSecrets, and SCORECARD §Planned leaves.
8. Operator housekeeping: about 5.95 GiB of `/tmp/kama-r19-*` seat scratch
   remains, including a 675 MB strace written after round completion. This is
   not lane-committed and not deleted by this closure.
9. SHONEN: all four `[~]`. Box 2 remains the best candidate for non-author
   checking (five-pin live receipts, round 18). Boxes 1, 3 and 4 were not
   independently assessed. Promotion is operator-owned.
