# R0Prereg — round-46 freeze integrity

Verdict: **PASS — the freeze is intact.** Both preregistration predicate sentences equal the counters' docstring PREDICATE sentences word-for-word; both `counter_sha256` values and the builder hash equal `sha256sum` of the committed files at 5790944350ae41bfe2ce50934bba59e086e747f4 (working tree identical too); `freeze/prereg-time-check.out` shows `exit=0` / `RESULT pass`; all six control receipts reproduce (base pair byte-identical, junk quartet differing only in by-construction fields). Two low-severity observations, no defect in the frozen contract.

## 1. Predicate sentences (docstring vs preregistration)

Method: extracted the `PREDICATE (same sentence in the preregistration):` block from each counter's committed docstring (joined the wrapped lines), stripped the label, compared to the preregistration's `claims[].predicate` field.

- C1 `tools/round46-release-recheck-audit.py` docstring lines 82–86 vs prereg `claims[0].predicate`: **equal** (302 chars both).
- C2 `tools/round46-append-audit-check.py` docstring lines 61–65 vs prereg `claims[1].predicate`: **equal** (257 chars both).

C1 sentence (both copies): `every frozen population row re-verifies at b11906 from upstream bytes with a machine witness for every reworded, drifted or removed verdict, every drifted or removed row is flagged, SOURCES.md has a round-46 re-verification section and registers b11906; unverified=0 flags_missing=0 section=1 newrow=1.`
C2 sentence (both copies): `the append-only-audit capability runs at the measured commit, passes its selftest, matches an independent recomputation on a random fixture and on the lane's own history, and is entered in the SCORECARD capability table; selftest=1 fixture=1 lane=1 table=1.`

## 2. Counter and builder hashes at the freeze commit

`git -C <lane> show 5790944350ae41bfe2ce50934bba59e086e747f4:<path> | sha256sum`:

| file | committed sha256 | prereg field | match |
|---|---|---|---|
| tools/round46-release-recheck-audit.py | `502e6f57036fca803a081f844ea80f19e26c0dd782f329148d72b25b89861997` | C1 `counter_sha256` | yes |
| tools/round46-append-audit-check.py | `4dcfbe1063d600d103ebbccf1ac3008771a6962ae0dac9b91980b1e93ff3cb0a` | C2 `counter_sha256` | yes |
| .ufo/waves/round-46/controls/build_controls.py | `b4bf4799ea86266ce23cda4c6b78e7f314d55e1ef524a913ab5fcdbd22591d44` | `controls.builder` | yes |

Working-tree copies of all three hash identically to the committed ones (`git diff 57909443 -- .ufo/waves/round-46/ tools/round46-*.py` is empty for those paths), so nothing was touched after the freeze. `preregistration.json` itself is also identical between the freeze commit and the working tree.

## 3. prereg-time-check receipt

`.ufo/waves/round-46/freeze/prereg-time-check.out`: `rev=5790944350ae41bfe2ce50934bba59e086e747f4`, `committer_time=2026-10-26T16:50:10-03:00`, `ok line 6: 2026-10-26T19:50:02Z (at/before commit)`, `RESULT pass: no timestamp later than the committer time`, **`exit=0`**. The prereg's `frozen_at_utc` (19:50:02Z) is 8 s before the freeze commit's committer time (19:50:10Z), inside `max_future=86400`. Working-tree receipt is byte-identical to the copy committed at 4a2a4d55.

## 4. Controls reproduction

Ran from a scratch copy (`/fast/scratch/hyaku/kama-r46/R0Prereg/controls-copy`) with `TMPDIR=$S`:
`python3 ./build_controls.py /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r46/L1/llama.git $S/ctl` → **builder-exit=0**, 9.9 s.

Diff vs frozen `.ufo/waves/round-46/controls/*.out`:

