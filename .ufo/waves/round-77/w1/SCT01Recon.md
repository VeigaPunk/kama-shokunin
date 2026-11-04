# SCT01 — independent re-derivation of the base measurements

Seat `SCT01Recon`, kama r77 w1. Read-only. Base `cc6e1d3c`; freeze `7d60e2ab`; lane advanced
to `d86ce85b` during recon (all base numbers pinned to explicit revisions). Full commands,
exit codes and verbatim outputs: `.ufo/waves/round-77/w1/SCT01Recon/recon.md`; receipts in
`.ufo/waves/round-77/w1/SCT01Recon/`. Scratch `/fast/scratch/hyaku/kama-r77/SCT01Recon/`
deleted. No tools installed.

## 1. Base audit: 241 events = 95 + 5 + 53 + 47 + 41

`python3 tools/append-only-audit.py --repo . --to cc6e1d3c --json` → exit 1, valid JSON:
`events=241 restored=95 partial=0 unrestored=53 ungraded=88 disclosed=5 permitted_lines=634 … bad_declarations=0`.

Independent join (`recon_classify.py`) against the base registers/contract:
**95 restored + 5 disclosed + 53 accepted-register + 47 exempt-row + 41 ungraded-no-row.**
The 41 decompose as **28 fully permitted** (`permitted == deleted`, all `corpus/SOURCES.md`,
75 deleted lines) + **4 out-of-region** (`corpus/knowledge/consumer-registry.md`, contract
`only=## Errata`, all 19 deleted lines in sections outside it) + **9 SCORECARD head**
(14 lines; `ba9f7248`, `900e31b7`, `11c08bdc`, `b919f0cb`, `ac1c8538`, `461d2adb`,
`661622b5`, `417bbf81`, `c1ae92d5`) + **0 neither**. My 41 `(commit,file)` pairs are
**identical** to the 41 `APPEND_EXEMPT_FINDING` pairs in the committed
`.ufo/waves/round-77/measured/before/c2-append.out`. `permitted+graded+ungraded == deleted`
holds for all 241 events.

## 2. Three round-75 `measured/before/*.out` receipts: confirmed

Each of `c1-mutants.out`, `c2-mutants.out`, `c3-audit.out` names `rev=dc58e513…` in its
first five lines (twice in c1/c2 via `# base:`, once in c3); each is introduced by
`10f37171…` (single `--diff-filter=A` commit); `git merge-base --is-ancestor dc58e513…
10f37171…` → exit 0; sha256 at the introduction equals sha256 at `cc6e1d3c` and at
`b06cc612` (the C1 population tip): `0a2326ec…`, `208e8034…`, `e6aee72d…`. The round-76
counter at `--tip b06cc612` reproduces the base line exactly: `bound=6 unbound=2 shifted=3`,
exit 1; the three shifted are these receipts, shifted by
`registry/append-only-contract.tsv` at `b8ed2568`. (At `--tip cc6e1d3c` the old counter says
`shifted=9` because round-76 paths enter the delta — a population-tip difference, not a
contradiction.)

## 3. Stale round-76 facts: the two named, **plus a third**

- `filtered knowledge entries 46` (`SCORECARD.md:4190`, population sentence naming
  `c2aa7fb2`) vs the true filtered population at `c2aa7fb2`: `git ls-tree -r --name-only
  c2aa7fb2 corpus/knowledge/ | grep -v 'engine-sides\|processes' | wc -l` → **47** (raw 49).
  The `## Axes` coverage row already says 47. **Mismatch confirmed.**
- `## Axes` calibration row (`SCORECARD.md:18`) names `corpus/lessons/round-75-verifier-spotcheck.md`;
  the newest at `cc6e1d3c` is `corpus/lessons/round-76-verifier-spotcheck.md` (round69
  counter `--since-round 63`: exit 1, `STALE_CALIBRATION row_names=round-75 newest=round-76`).
  **Mismatch confirmed.**
