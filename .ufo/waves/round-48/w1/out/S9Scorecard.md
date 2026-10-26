# S9Scorecard — round 48: SCORECARD `## Round 48` section and the head re-anchors

**Verdict:** the draft is assembled and measured — with it applied, plus the in-flight integration edits it requires, `round41-scorecard-reconcile.py`, `round42-selfdesc-reconcile.py`, `round43-registry-audit.py` and `planned-pointer-check.py SCORECARD.md` all report `met=True` (exit 0) on a scratch clone at `d052fac7`; the pre-conditions outside SCORECARD.md are the gate registry rows for the two round-48 counters, a PROVINCE.md instrument token, and the Axes row re-anchors measured below (depth, coverage, operability, calibration).

Nothing in the lane was written, staged or committed by this seat; the lane tree carries uncommitted L1/peer edits (banner, calibration row, appended banners, the repaired `tools/sources-append-only.py` and four other tool files) that this report treats as external and measures by copying into a scratch clone.

## 1. Deliverables

| Path (absolute) | What it is |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Scorecard/round48-section.md` | the authored `## Round 48 — …` section (35 authored lines; 52 inserted lines once `{{CANON}}` is spliced) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Scorecard/build_draft.py` | assembler: reads the build blob, asserts every replacement matches exactly once, splices the section, appends the superseded banner bytes |
| `…/S9Scorecard/05-scorecard-full-draft.patch` | the whole SCORECARD proposal, `b85783e8 → d052fac7` (head re-anchors + section + the four Axes re-anchors) |
| `…/S9Scorecard/04-scorecard-integration-reanchors.patch` | SCORECARD-only delta `54b1831e → d052fac7`: the Axes depth/coverage/calibration/operability re-anchors the in-flight `SKILL.md`, `PROVINCE.md` and `tools/sources-append-only.py` edits force |
| `…/S9Scorecard/03-provinces-instruments-row.patch` | proposed `PROVINCE.md:17` instruments-row extension (the two round-48 counters) |
| `…/S9Scorecard/SCORECARD.draft.md` | the full drafted file at the verified integration state (2,796 lines) |
| `…/S9Scorecard/r41-state-{a,b,c,d}.out`, `r42-state-{a,b,c}.out`, `r43-state-{a,b,c}.out`, `*state-e.out`, `planned-pointer-state-c.out`, `append-only-audit-at-draft.json`, `c1-counter-at-draft.out`, `sources-append-only-selftest.out`, `sources-append-only.sha256` | tool receipts quoted below |

## 2. What the draft changes (line anchors in `SCORECARD.draft.md`)

Head re-anchors (all inside the head regions SCORECARD.md:6 declares re-derived, except the banner):

- **`:6` authority banner → round 48** (“Latest measured round: 48”, kept-current list extended through round 48, and the new sentence naming where the replaced banner is kept). The **round-47 banner is appended byte-exact** as the last line (`:2796`), from `git show 380bcdff…:SCORECARD.md | sed -n 6p`; `tail -1 | cmp` against the extracted bytes → equal.
- **`:18` calibration row**: `→ `33` (outside closures on record)` → `→ `34``; latest outside closure `round-46-…` → `round-47-verifier-spotcheck.md`; last-change cell → round 48.
- **`:14` operability row** (forced, not a head re-anchor of this round): `run `python3 tools/sources-append-only.py --selftest` → `42/42 selftest cases passed`` → `45/45 …`, because the repaired tool now prints 45 cases; last-change cell → round 48.
- **`:53` the first `## Planned` pointer**: `### Planned (round 48)` → `### Planned (round 49)`.
- **`:117`, `:130`, `:131` capability mirror**: intro re-pointed at the round-48 canonical list; `append-only-audit` re-worded for v3 (region cell, binding rule, `regressed` in the exit, round-48 counter in the evidence cell) and `live-receipt-replay` for v5 (record-time verified provenance, pinned revision, stable projection, `--compare`); names and first-working rounds unchanged (46, 47).
- **`:137` saturation**: “kept current in rounds 47 and 48”; “A capability entered in round 47 …” → “Round 48 entered no capability … so one round of the four that would exhaust the window has passed.” `nudge inactive` kept (calibration 7 < 8).
- Round-48 section at **`:2736`**: authority paragraph (base `33e00582`, freeze `12284ba3` with both counter sha256s, controls, build `380bcdff`, separability), the two-claim table with counting commands and evidence, the controls line quoting all five control receipts, `### Round-48 measured results` (`:2747`) with `<pending>` measured cells and regression list, `### What met=True does not show (round-48 wave attacks)` (`:2758`) carrying the preregistration `limits` as disclosed-limit bullets plus one `<pending>` wave-findings bullet, the **canonical list as of round 48** (`:2765`, 11 rows, assembled from the byte-intact round-47 rows with the two re-worded), and `### Planned (round 49)` (`:2783`) with exactly two items.

