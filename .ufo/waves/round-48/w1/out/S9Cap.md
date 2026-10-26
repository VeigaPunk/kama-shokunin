**Verdict: the round-48 capability draft is ready to land: 11 rows, two reworded, capability census `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (exit 0) at `380bcdff` + the draft, two controls red, and the self-description reconcile unchanged from its base state.**

# Seat S9Cap — round-48 capability entries

Deliverables sit in `.ufo/waves/round-48/w1/out/S9Cap/`. Nothing in the lane was written;
the draft was applied to one scratch clone `git clone --shared` of the lane, detached at
`380bcdff9c8af06997c482f6eb03db926a794a2b`, and committed there as
`c2dede9fa3ea440062d7d6a8d7c2981ff26d2830` (parent = the build commit). That clone is
deleted; every output it produced is kept beside this report.

## What the draft says

`round48-canonical-block.md` (17 lines) is the block to append at the end of `SCORECARD.md`
— after the `### Superseded head banners (kept verbatim; round 48)` block the build
added, which is where the file ends today:

- `round48-canonical-block.md:1` — `**Capabilities — canonical list as of round 48**`, the
  marker `tools/capability-repertoire-audit.py:48` resolves.
- `:3` — the note: same four columns, the round-47 table stays byte-intact, **no row added**,
  two rows reworded for the tools the build landed, first-working rounds unchanged.
- `:5-17` — 11 rows, rounds `10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47` (11 → 11).
- `:16` — `append-only-audit` reworded for **v3**: the per-row `region` cell (`*`,
  `exempt=` `## ` sections that stay ungraded while their line count's window maximum is not
  below the parent's, a single `only=` section), declarations that must **bind** (the
  declared_at line says append-only for that path and is not a negation; an exempt pointer
  names the line that declares those titles re-derived; an `only=` pointer names its prefix),
  the >= 20-line / `git diff --numstat` event set, the multiset maximum over the event's own
  window, and **`regressed`** in the exit semantics. Evidence: `tools/append-only-audit.py`;
  `registry/append-only-contract.tsv`; `tools/round48-append-audit-v3-check.py`. Stays 46.
- `:17` — `live-receipt-replay` reworded for **v5**: https provenance URLs, the model pinned
  to a 40-hex `/resolve/<commit>/` revision also stated as `provenance.model.commit`, the
  archive and its member hashed against the asset and server digests **before the server
  starts** so `provenance.verified` is recorded not asserted, the rerun from an empty home
  passing `--server-archive`, a **stable-projection** comparison of the captured surfaces
  (props, slots, health, models, metrics, loading, teardown, ownership), the three refusal
  classes, and `--compare A B` without the network. Evidence: `tools/kama-live-replay.py`;
  `tools/kama-llamacpp-live.py`; `.ufo/waves/round-48/c2/live/receipt-1.json` (present at the
  tip: `git ls-tree -r --name-only 380bcdff` lists all three receipts). Stays 47.
- Words checked against the tools' own docstrings: `tools/append-only-audit.py:4-35`
  (region/eligibility/`regressed`/`binds()`), `tools/kama-llamacpp-live.py:30-44` (v5 flags,
  `--server-archive`, `provenance.model.commit`, `provenance.verified`),
  `tools/kama-live-replay.py:5-30` (stable projection, `--compare`, exit codes). Every v5
  receipt is `schema kama-llamacpp-live/v5`, `outcome pass`, `model.commit 499bc882…`,
  `verified.at record`.

**Mirror rows for `SCORECARD.md ## Capabilities`** — `proposed-SCORECARD.diff` hunks
`@@ -115` and `@@ -128`: the intro at `SCORECARD.md:117` becomes "Mirror of the round-48
canonical capability list that §Round 48 carries …", and the two rows at `SCORECARD.md:130`
(`append-only-audit`) and `:131` (`live-receipt-replay`) are replaced by the canonical rows
byte-for-byte. The historical and earlier-round tables keep their bytes (the head section is
located by heading, never by line number; a name-keyed rewrite of the whole file touched 14
rows, which is why `draft-apply.py` bounds the edit to the head section).

One collateral edit the draft must carry: `round42-selfdesc-reconcile.py`'s `province` fact
(`tools/round42-selfdesc-reconcile.py:47-48`, `:257-263`) requires every `tools/` token a
canonical row cites to appear in `PROVINCE.md`, and `PROVINCE.md` does not name
`tools/round48-append-audit-v3-check.py`. `proposed-PROVINCE.diff` adds it to the Owns-table
cell (and the v3 clause). Because the round-41 counter pins `PROVINCE.md`'s sha256 in the head
`## Axes` coverage row, the same draft updates that digest
(`SCORECARD.md:17`: `929f3e3e…` → `aa7915a8590d9180ac559864897679ecb532a3c5b6595f58a4d19a5491e5d67d`,
line count 186 unchanged; hunk `@@ -15`). Alternative for the L1 without the extra two
edits: drop `tools/round48-append-audit-v3-check.py` from row `:16` — then `province` and the
digest stay untouched (nothing else in the row needs `PROVINCE.md`).

## Evidence (all commands in `evidence.txt`; outputs beside it)

