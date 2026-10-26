# Proposed fixes (K0Harm) — unapplied proposals, round 47

None of these were applied (lane read-only). They are the smallest corrections for
the defects in K0Harm.md §3. Counters/guards are frozen; all are *next-round or
integration-time documentation* work.

## 1. SCORECARD.md:18 calibration row (integration-time)

Row currently says (line 18):

    run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `32` (outside closures on record); that figure is the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit; … latest outside closure `corpus/lessons/round-45-verifier-spotcheck.md` (rejected-honest-stop; re-anchored round 46);

Proposed replacement (same line, re-derived value — this fact row is re-derived in
place per the append-only-contract note for SCORECARD.md, `registry/append-only-contract.tsv` row 2):

    run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `33` (outside closures on record); that figure is the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit; … latest outside closure `corpus/lessons/round-46-verifier-spotcheck.md` (admitted round 46);

Verification after edit: `python3 tools/round41-scorecard-reconcile.py --repo . --tip 3a09a1d…` and `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 3a09a1d…` should flip to `mismatches=0 met=True` (round43 `spot=0`).

## 2. tools/sources-append-only.py — scope ROWLIKE refusal to the registry section (next round)

Current behavior: ROWLIKE_RE matches any `| S0NN |`-looking line anywhere in the blob
(`:50-60`) and a match outside the parsed `## Registry` section is a parse error →
exit 2 (docstring `:27-31`). Since the Round-45 re-verification tables landed in
corpus/SOURCES.md, every transition whose FROM contains them is ungradeable.

Proposed change (sketch, next-round tool edit):

    # only enforce row-like strictness *inside* the registry section:
    # - parse the section once (heading to next same/higher heading)
    # - inside the section: existing strict rules unchanged
    # - outside the section: drop rows that look like `| S0NN |` without failing
    #   (they are re-verification tables / lesson tables; they can neither hide
    #   nor add registry rows because the section was already fully parsed)

This keeps the guard's "no hidden row" property for the registry while letting
non-registry tables exist. Note: `--selftest` must gain a case with a non-registry
`| S0NN |` table to pin the new behavior.

## 3. tests/llamacpp-live/check-receipt.py — v4 acceptance (integration-time)

Add v4 to the accepted schemas:

    RECEIPT_SCHEMA_V4 = "kama-llamacpp-live/v4"

- accept `provenance` (`server.asset_url`, `server.asset_sha256`, `server.member`,
  `model.url`, `model.sha256`) when present;
- accept `teardown.log_path` null or a repo-relative path with no `..` that exists
  at the audited tip (mirror the C2 counter's receipt leg);
- keep the same check-id set as v3 (v4 did not remove/rename checks).

If L1 prefers not to touch the gate this round, the acceptable fallback is to
document (SKILL.md/README/knowledge supersession lines) that v4 receipts are
validated by `tools/kama-live-replay.py` + `tools/round47-live-replay-audit.py`
only, and that `check-receipt.py` is v1-v3 only.

## 4. tools/gguf-identity.py — v3-only boundary (documentation)

`tools/gguf-identity.py:44,476-478` strictly requires `kama-llamacpp-live/v3`.
Either add a v4 branch reading `provenance.model.sha256` / `server.sha256`, or
state in the tool docstring that v4 receipts are out of scope and handled by the
replay tool.

## 5. Hexrun census — ledger fleet-report commits (next round)

`corpus/lessons/round-46-verifier-spotcheck.md:23` cites fleet commit
`8bca0cf333e7ceab5e734b354c87075c6efec86c` (exists in `/home/vgpnk/Projects/shokunin`, not in the lane).
The pre-existing unknown family `b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025` (fleet report commits,
104 occurrences) shows the same class. Add a ledger class (e.g. `fleet_lane`/`upstream_ok`-adjacent)
for fleet-repo commit objects, so the `unknown` count stops drifting +1 whenever a
lesson cites the fleet report commit.
