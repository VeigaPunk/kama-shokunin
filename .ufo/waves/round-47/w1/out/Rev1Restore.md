# Rev1Restore — what "restoration" means in kama's own history, and which v2 verdict is signal

**Verdict (one line):** v2's five events at the tip reconstruct the lane's history correctly — three are the true signal (the `0718b6ab` append-bug truncation, repaired byte-exact at `82b5e9d3`, including SCORECARD at 2420/2421) and the two partials are the *declared* SCORECARD §Axes head re-anchor — all 8 non-restored line occurrences are §Axes head lines (the six axis rows plus the reconcile paragraph at `dd9f5dc6`; the depth row inside the repair) — so the exit 1 is an instrument gap, not a lane violation. Giving the contract's own "expected partial" a machine-readable form (`exempt=` in the row's note) plus a matching read in the tool makes exit 0 at the tip while all four non-vacuity mutants still exit 1.

## Pins (what was measured, and a workspace caveat)

| object | value |
|---|---|
| lane commit | `3a09a1d93dcc16799cf6c4b48786e6440af134c4` |
| measured tool | `git show 3a09a1d9:tools/append-only-audit.py`, sha256 `5d47bc77e9bde41a1af1fcba449e60fd027d9ed30fbf2770a5a53f177856f874`, 500 lines (copy: `out/Rev1Restore/append-only-audit-v2-at-3a09a1d9.py`) |
| contract | sha256 `57ac17253522ec12c311341e564cd38e52a189aa0d0044c1d7a666f443c76608`; identical at `3a09a1d9` and in the working tree |
| clone | `git clone --shared <lane> $S/lane`, `git -C $S/lane rev-parse --show-toplevel` = `$S/lane` |

Caveat: while this seat measured, the lane *working tree* carried uncommitted edits from concurrent seats, including the same tool: at 18:37 the working-tree `tools/append-only-audit.py` was 604 lines, sha256 `a7feae03eaf97122fe73433c7c8524b4d5d5ac562bfc5f6938b9f5ef5891217d`, and `git -C <lane> status --porcelain` listed ` M tools/append-only-audit.py` among other ` M` files (the list kept growing while this seat worked: `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md` also appeared later). That working-tree version adds `vanished=/unmatched=/binary=` summary keys. Every receipt below runs the **committed `3a09a1d9` bytes**, not the working tree; line citations for the tool therefore use the pinned copy.

## 1. What each commit intended (from its subjects and its own round record)

| commit | subject / record | intended | observed |
|---|---|---|---|
| `0718b6ab` | subject "round-45: lesson, KQ62-KQ65, seat-yield and manifest-crosscheck tools, D3 corrections, SKILL registry, measured results, end census"; `corpus/lessons/round-45.md:30` mistake row 5 | land round-45 content; append-only files only appended | the L1's append idiom `open(p,'w').write(open(p).read()+…)` truncated before it read: `LOG.md` 2295→8 lines (numstat 5/2292), `SCORECARD.md` 2429→17 (9/2421), `corpus/QUALITY.md` (4/375), `corpus/README.md` (2/663) |
| `82b5e9d3` | subject "round-45: restore SCORECARD/LOG/QUALITY/README bodies truncated by the previous commit (append bug) and re-append round-45 text; SKILL v2 row flags; depth re-anchor" | restore the lost bodies from the last good state and re-append round-45 text | `git diff --numstat 21945c61 82b5e9d3` = `LOG.md 7/0`, `SCORECARD.md 17/1`, `corpus/QUALITY.md 4/0`, `corpus/README.md 4/0`: the repair is the pre-truncation state (`21945c61`) plus insertions only, except one deliberately re-derived line (`repair-fidelity.out`) |
| `dd9f5dc6` | subject "round-42: claim work — SCORECARD head and README/PROVINCE reconciled (C1)"; `SCORECARD.md:2248`, `:2254`; `LOG.md:2265` | re-derive the SCORECARD head (§Axes table, §Planned, §Retired, §Saturation, §Capabilities) from the tree so it matches observed repository state | 31 lines deleted, 98 inserted in SCORECARD; 24 of the 31 are held **in the same commit** because the round-5 banner and the §Planned/§Retired bodies were moved verbatim under `## Historical head sections`; the 7 not held are the §Axes rows and their preamble |

