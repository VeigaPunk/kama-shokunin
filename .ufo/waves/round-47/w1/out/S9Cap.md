**Verdict: the round-47 canonical capability list is drafted and measured — 11 rows (10 existing + `live-receipt-replay`, `append-only-audit` reworded for v2 with first-working round still 46) and, on a scratch clone at `3a09a1d9` with the draft applied, `python3 tools/capability-repertoire-audit.py` reports `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (exit 0), in working-tree and `--tip` mode alike; the head mirror and four companion edits it forces are drafted and measured too.**

# S9Cap — round-47 canonical capability entries

Lane: kama. Wave `.ufo/waves/round-47/w1` (attack + frontier). Seat: S9Cap, scribe, leaf.
Revision under test: build commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (clone HEAD
`46a924e0`, one commit later). Lane tree was never written by this seat; every edit lived in
`/fast/scratch/hyaku/kama-r47/S9Cap/lane` (`git clone --shared`).

## 1. What the integrator lands

1. **Canonical block** — `canonical-round-47.md` (verbatim). Marker
   `**Capabilities — canonical list as of round 47**` plus a four-column table. Placement is
   settled with S9Scorecard: the block is carried **inside** `## Round 47` (round-46 shape), after
   the claim/controls prose; this seat's file shows it before the heading, which measures the same
   `caps=0` and is therefore cosmetic. Apply it **once** — applying both `proposed.patch` and the
   section draft would leave two markers (`capability_tables` 14 instead of 13). Two rows change
   relative to round 46:
   - `append-only-audit` (first-working **46**, unchanged): "Set the lane's contract-declared
     append-only self-description - the paths and patterns `registry/append-only-contract.tsv`
     names, each row pointing at the lane line that declares the rule - … deleted count equal to
     `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost) … the largest share of
     those lines any commit in the event's own window holds again (a multiset maximum, so a later
     head re-anchor cannot lower it) … exit 1 on a partial or unrestored mass deletion", evidence
     `tools/append-only-audit.py`; `registry/append-only-contract.tsv`;
     `tools/round47-append-audit-v2-check.py`.
   - `live-receipt-replay` (first-working **47**): "Re-acquire a `kama-llamacpp-live/v4` receipt's
     server release archive and model from the URLs its provenance block records, verify both
     sha256 values before anything is extracted or executed, re-run the lifecycle from an empty
     home and compare every check the original evaluated, and refuse a receipt whose provenance is
     missing, whose recorded digest does not match what it downloads, or whose server-archive
     member is unsafe", evidence `tools/kama-live-replay.py`;
     `.ufo/waves/round-47/c2/live/receipt-1.json`.
   The other nine rows are copied byte-for-byte from the round-46 table, which itself stays
   byte-intact (`SCORECARD.md:2448` at the tip).
2. **Head mirror** — `mirror-capabilities.md`: `## Capabilities` (`SCORECARD.md:115`) prose says
   round-47 and its table carries the same 11 rows. Required: the reconcile tool's `caps` leg
   compares the head name set with the canonical one (`tools/round42-selfdesc-reconcile.py:224`).
3. **Forced head/PROVINCE edits** — `companion-head-and-province.md`:
   `SCORECARD.md:57` "10 capabilities" → 11; `SCORECARD.md:136` first-working rounds gain `47` and
   "entered in round 46" → round 47; `PROVINCE.md:17` instrument row rewritten (contract +
   round-47 check tool + `kama-live-replay`, dropping the stale "five files" wording); and
   `SCORECARD.md:17` (`## Axes` coverage row) re-anchored `PROVINCE.md` sha256
   `659a5101…` → `929f3e3e…` (line count unchanged at 186).
4. **`proposed.patch`** — the same combined diff, `2 files changed, 24 insertions(+), 6 deletions(-)`
   (`patch -p1 -d kama-shokunin < proposed.patch`; the clone emits `i/`…`w/` prefixes).

## 2. Measurement

Commands ran in `/fast/scratch/hyaku/kama-r47/S9Cap/lane` unless stated; Python 3.14.8, git 2.56.0.