Scores declared in the section: held at operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7; capabilities 11 → 11 (re-wording only).

## 3. Verification — five states on one scratch clone

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r48/S9Scorecard/lane` (toplevel asserted `= $S/lane` before every commit; commits made with `-c user.name/-c user.email` local to the clone only). `TMPDIR=$S`.

| State | Content | Commit |
|---|---|---|
| A | build blob + SCORECARD draft only | `54b1831e9ff9aef6210a064d1f62dc4865ef1b4e` |
| B | + the L1's uncommitted `SKILL.md` round-48 registry rows (sha256 `8629b3ac…`, 1482 lines) + the `PROVINCE.md` row patch | `1b5c142dd693b3e0b51bdc25f0eee3514798a7c7` |
| C | + Axes depth/coverage/calibration re-anchors and the last-change cells | `f2101f22f3ff18dbb38f42d1092011a21526f4ab` |
| D | + the repaired `tools/sources-append-only.py` copied from the lane working tree (sha256 `2e23a04e…`, selftest `45/45`) | `8e25604bb4313a4a76bc7a8e1fc1d876c6b13699` |
| E | + the operability row re-anchored `42/42` → `45/45` | `d052fac73d69000b223f905af2e423975c4c22ab` |

Commands (from `$S/lane`, tool paths relative to it):

```
python3 tools/round41-scorecard-reconcile.py --repo $S/lane --tip <commit> --out <receipt>
python3 tools/round42-selfdesc-reconcile.py  --repo $S/lane --tip <commit> --out <receipt>
python3 tools/round43-registry-audit.py      --repo $S/lane --tip <commit> --out <receipt>
python3 tools/planned-pointer-check.py SCORECARD.md
python3 tools/append-only-audit.py --repo $S/lane --to <commit> --json
python3 tools/capability-repertoire-audit.py --repo $S/lane --tip <commit>
python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip <commit> --scratch $S --out <receipt>
```

Observed:

| Check | A `54b1831e` | B `1b5c142d` | C `f2101f22` |
|---|---|---|---|
| round41 | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` exit 0 | `hash_bad=2 lines_bad=1 run_bad=1 mismatches=4 met=False` exit 1 | `mismatches=0 met=True` exit 0 |
| round42 | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=1 rel=0 mismatches=1 maxN=48 met=False` exit 1 | `r41=4 … province=0 … mismatches=4 met=False` exit 1 | `r41=0 … province=0 … mismatches=0 maxN=48 met=True` exit 0 |
| round43 | `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=0 hidden=0 pop=42 registered=40 mismatches=3 met=False` exit 1 | `unreg=0 … selftest=0 … spot=0 … pop=42 registered=42 mismatches=0 met=True` exit 0 | `mismatches=0 met=True` exit 0 |
| planned-pointer | — | — | `pointer: ok (… round 49 …)`, all nine `§Round-N measured results` refs resolve incl. `### Round-48 measured results`, `met=True` exit 0 |
| append-only v3 on the draft | — | — | exit 0; `summary` `events=5 restored=5 partial=0 unrestored=0 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0 ungraded_lines=89` |
| capability census | — | — | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` exit 0 |
| **C1 counter** at the draft tip | — | — | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` exit 0 |

States D and E (the repaired `tools/sources-append-only.py` from the lane working tree, copied into the clone):

| Check | D `8e25604b` | E `d052fac7` |
|---|---|---|
| round41 | `hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False` exit 1; `detail: operability run 'python3 tools/sources-append-only.py --selftest' no stdout line == '42/42 selftest cases passed' (exit 0)` | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` exit 0 |
| round42 | — | `r41=0 … province=0 … mismatches=0 maxN=48 met=True` exit 0 |
| round43 | — | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=42 registered=42 mismatches=0 met=True` exit 0 |
| planned-pointer | — | `met=True` exit 0 |

Control measurements (attribution):

- round41 at the build `380bcdff` **without** any draft: `run_bad=1`, detail `calibration run … no stdout line == '33' (exit 0)` → the stale `33` alone reddens round-41 (exit 1).
- round43 at `380bcdff`: `unreg=2 … selftest=1 … spot=1 … mismatches=4 met=False` → with the draft’s `34` the `spot` count clears; `unreg`/`selftest` remain and are the gate-registry items below.
- C2 (v5 live replay) was **not run** by this seat: the counter downloads ~74 MB and its measurement belongs to the L1. No C2 value is claimed here.

