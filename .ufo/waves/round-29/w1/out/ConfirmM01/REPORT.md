# ConfirmM01 — SCORECARD.md:Q:f4c42debcc:0 (round 29, W1)

## Verdict

**confirmed-false.** The base statement was false at the revision that wrote it. The
counter's observation `q:no-artifact` is correct, independently reproduced by hand
without executing the counter.

- sid: `SCORECARD.md:Q:f4c42debcc:0` — file SCORECARD.md, line 20 at base
  `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, class Q
- token: `` `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` ``
- writing revision **W = `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`** (confirmed by
  `git blame -L 20,20 --line-porcelain 2aa46e24 -- SCORECARD.md`; commit "round-3:
  re-census — derived --ufo-src, registry cut to live rows, corpus errata",
  author-time 1791981983)

## The class rule, read from the frozen counter source

count-c1.py docstring lines 31-32: a Q span HOLDS iff "the span occurs verbatim in at
least one blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md and
corpus/** (committed evidence at writing) (fail: q:no-artifact)". Implementation
(lines 259-264): `git grep -F -q -e SPAN W -- . :(exclude)SCORECARD.md
:(exclude)SHONEN.md :(exclude)LOG.md :(exclude)corpus`; returncode 1 →
`q:no-artifact`. Counter file sha256 re-hashed to
`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the
freeze). The counter was **read, never run**.

## Independent check at W (performed by hand)

1. `git grep -F -n '<full span>' W -- ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md'
   ':(exclude)LOG.md' ':(exclude)corpus'` → **no hits, exit 1**.
2. Without exclusions, the span occurs at W in exactly two blobs:
   `LOG.md:239` (line `snapshot: snapshot=20261014T124232Z ...`) and
   `SCORECARD.md:11` — the row itself, which sat at line 11 at W and line 20 at base
   (blame confirms W wrote the base line; the row is unchanged since W). Byte identity
   of the span in both lines verified by an exact substring count (1 occurrence each).
3. Same excluded search at base `2aa46e24` → also exit 1.

So no committed blob at W outside the four excluded locations contains the quoted
span verbatim: the Q statement does not hold. **Not a counter false positive** —
the exclusions are the rule working as designed (self-referential quoting — the
writing file or the lane log — is not independent committed evidence).

## What the statement most likely referred to (intended referent)

The live `tools/kama-probe.sh snapshot` re-census of 2026-10-14T12:42:32Z performed
during round 3. The full span is archived **verbatim only** in LOG.md:239 (the
round-3 entry's "Live proof after" block, committed in W itself) plus the SCORECARD
row — both excluded by the rule. Independent, committed, non-verbatim corroboration
at W is strong and internally consistent:

- `registry/history/latest.tsv` at W: header `#@snapshot_id 20261014T124232Z`, 3 rows
  all DEAD (→ rows=3, model_ok=0, drift=3).
- `registry/history/DELTA.md` at W: exactly 16 transition lines, every one stamped
  2026-10-14T12:42:32Z (→ transitions=16; 3+3+3 field/verdict changes + 8 row-absent).
- LOG.md:240 second run `snapshot=20261014T124525Z prev=20261014T124232Z ...
  transitions=0 exit=2` (→ the row's "stable re-run transitions=0").
- Dated kama-probe JSON snapshots are untracked by design:
  `registry/history/.gitignore` at W ignores `*.json` with the comment "Dated
  snapshots are local run evidence; the normalized baseline and ledger are tracked."
- Fleet (read-only, outside the lane repo) `/home/vgpnk/Projects/shokunin/.ufo/reports/`:
  `round-2/kama.md:31-34` shows the identical `snapshot=... prev=...` stdout format
  from the round-2 runs; `round-10/kama.md:21` cites the tracked baseline
  `20261014T124232Z`. No fleet report carries the full span.

Ruled out: reformatted/paraphrased artifact at W (none — full-tree grep at W hits only
the two excluded blobs); artifact committed later (first carrier outside the
exclusions anywhere in history is `827d136`'s own `.ufo/waves/round-29/before/
c1-base.json`, i.e. this round's freeze receipt; all later carriers are round-29 wave
artifacts); fleet report (format/baseline citations only, no span).

## Sanity cross-checks

- Frozen base receipt entry for this sid matches my item exactly (class Q, line 20,
  token, W, observed `q:no-artifact`, holds:false).
- Sibling statement `:1` (`transitions=0`) on the same line holds (`ok`): the string
  occurs in non-excluded `SKILL.md:187` at W (round-2 run text) — the extractor and
  grep path behave consistently.
- Sibling `:2` (`RESULT pass=24 fail=0`) also fails as q:no-artifact — same root
  cause, out of my item's scope.

## Residual risk and verification gaps

- The 2026-10-14T12:42:32Z run itself was not re-executed (would require the round-3
  box state); the quote's authenticity rests on LOG.md plus the mutually consistent
  tracked `latest.tsv`/`DELTA.md` ledger, not on re-derivation.
- The lane working tree has no committed round-3 `.ufo` directory (top-level tree at
  W: AGENTS.md LOG.md MINT.md PROVINCE.md SCORECARD.md SHONEN.md SKILL.md corpus
  registry tools), so no further committed artifact could exist beyond those checked.
- Nothing else material left unverified for this sid.

## Installations

None. No tool installed or updated (nothing beyond /usr/bin/git and stock python3 was
needed). No git writes anywhere; no tracked lane file touched; scratch-free
investigation (all evidence via read-only git object access).