- **Third stale fact — work tip.** `LOG.md:3061` files work tip `a3fbc629…`. The lane's
  inherited closure-sealed rule (the one that produced the round-76 correction value
  `c9ab73d8` for round 75) applied to round 76 derives **`0e01f32f…`** (the `PROVINCE.md`
  surface-row commit). The landed `tools/round77-selfrecord-round76.py` prints at base:
  `SELFRECORD_R76 claims=6 mismatches=3 corrected=0 unbacked=0` +
  `SELFRECORD_R76_FACT work-tip filed=a3fbc629… derived=0e01f32f…`, and at `d86ce85b`:
  `mismatches=0 corrected=3 unbacked=0`. Three correction blocks landed (`work-tip`,
  `knowledge-entries`, `closure-pointer`).

**Disagreement, stated plainly:** the base has **three** stale round-76 facts, not two, and
the landed green line is `corrected=3`, not the frozen `corrected=2`. The plan's C3
population misses the work-tip fact that the round's own correction block then adds. C3 as
frozen is not met by the landed counter; this is a freeze-target defect of the same family
as the round-76 C1/C3 misses and should be recorded as such, not scored green.

## 4. Counter-evidence

- **No event falls through all six classes.** With the 9 planned head rows, the 241 events
  partition 53/56/28/4/95/5 (accepted/exempt/permitted/out_of_region/restored/disclosed),
  sum 241, 0 fall-through. The landed C2 counter at `--to cc6e1d3c` prints the frozen
  `APPEND_REGISTERS … unaccounted=0 … introductions=1/1 rotation_safe=1` line, exit 0.
- **No baseline receipt has a non-ancestor introduction.** Scanned all 80
  `measured/before/` paths (75 `.out`): 0 non-ancestor introductions, 0 no-add-commit.
  Two out-of-population hazards exist and are named in `recon.md` §4.2: one baseline receipt
  changed bytes after introduction (`round-72/measured/before/round-scope-control-old.out`),
  and two name >1 distinct 40-hex revisions in their first five lines (`round-73/…/
  sources-census-start.out`, `round-76/…/c2-facts.out`). Neither is cited by the round-75
  record, so `bound=9` is unaffected.
- **3 permitted events carry graded lines:** `5890d1a0` (permitted 6, graded 1, restored),
  `9c5a8644` (276/362, restored), `ea33a78f` (277/362, unrestored/accepted). Ruling (d)
  excludes all three; a `permitted > 0` classifier would launder 362 graded lines in
  `ea33a78f`.
- **Exempt-cutoff tension:** 5 of the 9 head events are ancestors of the exempt register's
  introduction `c2aa7fb2`; **4 postdate it** — `461d2adb`, `661622b5`, `417bbf81`,
  `c1ae92d5`. The round-76 SN01 rule would admit only 5 (`exempt=52`, 4 unaccounted); the
  frozen `exempt=56` requires C2 scope ruling (a) (row admissible when its event commit is
  an ancestor of the audit revision). This is a real divergence from the round-76 temporal
  cutoff and should be recorded in the lesson/report. The old round-76 counter at the current
  tip calls the 9 new rows `rotation` (18 findings) because it applies the single earliest
  cutoff; the new counter correctly reserves `rotation` for a re-introduced register path.

## 5. Receipts (absolute paths)

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SCT01Recon/`:
`recon.md`, `audit-base.json`, `audit-base.txt`, `recon_classify.py`,
`recon_classify.out`, `counter_evidence.py`, `counter_evidence.out`,
`decomposition-table.txt`, `receipts-verify.out`, `facts-verify.out`,
`closure-base.out`, `r76-append-at-head.out`, `r76-scope-at-b06cc612.out`,
`c1-current.out`, `c2-current.out`, `c3-at-base.out`, `c3-at-integration.out`,
`knowledge-c2aa7fb2.txt`.