| # | command | exit | output |
|---|---|---|---|
| 1 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 3a09a1d9 --out caps-baseline.json` | 0 | `listed 10 observed 10 missing 0 unsubstantiated 0 met True` (`canonical_line 2452`) |
| 2 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --out caps-after.json` (draft applied) | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (`canonical_line 2687`, marker at 2683, `capability_tables 13`) |
| 3 | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 81d0ebb4 --out caps-tip-committed.json` (synthetic commit holding the draft) | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| 4 | `python3 tools/capability-repertoire-audit.py --selftest` | 0 | `CAP_SELFTEST pass=2 fail=0` |
| 5 | per-row `path_exists(repo, 3a09a1d9, token)` for all 11 rows | n/a | `all_rows_substantiated_at_tip True` (each row listed with its tokens) |
| 6 | `python3 tools/round42-selfdesc-reconcile.py --repo $S/lane --tip 81d0ebb4` | 1 | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1` — the single r41 miss is the stale calibration row (`32` vs 33 blobs, see §4) |
| 7 | `python3 tools/append-only-audit.py --repo $S/lane --to 3a09a1d9` | 1 | `SCORECARD 31/24 partial`, `LOG 2292/2292 restored`, `SCORECARD 2421/2420 partial`, `QUALITY 375/375 restored`, `README 663/663 restored`, `summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0` |

Row 1 (`baseline`) is the honest base: the tip already reports `10/10 met True`, i.e. nothing at
the tip forces a round-47 entry — the new row exists because the round demonstrated it, not because
a counter demanded it.

### Controls (constructed trees, `evaluate(dir, None)`)

| case | rc | line |
|---|---|---|
| draft applied, all evidence paths present | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| canonical row's only pointer dead | 1 | `… unsubstantiated 1 met False` |
| both pointers of the new row dead | 1 | `… unsubstantiated 1 met False` |
| tool pointer dead, receipt pointer alive (`dead-tool-live-receipt`) | 0 | `… unsubstantiated 0 met True` |
| new row removed from the canonical table only (mirror keeps it) | 1 | `listed 10 observed 11 missing 1 … met False` |
| round-47 marker removed (round-46 table becomes canonical) | 1 | `listed 10 observed 11 missing 1 … met False` |
| marker present, table absent | 1 | `listed 10 observed 11 missing 1 … met False` |

### Companion edits are load-bearing (measured, not asserted)

| omission | reconcile output | exit |
|---|---|---|
| none | `mismatches=1` (r41 only) | 1 |
| `PROVINCE.md:17` left alone (variant `99667497`) | `province=3 … mismatches=4`; names `registry/append-only-contract.tsv`, `tools/round47-append-audit-v2-check.py`, `tools/kama-live-replay.py` | 1 |
| PROVINCE edited, coverage hash not re-anchored (variant `0c661cf3`) | `r41=2 … mismatches=2`; `coverage sha256 PROVINCE.md cited 659a5101… observed 929f3e3e…` | 1 |
| canonical block added, mirror/§Retired/§Saturation left at round 46 (variant `ae7e2801`) | `retired=1 saturation=1 caps=1 … mismatches=4` | 1 |

Variants are unreferenced `commit-tree` objects in the scratch clone built from a temporary
`GIT_INDEX_FILE`; no ref, branch or normal index was touched, and `git rev-parse --show-toplevel`
was asserted before the first of them.

## 3. Grounding of the two changed rows

- `append-only-audit` v2 wording follows `tools/append-only-audit.py:1-34`: contract file and
  `declared_at` rows, deleted counts from the `-U0` hunk headers equal to `--numstat`, `held(x)`,
  `window`, `restored_max`, `status` classes, exit map. My own run (row 7 above) reproduces the
  round's figures independently of the L1 dry run: `2421/2420` and `2292/2292`, `files=85`,
  `events=5`, `restored=3 partial=2 unrestored=0`, exit 1. `--`-prefixed lines are now counted
  (`deleted=2421` here vs the v1 undercount of 2417 that round-46 closure D1 reports).