Restoration, as the lane itself defines it in these two commits, is therefore: *re-append the body from the last good state and change nothing but the head rows the commit re-derives*. That is exactly what v2 measures (content multiset over the event's window), and it is why `82b5e9d3` scores 2292/2292, 375/375, 663/663 and 2420/2421.

## 2. v2's verdicts at the tip, set against that history

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_max=24 status=partial restored_best=dd9f5dc6c0e6 restored_by=-
event 0718b6abbda6 LOG.md deleted=2292 restored_max=2292 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 SCORECARD.md deleted=2421 restored_max=2420 status=partial restored_best=82b5e9d33a19 restored_by=-
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_max=375 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 restored_max=663 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0
exit=1
```

Per-line triage (`restored-per-line-dd9f5dc6.tsv`, `partition.txt`):

* `dd9f5dc6` SCORECARD, 31 deleted / 24 held / 7 rewritten. The 7 rewritten are parent lines 17 and 21–26, all inside `## Axes` (parent range 15–57): the "Reconciled in round 41 …" paragraph and the six axis rows (operability, freshness, depth, coverage, calibration, adjacency). The 24 held are the round-5 banner (parent 6–13) and the §Planned/§Retired bodies (parent 60–77) relocated verbatim into §Historical head sections, plus the `## Saturation` heading. This is the round-42 C1 re-derivation, declared at `SCORECARD.md:6` ("The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived from the tree … kept current in rounds 43, 44, 45 and 46") and classified by the lane itself at `LOG.md:2307` ("2 SCORECARD partials that are documented head re-derivations").
* `0718b6ab` SCORECARD, 2421 deleted / 2420 held / 1 rewritten. The single line is parent line 16, the §Axes **depth** row, re-anchored in the repair commit from `SKILL.md` sha256 `91440eb8…` (1420 lines) to `3046955b…` (1432 lines, `grep -c '^## '` = 33), which is exactly the state of `SKILL.md` at `82b5e9d3` (verified: `git show 82b5e9d3:SKILL.md | sha256sum`, `| wc -l`, `| grep -c '^## '`). So the repair lost nothing; it updated the head row the same commit re-derived.
* `0718b6ab` LOG / QUALITY / README: restored == deleted, and `82b5e9d3` deletes no line of `21945c61` in those files (numstat 7/0, 4/0, 4/0), so the truncation left no residue.

| verdict | classification | why |
|---|---|---|
| `0718b6ab` LOG 2292/2292, QUALITY 375/375, README 663/663 | **true signal** | the append-bug truncation was detected and repaired byte-exact at `82b5e9d3`; `restored_by` names the repair commit |
| `0718b6ab` SCORECARD 2421/2420 | **true signal + head carve-out** | 2420 lines restored byte-exact; the 1 unrestored line is the §Axes depth row, re-derived in the repair commit |
| `dd9f5dc6` SCORECARD 31/24 | **exempt head carve-out** | all 7 unrestored occurrences are §Axes head rows rewritten in place by the round-42 C1, declared expected at `SCORECARD.md:6` and in `registry/append-only-contract.tsv:3` ("a head re-anchor is an expected partial") |
| `unrestored=0`, 303 commits | **true signal of absence** | no ≥20-line deletion in any contracted file was left unrepaired anywhere in the lane's history |

D1/D2 closure restated from the same receipts: deleted counts equal git numstat exactly (`2421`, `2292`, `375`, `663` — v1 read 2417/2290, D1), and the five events have identical `deleted`/`restored_max` at the base (301 commits) and the tip (303) — moving the tip does not lower a restoration (D2). Evidence `v2-tip.out` vs `v2-base.out`.

## 3. The defect and the single change

**Defect (instrument, not history).** `tools/append-only-audit.py` at `3a09a1d9` computes status from the whole deleted multiset at line 218 (`status = "restored" if best == len(dl) else …`) and maps any partial to exit 1 at lines 239–241 (`return 1 if s["partial"] or s["unrestored"] else 0`). The contract row that governs SCORECARD (`registry/append-only-contract.tsv:3`) declares an expected-partial class in prose only ("… so a head re-anchor is an expected partial") and the tool parses nothing from `note`. Command that shows it: the v2 tip run above (`exit=1`) with `unrestored=0` and two partials whose every non-restored occurrence is a §Axes line. Consequence: at a tip where the lane's declared rule holds, the instrument's exit code still says it does not — exit 1 carries no signal here.

**Single change that closes it** (proposed full text and diff in this directory): read a trailing `exempt=<title>|<title>|…` clause from the contract row's `note` and grade a deleted line only when it falls outside a declared re-derived section; honour a title only when that section holds at least as many lines at the audited revision as at the event's parent (so a truncation that is never repaired still fails); report `graded=N exempt=E` and exit 1 only on graded partial/unrestored.

* `registry/append-only-contract.tsv:3` note gains `; exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities` (`contract-v3.tsv`, `contract-v3.diff`).
* Tool: `append-only-audit-v3.py` (+ `append-only-audit-v3.patch`, 270 lines, base = the `3a09a1d9` blob). Format stays 4 cells / same header — a fifth column was rejected because the frozen C1 contract leg requires exactly 4 cells and a known rule.

Proof at the tip (`v3-tip.out`, `v3-tip.json`):

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 graded=23 exempt=8 restored_max=23 status=restored restored_best=dd9f5dc6c0e6 restored_by=dd9f5dc6c0e6
event 0718b6abbda6 LOG.md deleted=2292 graded=2292 exempt=0 restored_max=2292 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 SCORECARD.md deleted=2421 graded=2349 exempt=72 restored_max=2349 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/QUALITY.md deleted=375 graded=375 exempt=0 restored_max=375 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 graded=663 exempt=0 restored_max=663 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
summary commits=303 files=85 events=5 restored=5 partial=0 unrestored=0 exempt=0 exempt_lines=80
tip_exit=0
```

`exempt_lines=80` = 8 (dd9f5dc6) + 72 (0718b6ab), the second being all five declared head sections at the truncation event (Axes 42, Capabilities 18, Planned 4, Retired 4, Saturation 4). At the base the same five events read the same and exit 0 (`v3-base.out`), so the verdict does not depend on the tip moving. Selftest: `AOA_SELFTEST pass=18 fail=0`, exit 0 (`v3-selftest.out`; the v2 15 cases unchanged plus `exempt-head-rewritten`, `exempt-head-gutted`, `dated-rewritten`).

Non-vacuity — four mutants committed in the scratch clone at the tip (identity `r47-fixture`, toplevel asserted each time; receipts `m*.v2.out`, `m*.v3.out`, `mutants.out`):

| mutant | change | v2 exit | v3 exit | v3 event |
|---|---|---|---|---|
| m1 dated-rewrite | 25 lines of `## Round 41` replaced in place | 1 | **1** | `deleted=25 graded=25 exempt=0 status=unrestored` |
| m2 axes-rewrite | 25 lines of `## Axes` replaced in place, count unchanged | 1 | **0** | `deleted=25 graded=0 exempt=25 status=exempt` (the declared re-derivation v2 cannot express) |
| m3 axes-gutted | 25 `## Axes` lines → 2 (section shrinks 43→20) | 1 | **1** | `graded=25 exempt=0 status=unrestored` (guard refuses) |
| m4 head-truncated | SCORECARD truncated to 5 banner lines + 1, no repair | 1 | **1** | `deleted=2676 graded=2676 exempt=0 status=unrestored` (a repeat of `0718b6ab` without `82b5e9d3` still fails) |

m1 is why a generic "same heading, same size ⇒ exempt" rule is wrong: it would let a dated-section rewrite pass. m3/m4 are why the carve-out cannot be a blanket "head sections are free".

**Scope limit on the change, stated so it is not oversold:** the threshold (default 20, frozen at 20) is unchanged, so exit 0 means "no graded event of ≥20 deleted lines is partial or unrestored", not "append-only holds at every size". And because the frozen round-47 C1 counter (`tools/round47-append-audit-v2-check.py`, `lane` leg) pins v2's exact event values, statuses and exit-code agreement, v3 cannot be scored by it: at this tip C1-v2 would read `lane=0` against a v3 tool. The change is therefore a round-48 instrument (schema `append-only-audit/v3`) with its own counter, not a patch to the frozen round-47 instrument — which is also why C1 `met=True` and this tool's `exit=1` coexist without contradiction.

## 4. Further calibration findings

1. **Contract provenance for SCORECARD.** `registry/append-only-contract.tsv:3` sets `declared_at` = `corpus/README.md:521`, which is a round-33 correction record whose text is "append-only records in `corpus/lessons/round-33.md` and `SCORECARD.md`." The five-file append-only set is declared at `corpus/README.md:758-761` (the set itself at :760), and SCORECARD's own exception at `SCORECARD.md:6`. C1's contract leg only tests that the declared line's text contains "append" (`round47-append-audit-v2-check.py`, contract leg), so the row passes while pointing at the weakest of the three. Suggested fix (row text, next round): `SCORECARD.md  A-corr  SCORECARD.md:6  dated round sections append-only (set rule corpus/README.md:760); head sections re-derived in place since round 42; …`.
2. **Relocation counts as restoration.** v2's `held(x)` is a content multiset over the window, so the 24 "restored" lines of `dd9f5dc6` are lines moved verbatim into §Historical head sections, not lines left in place. The tool docstring and the `relocation` selftest case declare this deliberately; it is worth saying "content preserved anywhere in the file" whenever this number is quoted.
3. **§Planned and §Retired are net-shrunk at the tip** (12→3 and 9→3 lines versus the round-42 parent), because their bodies live under §Historical head sections. Under the tip guard v3 grades those 15 lines; they are held by relocation, so the tip stays exit 0. If the lane wants them exempt it must either keep them non-shrinking at the tip or accept the conservative grade — the current behaviour refuses the carve-out and does not hide a real loss.

## 5. Commands run (receipts in this directory)

```
S=/fast/scratch/hyaku/kama-r47/Rev1Restore; O=<out>/Rev1Restore
TIP=3a09a1d93dcc16799cf6c4b48786e6440af134c4
BASE=172b8ad040d51ce8c011238c1408d4e0b6aa9595
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel                                  # $S/lane

python3 "$O/append-only-audit-v2-at-3a09a1d9.py" --repo "$S/lane" --to $TIP \
        --contract "$O/append-only-contract-at-3a09a1d9.tsv"                # exit 1  (v2-tip.out)
python3 "$O/append-only-audit-v2-at-3a09a1d9.py" --repo "$S/lane" --to $BASE \
        --contract "$O/append-only-contract-at-3a09a1d9.tsv"                # exit 1  (v2-base.out)
git -C "$S/lane" diff --numstat 21945c61 82b5e9d3 -- LOG.md SCORECARD.md \
        corpus/QUALITY.md corpus/README.md                                  # repair-fidelity.out
git -C "$S/lane" show 82b5e9d3:SKILL.md | sha256sum; ... | wc -l; ... | grep -c '^## '   # depth row re-anchor check

python3 "$O/append-only-audit-v3.py" --selftest --scratch "$S"              # exit 0, AOA_SELFTEST pass=18 fail=0
python3 "$O/append-only-audit-v3.py" --repo "$S/lane" --to $TIP \
        --contract "$O/contract-v3.tsv"                                     # exit 0  (v3-tip.out/json)
python3 "$O/append-only-audit-v3.py" --repo "$S/lane" --to $BASE \
        --contract "$O/contract-v3.tsv"                                     # exit 0  (v3-base.out)

# mutants: a detached branch per mutant off $TIP inside the scratch clone, identity r47-fixture,
# toplevel asserted before each commit; each run audits --to HEAD with both tools.
S=$S O=$O python3 mutants.py                                                # m1 1/1, m2 1/0, m3 1/1, m4 1/1 (mutants.out)

patch -p1 --dry-run < "$O/append-only-audit-v3.patch"                       # applies to the pinned v2, exit 0
```

No lane file was modified; all fixture commits live only in the scratch clone (removed at exit), and no receipt
depends on a `/tmp` path. No tool installs were needed.

## 6. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/append-only-audit-v2-at-3a09a1d9.py` (pinned measured tool, sha256 `5d47bc77…`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/append-only-contract-at-3a09a1d9.tsv` (pinned contract, sha256 `57ac1725…`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/append-only-audit-v3.py` (proposed full text, sha256 `4341d410…`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/append-only-audit-v3.patch` (unified diff against the pinned v2)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/contract-v3.tsv`, `contract-v3.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/v2-tip.out`, `v2-tip.json`, `v2-base.out`, `v3-tip.out`, `v3-tip.json`, `v3-base.out`, `v3-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/restored-per-line-dd9f5dc6.tsv`, `partition.txt`, `repair-fidelity.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/Rev1Restore/m1-dated-rewrite.{v2,v3}.out`, `m2-axes-rewrite.{v2,v3}.out`, `m3-axes-gutted.{v2,v3}.out`, `m4-head-truncated.{v2,v3}.out`, `mutants.out`
