# RV01C1Attack — attack report: the C1 counter and its corrections (round-81 w1)

Seat: RV01C1Attack (reviewer, kama r81 w1). Item: attack `tools/round81-selfrecord-round80.py`
against frozen claim C1 (`plans/round-81-claims.md` §C1; block quote, fact table and controls treated
as frozen text). Judged on: calibration.

**Verdict: 9/9 attacks CAUGHT, 0 escaped.** The counter survives every named attack class. No
high- or medium-severity finding. Four info-severity hardening notes below, none with live effect at
the graded revisions.

Revisions pinned: base `e7d2fd729cf8204c89c32534303bc9f2a97fcee4`, sealed
`a2af1af59faf6cf66fe854559293c4e4b441aff3`, tip `1b96317f690dbe9f42675099a004e150aaa54419`
(lane master moved 2c1faed0 → 1b96317f while this seat ran; every run pins `--tip`, matching the
`# rev:` header the L1 recorded in its own receipts).

## Findings by severity

### High / Medium

None. Every attack the item named is caught at the exact boundary the frozen counter rule demands.

### Info (hardening notes, no live effect — each verified non-exploitable at the graded revisions)

- **N1 — the predicate's "matches the same fact re-derived at the tip" clause is enforced as a
  sealed-revision observation for F1–F5.** `f1`–`f5` take only `rev` and read both the declared row
  and the witness receipt at that revision; `score()` calls `derive(repo, sealed, tip)`
  (`tools/round81-selfrecord-round80.py:158-220, 277-278`), so the correction's `new` is checked
  against the *sealed* receipt observation, never a tip re-derivation. Consequence-free today: the
  receipt blobs are byte-identical between sealed and tip (verified:
  `git diff --stat a2af1af5 1b96317f -- .ufo/waves/round-80/measured/after/` is empty) and that area
  is append-only-guarded. It is a divergence from the frozen predicate text only under a hypothetical
  receipt mutation that the append-only rule already forbids.
- **N2 — `section()` prefix matching is loose.** `inside = line[3:].strip().startswith(prefix)`
  (`:117-126`): a heading like `## Corrections-archive` would be joined into the correction container
  alongside `## Corrections`, and blocks under it would count. The committed
  `corpus/lessons/round-81.md` has exactly one `## Corrections` and one `## Mistakes`, so no block
  can hide this way today; A1 confirms `## Mistakes` is excluded.
- **N3 — `marked_section()` does not stop at `###` headings** (`:129-139` breaks only on `## `/`#### `):
  content in a `###`-level section below the `#### round-81 correction` block stays inside the marker
  haystack, so a marker string in lower-level prose after the block would still satisfy the
  "named by the appended record block" rule. The tip block is well-formed (all five markers inside the
  block itself), so no live effect.
- **N4 — "newest" closure is newest by committer date, not round number.** `Repo.newest_closure`
  maximizes `(commit time, path)` over the tip tree (`:90-99`); a backdated or misnumbered
  `round-*-verifier-spotcheck.md` could outrank a higher-numbered one. This is a defensible reading of
  "the newest non-author closure is …" in present tense and matches the tip state; note only.

## Attack table

| # | Case | Vector | Observed vs expected | Verdict | Deciding lines |
|---|---|---|---|---|---|
| A0 | baseline equivalence (control) | CLI pinned-tip run + harness on real blobs | green line byte-equal to L1 `c1-green.out`; harness identical | caught | `:509-517` |
| A1 | correction block refiled under `## Mistakes` | harness, real tip lesson blob | F1 unanswered (`mismatches=1`, `corrected=5`, `no-correction`); block not parsed at all | caught | `:266-274, 117-126, 284-289` |
| A2a | `new=c1-selftest=pass=99` does not re-derive | harness | `unbacked=1`: `new=… != observed c1-selftest=pass=11` | caught | `:295-296` |
| A2b | `at=` names the tip instead of the sealed revision | harness | `unbacked=1`: `at=1b96317f… != sealed a2af1af…` | caught | `:297-298` |
| A3 | `old=c1-selftest=pass=7` ≠ sealed declared value | harness | `unbacked=1`: `old=… != declared c1-selftest=pass=9` | caught | `:293-294` |
| A4a | worktree-only plant: SCORECARD marker bullets deleted | CLI over scratch clone (` M SCORECARD.md`) | verdict byte-identical, exit 0 | caught | `:82-88, 303` |
| A4b | worktree-only plants: LOG marker + lessons F1 block deleted | CLI over scratch clone (3 files ` M`) | verdict byte-identical, exit 0 — the "scratch copy of the tip" vector is closed by the same git-show binding | caught | `:267, 303` |
| A5 | F6 tip-bound while F1–F5 sealed-bound, and stated | CLI `--json` at tip, `--enumerate` at base, harness round-79-only closure | F6 declared round-79 observed round-80 at tip; still stale at base; F6 correction flips unbacked when tip closure is round-79; stated at `:27-28`, `:251`, lessons "Freeze divergences" 1 | caught | `:224-236, 90-99, 254-258` |
| A6a | `--no-corrections` at tip | CLI | `SELFRECORD_R80 claims=6 mismatches=6 corrected=0 unbacked=0`, exit 1 (= frozen control 2) | caught | `:482, 279, 509-517` |
| A6b | `--enumerate` at base | CLI `--tip e7d2fd72…` | `SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0`, exit 1 (= frozen control 1) | caught | `:501-508` |

