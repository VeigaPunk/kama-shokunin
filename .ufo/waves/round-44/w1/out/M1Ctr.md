# M1Ctr — mutation test of the frozen C1 counter `round44-release-recheck-audit.py`

**Verdict: the C1 counter survives its mutation battery — 32 of 39 single-rule mutants are killed behaviorally (exit code or summary line changes) by a 35-input fixture battery; the 7 survivors are equivalent mutants on the frozen inputs (each with a proof or a named unreachable fixture below); no counter defect found.**

Target: `kama-shokunin/tools/round44-release-recheck-audit.py` at lane commit `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40` (sha256 `87503e18e47dae6fa0414cf24d988f2a44ffa61d422db62c82cad3c24d8218d2`). The lane file was never edited; all mutants lived in scratch (`/fast/scratch/hyaku/kama-r44/M1Ctr/mut/`, removed at the end).

## 1. Setup (commands, isolation)

```
S=/fast/scratch/hyaku/kama-r44/M1Ctr; mkdir -p "$S/ctl" "$S/mut" "$S/out"; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"   # HEAD 098df344 (drafts committed)
```

Upstream: `/fast/scratch/hyaku/kama-r44/shared/llama.cpp` (read-only; holds `704366d76f…`=b11755 pins and `d854d98bae…`=b11889). Fixture commits used the fixture identity from `build_controls.py` (`r44-control@fixture.invalid`) and ran only inside scratch clones; `git rev-parse --show-toplevel` isolation is asserted by `bc.clone` (`.ufo/waves/round-44/controls/build_controls.py:31-39`).

## 2. Detector

For each (mutant, fixture): run `python3 <mutant> --repo <fixture tree> --tip <tip> --upstream <llama.cpp>`, capture `(exit, stdout)`, and compare against the pristine counter's output on the same fixture, ignoring the `tip=` line (fixture-constant). Classification:

- **killed-behavioral** — exit code or summary line (`pop=… met=…`) differs;
- **killed-strict-only** — only `detail:` lines differ (same exit + summary);
- **survived** — byte-identical behavior on every fixture.

The counter's contract (docstring, `round44-release-recheck-audit.py:2-49`) is exit 0/1/2 plus the summary line, so behavioral kills are the meaningful ones; no mutant was killed strict-only.

## 3. Fixtures (35)

Built by `scripts/build_fixtures.py` (+ `scripts/addendum.py`, `scripts/addendum2.py`), all under `$S/ctl/`, tips recorded in `fixtures.json`:

- **IN1-base** — lane clone read at BASE `9d9cc93e…` (no ledger, no section). Pristine: `pop=91 rows=0 … met=False`, exit 1.
- **IN2-allunchanged**, **IN3-draftonly** — exact mirrors of `build_controls.py`'s `junk-c1-allunchanged` / `junk-c1-draftonly` trees (same draft generation via `tools/release-recheck.py draft`, same edits). Pristine: exit 1, `valid=6` / `valid=85`.
- **pass** — synthetic fully-valid ledger: the 91-row draft with its 6 TODO rows completed mechanically (S015/S059 → `unchanged-file`; S001/S037/S043/S108 → `drifted` with `1-1` release ranges), SOURCES section + knowledge-file flag lines for the 4 drifted ids. Every row was oracle-validated with the **pristine** counter's own `check_row`; pristine run: `pop=91 rows=91 valid=91 unverified=0 … met=True`, exit 0. Caveat: the 4 drifted rows are satisfiability placeholders chosen to exercise counter mechanics — they say nothing about the lane's real C1 verdicts.
- **31 one-defect fixtures** (F01–F28, F27b, F28b, F32, F33) — `pass` + exactly one targeted corruption each; pristine rejects each with exactly the expected isolated reason (e.g. `F27b`: `detail: S001 invalid: release range outside file`), so any mutant that accepts the row flips `unverified` 1↔0 and `met` False↔True.