## 4. What the four tools require (in integration order, plus the run-fact consequence)

1. **`round42-selfdesc-reconcile.py` — `province=1` until `PROVINCE.md` names every `tools/`/`registry/` token carried by the highest canonical table.** At state A: `detail: province: PROVINCE.md lacks tools/round48-append-audit-v3-check.py (capability append-only-audit)`. Proposed fix: `03-provinces-instruments-row.patch` (extends `PROVINCE.md:17` with `tools/round48-append-audit-v3-check.py` and `tools/round48-live-replay-v5-audit.py`). The L1’s current `SKILL.md` draft does not affect this fact; peer S9Cap’s `proposed-PROVINCE.diff` covers only the v3 counter, so it is equally sufficient for its own canon rows.
2. **`round41-scorecard-reconcile.py` / `round42` `r41` — the `## Axes` rows hard-code digests of `SKILL.md` and `PROVINCE.md`, so any round that edits either file must re-anchor two rows in the same commit.** At state B: `depth sha256 SKILL.md cited 2e132fa6… observed 8629b3ac…`; `depth lines cited 1463 observed 1482`; `depth run 'grep -c …' no stdout line == '35'` (observed 36); `coverage sha256 PROVINCE.md cited 929f3e3e… observed 6388a9f4…` (line count still 186). Fix: `02-scorecard-axes-reanchors.patch`; the values must be re-derived (`sha256sum`, `wc -l`, `grep -c '^## '`) after the **final** `SKILL.md`/`PROVINCE.md` text lands — both files are still in flight in the lane working tree.
3. **`round43-registry-audit.py` — the two round-48 counters must be registered in a five-column `SKILL.md` registry row.** With the L1’s current `SKILL.md` draft: `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=42 registered=42 mismatches=0`. Without it: `unreg=2` **and** `selftest=1` (see F1) — one cause, two mismatch counts.
4. **`planned-pointer-check.py` — the first `## Planned` section must carry the contiguous sentence for round 49 and every `§Round-N measured results` reference must resolve.** Both hold in the draft; the new section must keep the heading spelling `### Round-48 measured results` (hyphen, as referenced) and must not be re-titled.
5. **`round41` — any round that changes a tool cited by an Axes `run` fact must re-anchor that fact.** The repaired `tools/sources-append-only.py` (working tree, sha256 `2e23a04e…`) prints `45/45 selftest cases passed`, not `42/42`; at state D that alone is `run_bad=1` (`detail: operability run 'python3 tools/sources-append-only.py --selftest' no stdout line == '42/42 selftest cases passed'`), cleared by the `:14` edit at state E. Four other working-tree tool edits (`tools/kama-live-replay.py`, `tools/gguf-identity.py`, `tests/llamacpp-live/check-receipt.py`, `registry/hexrun-ledger.tsv`) are cited by no Axes row, so they add no round-41 fact — but the round-47 regression list cites `kama-live-replay --selftest pass=13`, which the L1 must re-measure, not copy.

## 5. Findings