Method note (why A1–A3 ran in-process): mutating the committed lesson requires a commit — forbidden
for this seat — and the CLI peels `--tip` with `^{commit}` (`:492-493`), so no tree-sha injection
exists. The attacks drive the production `score()/derive()/corrections()` over real sealed/tip lane
blobs through the counter's own `Fixture` boundary (`:108-114`), the same boundary its `--selftest`
exercises (`--selftest` independently: `pass=13 fail=0`, exit 0). Attack 4 proves at the CLI that
nothing but `git show <rev>:<path>` feeds that boundary, for facts, corrections and record markers
alike.

## Receipts (absolute paths in this seat dir; each with command and exit code)

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/RV01C1Attack/receipts/`;
`CTR` = `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-selfrecord-round80.py`,
`D` = scratch shared clone of the lane, `TIP` = `1b96317f690dbe9f42675099a004e150aaa54419`,
`BASE` = `e7d2fd729cf8204c89c32534303bc9f2a97fcee4`.

- `cli-baseline.out` — `python3 $CTR --repo $D --tip $TIP` → `SELFRECORD_R80 claims=6 mismatches=0 corrected=6 unbacked=0`, exit 0
- `cli-baseline.json` — same + `--json` → facts+summary JSON, exit 0
- `cli-nocorr.out` — `python3 $CTR --repo $D --tip $TIP --no-corrections` → `mismatches=6` + 6×UNANSWERED, exit 1
- `cli-enum-base.out` — `python3 $CTR --repo $D --tip $BASE --enumerate` → `SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0` + 6×STALE, exit 1
- `selftest.out` — `python3 $CTR --selftest` → `SELFRECORD_R80_SELFTEST pass=13 fail=0`, exit 0
- `wt-0.out` — pristine clone run, exit 0 (clone worktree clean: 0 porcelain lines)
- `wt-1-scorecard-plant.out` — after uncommitted SCORECARD plant, exit 0; `diff wt-0.out` empty
- `wt-2-all-plants.out` — after SCORECARD+LOG+lessons plants, exit 0; `diff wt-0.out` empty
- `parser-attacks.json` — harness ledger, 6 cases all CAUGHT, exit 0 (source kept as `../attack-parser.py`)

The three CLI green/red lines reproduce the L1's committed receipts
(`.ufo/waves/round-81/measured/after/c1-green.out`, `…/control/c1-no-corrections.out`,
`…/before/c1-enum.out`) line-for-line at the same pinned revision.

## Residual risk and verification gaps

- The only untested edge for A1–A3 is git's own `show rev:path` (the Fixture↔Repo boundary):
  unreachable without a commit, which the VCS rules forbid this seat. Everything above that edge is
  attacked directly and caught.
- The lane tip kept moving while this seat ran (L1 commits at 08:47–08:57+). All runs pin `--tip`; a
  future tip move could only change C1's verdict if the graded inputs moved — sealed blobs and the
  round-80 receipt blobs are append-only and verified byte-identical sealed↔tip, and F6's closure set
  only grows.
- N1–N4 above are hardening notes only; none is reachable at the graded revisions.
- F1's true post-hardening tally (`pass=11`) is taken from the cited receipt
  (`.ufo/waves/round-80/measured/after/c1-selftest.out`, `SELFRECORD_R79_SELFTEST pass=11 fail=0`),
  not re-executed — the frozen predicate grades the record against its witness, which is what the
  counter implements.

Tooling: none installed or upgraded (no need); all work read-only against the lane plus a
`git clone --shared` fixture and one in-process harness under `/fast/scratch/hyaku/kama-r81/RV01C1Attack/`
(deleted after receipt copy, per scratch rule). No lane file was modified; no git write ran anywhere.