- `live-receipt-replay` wording follows `tools/kama-live-replay.py:1-24` and its refusal sites:
  `:71` not-a-v4 receipt, `:77` provenance-missing, `:80`/`:82` bad provenance digests,
  `:85` unsafe member, `:94` download digest mismatch, `:108`/`:163-164` the check-by-check
  comparison. First-working 47 is grounded on the tool entering the tree in the round-47 build:
  `git show --stat 3a09a1d9` lists `tools/kama-live-replay.py | 267 +`, `registry` untouched by
  that commit's SCORECARD (not in its file list), matching the round's own statement that the
  capability is new this round.

## 4. Findings and limits (instruments are frozen; nothing here was fixed in place)

1. **`unsubstantiated` is satisfied by any one resolving token.** `tools/capability-repertoire-audit.py:148`
   (`if not any(path_exists(root, rev, t) for t in tokens)`). With two pointers per row a dead
   primary pointer is invisible while the second resolves: control `dead-tool-live-receipt` (tool
   pointer dead, receipt pointer alive) reports `unsubstantiated 0 met True`, whereas killing both
   reports `unsubstantiated 1 met False`. Not a contract breach (the docstring says "carries no
   repo-relative path token that resolves"), but an integrator wanting the tool pointer to be
   load-bearing must keep one pointer per row. Proposed strengthening, if wanted: require the
   first token (or every `tools/`/`registry/` token) to resolve; that is a round-48 instrument
   change, not a round-47 edit.
2. **Placement couples the marker to its table.** Canonical selection is "first capability-shaped
   table after the highest marker" (`tools/capability-repertoire-audit.py:127-136`, fallback
   `:135`). Any 4-column table with a `First working round` header landing between the marker and
   the table silently becomes canonical (measured: marker-without-table control returns 2's
   predecessor path and reports `listed 10 observed 11 missing 1`). The block therefore keeps them
   adjacent; §Round 47 (S9Scorecard) must be placed after the block, not between marker and table.
3. **The audit cannot force a new capability into the repertoire.** It compares canonical names
   with the union of names already in the file (`:150-155`); a capability absent from *every* table
   is invisible, and the tip is green (`10/10`) before the round-47 row exists. The only forcing
   leg is `unsubstantiated`, weakened per finding 1. Stated so the entry is read as a demonstration,
   not a counter verdict.
4. **A `PROVINCE.md` edit in round 47 also re-anchors `## Axes` coverage.** The coverage row cites
   the file's sha256 (`SCORECARD.md:17`), so any PROVINCE edit without the re-anchor turns
   `round42-selfdesc-reconcile` r41 from 1 to 2 (measured). Land both in one commit.
5. **The `r41=1` I first read as "pre-existing" is a real, round-47-repairable stale row.**
   `SCORECARD.md:18` (calibration) claims `corpus/lessons/*verifier-spotcheck.md` → `32`; the tree
   holds **33** at both `3a09a1d9` and `46a924e0`
   (`git ls-tree --name-only <rev> corpus/lessons/ | grep -c 'verifier-spotcheck\.md$'` → 33; round-46
   closure added `round-46-verifier-spotcheck.md`). The canon list does not own that line, the
   §Round 47 head re-anchor does; `S9Scorecard` carries it as `32` → `33`. Correction to my first
   report: this is not an unrelated red — it is one of the head moves the round owes.

6. **Two more head moves become necessary only once `## Round 47` exists** (and are therefore absent
   from my demo tree, whose `maxN` stays 46): `SCORECARD.md:6` `Current authority (round 46)` → 47
   and `Latest measured round: 46.` → 47 (banner leg), and `SCORECARD.md:53` live-plan pointer
   `### Planned (round 47)` → `### Planned (round 48)` with a `### Planned (round 48)` heading and a
   numbered item (planned leg = `maxN+1`). Owned by the section/head draft, not by the canon list.

## 5. Advisory observation (not mine to change)

