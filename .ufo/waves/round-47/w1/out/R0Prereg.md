# R0Prereg — Round 47 freeze integrity (lane kama)

**Verdict: PASS — all freeze-integrity checks hold; no mismatches found (controls reproduce exactly, modulo by-construction tip=/started= lines and the counter's own random fixture detail lines).**

Scratch: `/fast/scratch/hyaku/kama-r47/R0Prereg` (removed before finish). Lane clone (read-only): `$S/lane` (`git clone --shared`). No tools were installed (python3/git already present; no installs needed — operator tooling rule recorded, nothing to report). The lane, fleet repo and controls dir were never written; the builder was run from a copy in scratch.

## 1. Preregistration predicates == counter docstring PREDICATE sentences — PASS

Extracted PREDICATE from each counter docstring and compared to `preregistration.json` `claims[].predicate`:

- C1: `round47-append-audit-v2-check.py:93-98` vs `preregistration.json:17`.
- C2: `round47-live-replay-audit.py:66-70` vs `preregistration.json:32`.

Raw string comparison differs only by the docstring's source line-wraps (embedded newlines); after collapsing whitespace both are identical. Evidence (eval):

```
C1 normalized docstring PREDICATE == prereg predicate: True
C2 normalized docstring PREDICATE == prereg predicate: True
```

## 2. counter_sha256 == sha256 of the frozen blobs — PASS

`git show bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba:<path> | sha256sum`:

```
C1: a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed  (preregistration.json:19 identical)
C2: 15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f  (preregistration.json:34 identical)
```

## 3. Both counters byte-identical at 3a09a1d93dcc16799cf6c4b48786e6440af134c4 — PASS

Blob object IDs (`git rev-parse <rev>:<path>`):

| counter | at freeze bbcc6dc2 | at build 3a09a1d | identical |
|---|---|---|---|
| C1 tools/round47-append-audit-v2-check.py | e74d168caa0abd7adc09acfd3579e0f139d519c9 | e74d168caa0abd7adc09acfd3579e0f139d519c9 | yes |
| C2 tools/round47-live-replay-audit.py | 2c345e08669ccb9b4393c704df8836efc2e706b3 | 2c345e08669ccb9b4393c704df8836efc2e706b3 | yes |

## 4. prereg-time-check.out shows exit 0 — PASS

`.ufo/waves/round-47/freeze/prereg-time-check.out` line 5 `RESULT pass: no timestamp later than the committer time`, line 6 `exit=0`; both prereg timestamps (lines 6, 42) reported `ok` (at/before commit).

## 5. frozen_at_utc precedes the freeze commit time — PASS

`frozen_at_utc` = 2026-10-26T21:12:52Z (preregistration.json:6). Freeze commit committer time (`git show -s --format='%ci' bbcc6dc2...`) = `2026-10-26 18:12:57 -0300` = 2026-10-26T21:12:57Z. frozen_at_utc precedes the commit time by 5 s.

## 6. v2 tool / replay tool / receipts absent at freeze bbcc6dc2 — PASS

`git ls-tree -r --name-only bbcc6dc2... | grep -E 'tools/(append-only-audit\.py|kama-live-replay\.py)$|\.ufo/waves/round-47/c2/live/'` returns only:

```
tools/append-only-audit.py
```

- `tools/append-only-audit.py` exists at freeze but is v1: 0 occurrences of v2 markers (`append-only-audit/v2|restored_max|restored_best`) at freeze vs 17 at build.
- `tools/kama-live-replay.py` not present at freeze (exists at build: blob 3773e62da07a9eaf9329be93c3c5c1f65415cc21).
- `.ufo/waves/round-47/c2/live/` receipts not present at freeze (no such tree paths).

## 7. Controls reproduce — PASS (no control mismatches)

Copied the committed controls dir to `$S/ctl`, then ran the builder from the copy (so receipts land beside it, in scratch):

```
TMPDIR=$S python3 $S/ctl/build_controls.py /home/vgpnk/Projects/shokunin/kama-shokunin $S/ctl
```

Builder output (summary lines) — identical to committed controls for all five:

```
base c1 selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False
base c2 receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=0 met=False
junk-c1-v1-contract c1 selftest=1 contract=0 lane=0 fixture=0 stable=0 files=84 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False
junk-c1-v1-numstat c1 selftest=0 contract=1 lane=0 fixture=0 stable=1 files=84 lane_events=5 lane_mismatch=4 fixture_mismatch=6 met=False
junk-c2-r46-relabel c2 receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=11 met=False
```

`diff` of regenerated vs committed `*.out`, excluding the by-construction `tip=` (fresh control commit hash) and `started=` (timestamp) lines:

- base.c1.out — NO DIFF
- base.c2.out — NO DIFF
- junk-c1-v1-contract.c1.out — NO DIFF
- junk-c2-r46-relabel.c2.out — NO DIFF
- junk-c1-v1-numstat.c1.out — differs only in the 6 `detail: fixture missing/unexpected ...` lines. These carry per-run random fixture commit hashes and line counts (`build_fixture` uses `os.urandom`, C1 docstring lines 78-88), so exact-line equality is impossible across runs. The mismatch *pattern* is structurally identical (3 missing + 3 unexpected, `fixture_mismatch=6`), and every deterministic detail (`selftest: exit=1 line=AOA_SELFTEST pass=8 fail=2`, all four `lane missing/unexpected` lines on the shared round-47 history, `exit=1`) matches byte-exact.

All five regenerated controls exit 1 with `met=False`, as committed.

## Defects

None found. The only diff observed (junk-c1-v1-numstat fixture detail lines) is the counter's own random fixture variance, not a control mismatch.

## Residual risk / verification gaps

- Fixture detail lines of junk-c1-v1-numstat were compared structurally (counts/statuses), not byte-exact, because C1's fixture content is randomized per run by design (docstring lines 78-88); the frozen control's summary verdict is unaffected.
- `predicate` equality is confirmed modulo whitespace wrapping inside the docstring source; content is byte-identical after normalization.

## Files written (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/preregistration.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/round47-append-audit-v2-check.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/round47-live-replay-audit.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/prereg-time-check.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/committed-controls/{base.c1.out,base.c2.out,junk-c1-v1-contract.c1.out,junk-c1-v1-numstat.c1.out,junk-c2-r46-relabel.c2.out}
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/R0Prereg/regenerated-controls/{same five .out files}