**F1 (new detail on a known item) — `round43`’s `selftest` fact is not independent of `unreg`: the gate’s Arm 6 grades the lane’s own `master` tip.**
`tools/gate-registry-check.py:333-350` (“Arm 6: this lane's own tree at its branch tip”, comment at `:333`) resolves `master`, runs `evaluate()` and requires `EXIT_CLEAN`; with the two round-48 counters unregistered the arm prints `FAIL lane-tip <tip>: exit=1 line='registered 40 unregistered 2 defective 0'` and the tool prints `GATE_SELFTEST pass=5 fail=1` exit 1, against the `GATE_SELFTEST pass=6 fail=0` that `SKILL.md:1330` documents — which is exactly what `tools/round43-registry-audit.py:173-187` grades (`documented {want!r}, run printed {last!r}`). Reproduce: `python3 tools/round43-registry-audit.py --repo <clone> --tip 380bcdff…` → `selftest=1`. So the round-48 counters being unregistered costs *two* mismatches (`unreg`, `selftest`) in one counter, and both clear with the same SKILL.md rows (measured at state B). Proposed fix: none needed in the counter; the integration must land the rows before the round-43 counter is re-run, and the round-48 report must not read `selftest=1` as a second defect.
**F2 — the Axes table couples the SCORECARD to three other files’ bytes per round.** Exact file/line: `SCORECARD.md:14` (operability, `run` fact of `tools/sources-append-only.py --selftest`), `SCORECARD.md:16` (depth, `SKILL.md` sha256 + line count + `grep -c '^## '`), `SCORECARD.md:17` (coverage, `PROVINCE.md` sha256). Command that shows it: section 3, state B → `mismatches=4`; state D → `mismatches=1`. Proposed fix: the re-anchors in `04-scorecard-integration-reanchors.patch`, re-derived at integration time. (This is the round-47 “re-measured at the post-measure fix commit” pattern repeating; it is avoidable only by dropping the digests, which is a design change, not this seat’s call.)
**F3 — the stale spot-check figure reddened two counters, not one.** `33` was correct at the round-47 measured tip `383f1fc7` and stale from the round-47 closure commit `33e00582` (which added `corpus/lessons/round-47-verifier-spotcheck.md`; `git log --diff-filter=A` names `33e00582`). Measured at `380bcdff`: round-41 `run_bad=1` (glob prints 34) and round-43 `spot=1` (`calibration row states 33, tree holds 34`). The draft’s `34` clears both (states A and C).
**F4 (coordination, not a defect) — peer S9Cap independently drafts the same two capability rows and the round-48 canonical block** (`.ufo/waves/round-48/w1/out/S9Cap/round48-canonical-block.md`, `proposed-SCORECARD.diff`, `proposed-PROVINCE.diff`, `after-audit.out` `listed 11 observed 11`). The two texts differ only in wording (their `live-receipt-replay` row says `kama-llamacpp-live/v5`, this draft says `v4` or `v5`); the counters read only the 11 names, their order-independent set and the first-working-round integers, so either text satisfies `caps`/`saturation`/capability census. The L1 should take one — this draft’s `{{CANON}}` slot is `SCORECARD.md:2765-2781`, so S9Cap’s block can be substituted there verbatim and only the head mirror rows (`:130-131`) need matching. Their `proposed-PROVINCE.diff` adds the v3 counter only; that is sufficient for their canon rows.

## 6. Not done / out of scope

- **The C2 counter was not run** (`tools/round48-live-replay-v5-audit.py`, ~74 MB of downloads); the `### Round-48 measured results` cells are `<pending>` placeholders, and the receipt paths named there (`.ufo/waves/round-48/measured/c1-after.out`, `c2-after.out`) are the round-47 naming pattern — the L1 should rename them if it measures elsewhere.
- The `### What met=True does not show` wave-findings bullet stays `<pending>`; only the preregistration’s own `limits` are written out, verbatim in substance.
- No lane file was edited, staged or committed; no service was started; no network call was made by this seat except the clone (local, `--shared`).
- The Axes **scores** were not re-assessed (held at 8/8/7/9/7/7 by the draft), and no capability enters, so the saturation window moved from 0 to 1 of 4 — stated in `:137`.

## 7. Provenance and limits

- Base for every draft diff: `b85783e8` (whose `SCORECARD.md` is byte-identical to the build commit `380bcdff`, verified with `git show … | cmp -`).
- The draft was assembled by `build_draft.py`, which replaces exactly-named strings and asserts a single match for each; it is not a hand edit of the lane file, and the resulting diff (`05-scorecard-full-draft.patch`) is the proposal.
- State C is a **synthetic integration state** in scratch: its `SKILL.md` is the L1’s uncommitted working-tree file (sha256 `8629b3ac…`), copied for measurement only and not proposed by this seat. If the final `SKILL.md` differs, the depth row and `round43` must be re-measured; the mechanism is what this report establishes.
- States C, D and E are **synthetic integration states** in scratch: `SKILL.md` is the L1’s uncommitted working-tree file (sha256 `8629b3ac…`) and `tools/sources-append-only.py` is the in-flight repair (sha256 `2e23a04e…`), copied for measurement only and not proposed by this seat. If either final file differs, the depth and operability rows and the round-43 verdict must be re-measured; the mechanism is what this report establishes.
- The lane working tree already carries an equivalent `:6` banner and `:18` calibration edit (applied by the L1/peers after this seat started), plus appended round-42/43/44 banners from seat X1Banner. Integration should therefore take the draft’s remaining hunks — `:53`, `:117`, `:130-131`, `:137`, the four Axes re-anchors and the round-48 section — and not double-apply `:6`/`:18`; the byte-exact round-47 banner is appended wherever the appendix ends.
- `met=True` on these four counters says the self-description surfaces agree with the tree at that commit; it does not say the round-48 claims are true — that is the L1’s C1/C2 measurement under the frozen counters.