The lane working tree is dirty with other seats' in-flight work — reported verbatim:
`M SKILL.md`, `M corpus/QUALITY.md`, `M corpus/README.md`, `M corpus/SOURCES.md`,
`M tests/llamacpp-live/check-receipt.py`, `M tools/append-only-audit.py`,
`M tools/gguf-identity.py`, `M tools/kama-live-replay.py`,
`?? .ufo/waves/round-47/c2/x0-digest-rehash.txt`, `?? .ufo/waves/round-47/hexrun-evidence/`,
`?? .ufo/waves/round-47/w1.ready`, `?? .ufo/waves/round-47/w1.ready.dispatched`,
`?? .ufo/waves/round-47/w1/out/`. `SCORECARD.md` and `PROVINCE.md` are clean at HEAD. My
measurements used committed bytes (`--shared` clone) and are unaffected, but three of the modified
paths are build-commit artifacts (`tools/append-only-audit.py`, `tools/kama-live-replay.py`,
`tools/gguf-identity.py`): an integration measurement run in that working tree would not be
measuring `3a09a1d9`.

## 6. Out of scope / not claimed

- No lane file, index, ref or jj state was written; no `git add/commit/checkout/stash/reset` in the
  lane; the only commits are unreferenced objects in the scratch clone.
- C1 (`round47-append-audit-v2-check.py`) and C2 (`round47-live-replay-audit.py`) were **not** run
  by this seat; the L1 dry-run values quoted in the seat brief are not restated as my evidence. The
  one counter-adjacent run I did make is `tools/append-only-audit.py` itself (row 7), read-only.
- §Round 47 section body, LOG, QUALITY, README, SKILL registry rows and PROVINCE notes are other
  seats' deliverables; I drafted only the entries and the edits they force.
- No tool installs or upgrades (nothing was needed; all pacman transactions stay paused).

## 7. Merge with S9Scorecard (received after the first measurement)

S9Scorecard adopted the canon verbatim and carries it inside `## Round 47`. Its merged measurement
(commit `1d9102972faf84d38ee0a78e37ded85193ad040c` = base `46a924e0` + section + head moves):
`round42-selfdesc-reconcile` `r41=0 … mismatches=0 maxN=47 met=True` (exit 0),
`round41-scorecard-reconcile` `mismatches=0 met=True`, `planned-pointer-check.py` `met=True`.
Its section-only variant `7ba2c796` reads `mismatches=9` = `r41 1 + banner 1 + planned 1 +
retired 1 + saturation 1 + caps 1 + province 3` — the retired/saturation/caps and province-3
components reproduce this seat's omission controls exactly; the three head moves are the ones my
list does not own.

Verified here, independently: 33 `corpus/lessons/*verifier-spotcheck.md` blobs at **both**
`3a09a1d9` and `46a924e0` (row claims 32), and the edited `PROVINCE.md` blob hashes to
`929f3e3e…` (both seats agree). Consequences recorded in `companion-head-and-province.md`:
the calibration row is a round-47 repair (`32` → `33`), and banner/Planned moves are needed once
`## Round 47` exists. Placement is settled (block inside the section); apply the block once.

One further head move is live but **not forced by the canon list** (S9Scorecard raised it, numbers
re-measured here): `SCORECARD.md:16` `depth` row anchors `SKILL.md`. Committed tip `46a924e0`:
sha256 `1ad95066…`, 1442 lines, `grep -c '^## '` → 34 — the row is correct there. The round-47
SKILL registry rows sit uncommitted in the lane working tree at sha256 `ddb80f6e…`, 1463 lines,
35 headings; when they land, the depth row's hash, line count and run fact must all three move or
`round41-scorecard-reconcile` reads `hash_bad=1 lines_bad=1 run_bad=1`. Re-derive from the applied
blob at integration, not from these working-tree figures.

## 8. Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/canonical-round-47.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/mirror-capabilities.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/companion-head-and-province.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/proposed.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/receipt.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/caps-baseline.{out,json}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/caps-after.{out,json}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/caps-tip-committed.{out,json}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/caps-tip-tokens.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/caps-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/controls.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/selfdesc-baseline.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/selfdesc-good.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/selfdesc-variant-no-province.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/selfdesc-variant-no-anchor.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/selfdesc-variant-no-mirror.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Cap/append-only-v2-at-tip.out`