Two fixture iterations are worth recording as counter properties they exposed:
- F27/F28 v1 used `1-999999` and were **eaten by the 80-line cap** (`ranges()`, line 176 rejects span ≥ 80 before the outside-file checks at lines 208/213 ever fire) — replaced by cap-legal beyond-end ranges (`F27b` `2519-2526`, `F28b` `2396-2403` on S001's 2400-line pin file).
- M06 was first judged equivalent (no ≤79-line pinned file exists for a pin-side `0-<len>` trick) until re-analysis showed the 20-char rule guards only pin ranges — a release-side `0-3` kills it (F33).

## 4. Results

39 mutants × 35 fixtures = 1365 counter runs (plus 35 pristine baselines), 78 s wall. Full matrix: `M1Ctr/matrix.json`, run log `M1Ctr/battery.log`, per-rule diffs `M1Ctr/diffs/M*.diff`, row-level detail in **`M1Ctr/mutants.tsv`**. 32 killed-behavioral; survivors:

| mutant | rule (counter line) | mutation | why no input kills it | smallest fixture that would kill |
|---|---|---|---|---|
| M03 | changed flag (198) | derive `changed` from ledger blobs instead of upstream blobs | the blob-equality check (line 196) runs first and forces ledger blobs == upstream blobs whenever `changed` is used, making the two derivations identical; when blobs lie the row is rejected earlier with the same summary | none — equivalent by construction while the blob check holds |
| M12 | WEAK cited-line coverage (223) | drop the weak-fallback rejection | branch is dead code: no population row has empty STRONG and ≥1 in-file WEAK cite (scan: `weak-only=[]`, `M1Ctr/scan.json`) | a frozen-BASE SOURCES row citing only a bare 2–5-digit number, with `pin_lines` avoiding it — population is frozen, cannot be constructed |
| M13a | STRONG coverage (217) | drop the `n <= len(ptext)` filter (tightening) | no row cites a STRONG line beyond its pinned file (`strong-beyond=[]`) | a population row citing e.g. `#L99999` in a 2k-line file |
| M13b | WEAK coverage (218) | same, for WEAK | `weak-beyond=[]` | same shape, weak cite |
| M27 | duplicate rows (287) | first-wins instead of last-wins | the intact dup flag (line 285) invalidates the id regardless of which copy is kept | none single-rule; killable only jointly with a dup-flag mutant |
| M28 | SOURCES section in `met` (336) | drop `and section == 1` | on this population `unverified=0 ∧ missing=0 ⟹ section=1`: S037/S043/S108 have strong-cited lines whose text is absent from the release file (measured 4/46, 2/31, 1/28 absent), so they cannot be `holds`/`holds-reworded`, and `changed=1` bars `unchanged-file` — any fully-valid ledger contains ≥1 valid drifted row, and with no section each adds `flags_missing≥1` | a population where every row re-locates verbatim plus a sectionless tip — impossible here |
| M36 | population filter (123) | drop the `on-release`/`mined|queued` test | all 56 eleven-cell rows failing that test also lack a ggml-org/llama.cpp URL (measured), so the URL filter (line 124) re-absorbs them; `pop` stays 91 on every fixture | a frozen-BASE SOURCES row with a llama.cpp URL + 40-hex pin but cadence ≠ `on-release` |

The 32 kills cover every rule family the seat was assigned: blob comparison (M01–M02), changed flag (M04), range parsing incl. `a<1`/`b<a`/dash-in-pin/outside-file (M06–M08, M39–M40), the 80-line cap (M05), the 20-char pin-range rule (M09–M10), STRONG/WEAK cited-line coverage (M11), every verdict branch (M14–M23), the drifted/removed flag checks (M30–M33), the SOURCES section check (M29), duplicate-row handling (M26), plus header check (M34), population binding (M25), release cell (M24), exit code (M38).

## 5. Findings

1. **No counter defect.** No single-rule mutant turns a wrong ledger into `met=True` on any constructible input: every loosening mutant is killed by a one-defect fixture, and every survivor is provably equivalent on the frozen inputs or blocked only by the frozen population (a coverage note, not a contract change).
2. **Redundancy, not weakness.** M28 (`section==1` conjunct) and M36 (recheck/status filter) are backed by other rules (flag machinery; URL filter) on this population — the conjuncts are redundant *here*, not wrong.
3. **Control layering.** `junk-c1-allunchanged` kills only joint blob+changed drops (its blob lie and flag lie cover each other); single-rule assurance comes from the targeted fixtures — worth keeping in mind when reading the committed control receipts.
4. **Robustness note (pristine, unreachable):** if `pin_lines` ever contained `-`, `check_row` would crash on `None[1]` (line 202) — unreachable because `ranges(pin_lines, False)` never yields `None`; only the M08 mutant reaches it (killed by IN3's crash-divergent output).
5. **Harness bug found and fixed (mine, not the counter's):** `open(p, "w").write(edit_row(open(p).read(), …))` truncates before the read (target expression evaluated first) — the addendum initially built empty-ledger fixtures; switched to `read_led`/`write_led` helpers.

## 6. Restoration evidence

- Lane counter sha256 before: `87503e18e47dae6fa0414cf24d988f2a44ffa61d422db62c82cad3c24d8218d2`; after the battery: identical (re-verified at cleanup).
- No `git add/commit/checkout/stash/reset` and no jj mutation was run in the lane; all fixture commits carried the fixture identity inside `$S` clones; scratch `$S` removed at the end (`rm -rf /fast/scratch/hyaku/kama-r44/M1Ctr`), receipts copied out first.
- Tooling record: no tools installed or upgraded (python 3.14 + git only, both preexisting); no pacman use.

## 7. Receipts (relative to `kama-shokunin/`)

- `.ufo/waves/round-44/w1/out/M1Ctr/mutants.tsv` — 39 rows: mutant, rule, counter line, mutation, verdict, killed_by, note
- `.ufo/waves/round-44/w1/out/M1Ctr/matrix.json`, `fixtures.json`, `scan.json`, `battery.log`, `build.log`, `addendum.log`
- `.ufo/waves/round-44/w1/out/M1Ctr/diffs/M*.diff` — pristine→mutant unified diffs
- `.ufo/waves/round-44/w1/out/M1Ctr/scripts/{scan,build_fixtures,mutate_and_score,addendum,addendum2}.py`