| Gate | Command | Result |
|---|---|---|
| capability census, base | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 380bcdff…` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`baseline-audit.json`) |
| capability census, draft | same at `--tip c2dede9f…` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 (`after-audit.out`, `after-audit.json`: `canonical_line 2748`, `capability_tables 14`) |
| census selftest | `… --selftest` | `CAP_SELFTEST pass=2 fail=0`, exit 0 |
| table shape | audit's own parser over the draft | 14 tables, canonical 11 rows, every row 4 cells, `mirror_names_equal True`, `mirror_rows_identical True` |
| control B (name) | canonical row renamed to `append-only-audit-v3` | `observed 12 missing 1 met False`, exit 1 (`controls.out`) |
| control C (evidence) | one row's evidence cell names only missing files | `unsubstantiated 1 met False`, exit 1 |
| self-description | `python3 tools/round42-selfdesc-reconcile.py --tip <base>` / `--tip <draft>` | both `mismatches=1 maxN=47 met=False`; the one detail both times is the pre-existing r41 spot-check-count item (`reconcile-before.out`, `reconcile-after.out`). `province=0`, `caps=0`, `saturation=0`, `retired=0` at the draft |

## The draft on the lane's current working tree

The lane working tree moved while this seat ran (siblings' in-flight edits, `git diff
380bcdff` = `SCORECARD.md` head banner to "Current authority (round 48)", the calibration-run
cell, the round-47 banner appended at EOF; plus `SKILL.md` and
`tests/llamacpp-live/check-receipt.py`). So the draft was applied a second time on a clone
snapshot of that tree (`b85783e8` + the lane's uncommitted `SCORECARD.md`/`PROVINCE.md`):

| Tip | Census | Reconcile |
|---|---|---|
| `ebc80f58` — sibling edits, no draft | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 | `r41=0 banner=1 … province=0 mismatches=1 met=False`, detail `banner: head lacks 'Latest measured round: 47'` |
| `3e588fba` — sibling edits + this draft | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0 | identical: `mismatches=1`, the same `banner` detail, `province=0`, `caps=0` |

So the draft adds nothing to the reconcile on the live tree either, and the one item there is
the siblings' own in-flight banner (`SCORECARD.md` head says "Current authority (round 48)"
while `Latest measured round` is 47 — `maxN=47` until a round-48 section exists). Because the
tail and head have both moved, the four edits should be applied **by content**, not by
`git apply` against `proposed-SCORECARD.diff` (that diff is against the build commit); the
canonical block is appended at EOF, after the superseded-banner section. The current-tree
before/after artifacts carry the same diffs regenerated from that tree.

## Findings

**F1 (census limit, disclosed — the round's own gate is weaker than it reads).**
`tools/capability-repertoire-audit.py:148` is `if not any(path_exists(root, rev, t) for t in
tokens)`, so a canonical row is substantiated by **one** live path token even when the rest of
its evidence cell is dead. Shown by control A (`make-controls.py`, `0b0921c5` at the final base): appending `-missing` to the counter's name inside `append-only-audit`'s cell leaves
`unsubstantiated 0 met True exit 0` (`controls.out`, `== ctlA`). Control C is the red control
that actually exercises the leg. Proposed fix (not applied; needs its own round and a
re-measure, and it would first need the historical rows checked): require every `tools/` and
`registry/` token in a canonical row's evidence cell to resolve — `all(...)` over that subset,
keeping `any(...)` for other tokens — and add a selftest arm with one dead pointer beside live
ones.

**F2 (coupling the L1 must land together).** One canonical evidence token binds two other
surfaces: `PROVINCE.md` (`province` fact) and `PROVINCE.md`'s sha256 in the head `## Axes`
coverage row (`r41` hash fact). Split the draft — rows without the `PROVINCE.md` edit — and the
reconcile goes `mismatches=2` (observed: `r41 coverage sha256 PROVINCE.md cited 929f3e3e…
observed aa7915a8…`, plus `province: PROVINCE.md lacks tools/round48-append-audit-v3-check.py`).
Both edits are in the proposal, so the composite is at the base state. Not a defect in a
counter: it is the declared design of `tools/round42-selfdesc-reconcile.py:47-48`.

**F3 (placement, informational).** The block carries no `## ` heading, so C1 v3's SCORECARD
`exempt=` region — the five `## ` titles `SCORECARD.md:6` declares re-derived — does not cover
it; the appended lines are graded and live in the last `## ` section (`## Round 47`). This is
correct and consistent with rounds 41-47 (each round appends a new table; none rewrites the
previous one), and appending creates no deletion event. Two mechanical constraints for the
integration: the block must sit **after** the round-47 marker (the census takes the first
capability table after the highest marker, `tools/capability-repertoire-audit.py:129-135`), and
it must be appended rather than inserted between the round-47 marker and its table.

## Out of scope / not done

- No counter, preregistration or control was edited; no lane file was touched; no lane git or
  jj state was mutated; no tool was installed; nothing was committed, pushed or published.
- Scores are not restated as moved: capabilities stay 11 → 11 and the `## Saturation` paragraph
  is left untouched — verified correct, not assumed (`saturation=0` at the draft, and the
  first-working-round list it states is unchanged).
- The two other known integration items in the brief (gate registry listing the two round-48
  counters, hexrun `d0012618`) were not re-checked here and are not re-reported.
- The measured-commit placement is the L1's: this draft claims no measurement, only that the
  census and the reconcile hold at the build commit plus this edit.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/round48-canonical-block.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/proposed-SCORECARD.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/proposed-PROVINCE.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/SCORECARD.md.proposed`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/PROVINCE.md.proposed`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/evidence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/baseline-audit.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/after-audit.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/after-audit.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/controls.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/control-shas.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/reconcile-before.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/reconcile-after.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/draft-apply.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/make-controls.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/make-control-c.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/current-tree/current-tree.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/current-tree/proposed-SCORECARD.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/current-tree/proposed-PROVINCE.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap/current-tree/base-sha.txt`