- `base.c1.out`, `base.c2.out`: the builder does not regenerate these, so I re-ran both counters at base on a fresh `git clone --shared --no-checkout` scratch clone (toplevel asserted) — **byte-identical** to the frozen receipts, `tip=` included (`0163fea2…`). C1: `pop=91 rows=0 valid=0 unverified=91 … section=0 newrow=0 met=False`, exit 1. C2: `selftest=0 fixture=0 lane=0 table=0 … met=False`, exit 1, with the five lane events exactly as the prereg's C2 statement records them (0718b6ab LOG 2290/2290, QUALITY 375/375, README 663/663 restored by 82b5e9d3; 0718b6ab SCORECARD partial 2416/2417; dd9f5dc6 SCORECARD partial 24/31).
- `junk-c1-carryforward.c1.out`, `junk-c1-massreworded.c1.out`, `junk-c2-hardcoded.c2.out`: only line 1 (`tip=`) differs — by construction, each run commits fresh control SHAs. All summary numbers equal the frozen receipts and the prereg's `controls` block: carryforward `valid=71 unverified=20 met=False`; massreworded `valid=6 unverified=85 met=False`; hardcoded `selftest=1 fixture=0 lane=1 table=1 met=False`.
- `junk-c2-norestore.c2.out`: `tip=` differs plus the fixture commit SHAs embedded in the two `detail: fixture …` lines (the fixture content is `os.urandom`, so its commit SHAs change every run — also by construction). Event structure identical: `('…','LOG.md',25,0,'unrestored',None)` / `('…','LOG.md',30,0,'unrestored',None)`; `selftest=1 fixture=0 lane=0 table=1 met=False`.

All four junk controls read `met=False` with exactly the numbers the preregistration records. Reproduced receipts copied to `out/R0Prereg/` (see paths below).

## 5. Cross-checks that fell out of the reproduction

- **17-commit gap**: `git -C llama.git rev-list --count d854d98b..4d71b42f` = **17**; both tags resolve (`b11889` = d854d98bae598388ecea1ed84396587e5edc326d, `b11906` = 4d71b42fd87db24b8b7c808c151b713aa4459cfd). Matches the prereg's `release.observed`.
- **Population**: prereg `claims[0].population` (91 ids) equals the counter's derived population at base (91 ids, set-equal).
- **"18 population rows' files changed since b11889" verified from blobs**: the b11889 ledger has 91 rows (82 holds, 6 unchanged-file, 3 holds-reworded) on 16 distinct paths; exactly 2 paths differ b11889→b11906 (`tools/server/server-context.cpp`, `tools/server/server-models.cpp`), carrying **18** rows: the 17 carryforward-failed holds rows (S042 S060 S109 S114–S125 S133 S138) **plus S479**, whose pinned ranges survived the change text-equal (its carried holds row is valid at b11906 — that is why the carryforward scores valid=71 = 6 unchanged + 65 holds). The 3 holds-reworded rows (S037 S043 S108) sit on `tools/server/server.cpp`, byte-identical b11889→b11906, and fail carryforward only on the witness rule. So the wave brief's "71 rows' files are byte-identical / 20 rows need reading" is a loose paraphrase (73 rows sit on byte-identical paths; the changed-path row set is 18 including mechanically-re-verifiable S479) — the **prereg's own numbers are correct**.
- **Ancestry**: base 0163fea2 is an ancestor of the freeze commit; the freeze commit is an ancestor of 4a2a4d55 (where the receipt and the C2 tool landed).

## Findings

No defect in the frozen preregistration, counters, or controls. Two observations:

1. **[low, wording] `routed.r45-D2` says the prereg-time-check receipt was "committed with this preregistration"**, but `freeze/prereg-time-check.out` is absent from the freeze commit 57909443 (`git cat-file -e 57909443:.ufo/waves/round-46/freeze/prereg-time-check.out` → fatal: exists on disk, but not in '57909443') and landed in the next commit 4a2a4d55. Structurally unavoidable — the receipt cites `rev=57909443`, so it cannot be contained in that commit — and the check itself is sound (it validates the prereg timestamp against the freeze commit's committer time). No fix needed beyond awareness; a future prereg could phrase it "committed immediately after the freeze commit".
2. **[info] Wave-brief paraphrase imprecision** (not a frozen artifact): "71 rows' files are byte-identical" should be 73 rows on byte-identical paths (71 carry forward validly + S037/S043/S108 which fail only for lack of witnesses), and the 20-row reading list omits S479, the 18th changed-path row, whose carried `holds` verdict re-derives mechanically at b11906 (proved by the carryforward control). The prereg's `release.observed` ("18 population rows' files changed") is exact.

Residual risk: none in scope. The fragment checker (`check-fragment.py`) and the live b11906 ledger are other seats' deliverables and were not audited here. No tools were installed or upgraded (none needed); no pacman transactions run.

Scratch `/fast/scratch/hyaku/kama-r46/R0Prereg` removed after evidence copy.
