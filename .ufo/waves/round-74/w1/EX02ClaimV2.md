# EX02ClaimV2 — kama round 74, wave w1, C2 build + attack

Seat: `EX02ClaimV2` (leaf executor, C2). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Lane tip while working: `b0b903a0` (`b0b903a0854365fbf4d1ba4d18ae9a66052cce4f`,
"round-74: freeze w1 wave spec (13 seats) and dispatch evidence"). No commit made by this seat.

Deliverable: `tools/round74-receipt-claim-binding.py`
sha256 `0f231fac27a2b49e99a8d186162f62942a7f9328bf0dcb8d987eabc98051ab44` (32144 bytes,
mtime 2026-11-04 01:21:29 -0300), untracked at the lane tip; the L1 commits it.

Receipts copied under `.ufo/waves/round-74/w1/EX02ClaimV2/receipts/` with `SHA256SUMS`.
Scratch `/fast/scratch/hyaku/kama-r74/EX02ClaimV2/` deleted after the copy (below).

## 1. What the module does (frozen C2 predicate, byte-equal)

`PREDICATE` is byte-equal to the plan's C2 blockquote with `>` marks and line breaks removed
(the selftest's `predicate` arm compares it against `plans/round-74-claims.md` every run):

```
$ python3 tools/round74-receipt-claim-binding.py --selftest --work <scratch>
[PASS] predicate
...
RECEIPT_CLAIM_V2_SELFTEST pass=15 fail=0
```

- **Paragraph scoping.** Both record blobs (`SCORECARD.md`'s `## Round <N>` section and
  `corpus/lessons/round-<N>.md`, both read at `<rev>`) are split on blank lines; citations
  (`base.TOKEN_RE` + `base._resolve_citation`) and tip claims are resolved per paragraph.
  A claim token broken by hard line breaks is `wrapped-claim`; a whole token standing on a
  different line of the paragraph than its citation is `offset-claim`.
- **Tip binding.** A paragraph that cites a receipt and carries a tip claim (`at the tip`,
  `at the report tip`, `report tip`, case-insensitive, `\s+` spanning newlines) must have
  every cited receipt whose `tip=`/`rev=` header (case-insensitive key AND hex, first five
  lines, conflicting headers unusable) names `<rev>`.
- **Explicit revision binding.** A 40-hex revision named in a citing paragraph binds each
  cited receipt whose header equals it (hex case-insensitive, lookarounds keep a 40-hex
  window out of 64-hex digests) and is a `stale-revision` finding when the header differs.
  This is the realizable clean rule: the named revision is an ancestor, never the record's
  own commit.
- **Exit map.** 0 only when the r72 base verdict is green and no claim finding exists; 1
  printing each base finding then each
  `RECEIPT_CLAIM_V2_FINDING <kind> <path> :: <line_no>: <line>` then the summary; 2
  (`RECEIPT_CLAIM_V2_UNREADABLE ...` on stderr) when the base tool is absent/exit 2, the
  self-record is unreadable, or the CLI is misused.
- **Composition.** Shells out to the byte-frozen `tools/round72-receipt-tip-binding.py
  --json`; imports `tools/round73-receipt-claim-binding.py` (byte-frozen) only for
  `_base_tool_path` / `_load_base` / `_run_base`, and the r72 module for citation/header/git
  primitives. Neither frozen file is edited.

### Interpretation disclosed (one sentence of the freeze is under-specified)

The predicate enumerates exactly three finding kinds. For the inherited r73 shape — claim
and citation on one line while the header names an older revision — there is no wrapping and
no offset, so the module classifies it `stale-revision` (the only revision-mismatch kind in
the frozen vocabulary). It does not emit `stale-claim`: that label is outside the frozen
enumeration and would make a clean `wrapped-claim`/`offset-claim` run also print a name the
plan does not define. Attack arm `same-line-stale-revision` pins this. Likewise, the
predicate says "names an explicit 40-hex revision" with no semantic test, so any full 40-hex
token in a citing paragraph is graded (critic fixture `nc2_recorded_at_hex` below).

## 2. Control + kill + clean receipts (committed builder)

`SURVIVORS` line over the fixtures rebuilt by the committed
`.ufo/waves/round-74/controls/build-survivors.py` (receipts/score-survivors.out):

```
BASE_C2 c2_wrapped exit=0 verdict=GREEN RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
BASE_C2 c2_offset exit=0 verdict=GREEN RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
V2_C2 c2_wrapped exit=1 KILLED RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=1 unbound_claims=1 bound_revisions=0
V2_C2 c2_offset exit=1 KILLED RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=1 unbound_claims=1 bound_revisions=0
V2_C2 c2_mixed_honest exit=0 GREEN RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=1
V2_C2 c2_clean_realizable exit=0 GREEN RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=1
SURVIVORS c2 base_green=2 v2_killed=2 v2=present clean=True
```

i.e. the r73 counter is green on both escape fixtures (the hole), the v2 counter kills both,
and both realizable-clean fixtures exit 0 with `bound_revisions=1`. Per-fixture finding
lines (receipts/c2-fixture-runs.out):

```
=== c2_wrapped
RECEIPT_CLAIM_V2_FINDING wrapped-claim .ufo/waves/round-74/measured/a.out :: 6: at the
exit=1
=== c2_offset
RECEIPT_CLAIM_V2_FINDING offset-claim .ufo/waves/round-74/measured/a.out :: 5: - C2 evidence: measured at the report tip.
exit=1
=== c2_mixed_honest
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=1
exit=0
=== c2_clean_realizable
RECEIPT_CLAIM_V2 round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=1
exit=0
```

## 3. Selftest arms (15/15)

`RECEIPT_CLAIM_V2_SELFTEST pass=15 fail=0` (receipts/selftest.out). Arms: `predicate`
(byte-equal to the frozen plan), `frozen-bytes` (r72+r73 clean against HEAD),
`header-case-insensitive` (`# TIP=<UPPER>` parses to lower-case hex),
`fixtures` (source=builder: the committed builder ran; inline rebuild is the fallback when
absent), `c2-wrapped-killed`, `c2-offset-killed`, `c2-mixed-honest-case`,
`c2-clean-realizable`, `same-line-stale-revision`, `two-receipts-stale` (one paragraph,
two receipts, `bound_revisions=1` + one `stale-revision`), `lesson-wrapped-claim`
(lesson file, line 4), `base-exit-2-propagates` (base rc 2 -> our rc 2),
`base-tool-absent` (rc 2 naming it), `cli-misuse` (missing `--round` and `--round 0`),
`frozen-digests-stable` (r72/r73 sha256 identical before/after the full selftest).

## 4. Live lane run (honest could-not-evaluate)

```
$ python3 tools/round74-receipt-claim-binding.py --repo . --round 74 --tip master
RECEIPT_CLAIM_V2_UNREADABLE base tool could not evaluate: RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at master carries no '## Round 74' section; the round's self-record cannot be read
exit=2
```

Expected and recorded honestly: the round-74 record does not exist yet at `b0b903a0`, so the
live run is exit 2, not a green claim. It will grade the round's record once the L1 lands a
`## Round 74` section plus `corpus/lessons/round-74.md` at the tip.

## 5. Frozen tools untouched

receipts/sha256.out, all worktree digests equal to the `HEAD:` blobs:

```
0f231fac...  tools/round74-receipt-claim-binding.py        (new, untracked)
a9a4e8d3...  tools/round72-receipt-tip-binding.py          == HEAD:a9a4e8d3...
888eb075...  tools/round73-receipt-claim-binding.py        == HEAD:888eb075...
9ecb77f8...  .ufo/waves/round-74/controls/build-survivors.py == HEAD:9ecb77f8...
451e51af...  .ufo/waves/round-74/controls/score-survivors.py == HEAD:451e51af...
frozen tool git status lines: 0
```

Inherited selftests re-run at this tip (receipts/frozen-selftests.out):
`RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0`, `RECEIPT_CLAIM_BINDING_SELFTEST pass=14
fail=0` — matching the plan's 16/16 and 14/14.

## 6. Attack cross-check (read-only, critic fixtures)

Ran the module over `CRT01Claims`' fixtures under
`/fast/scratch/hyaku/kama-r74/CRT01Claims/new-fixtures/` (read-only; nothing there written),
receipts/critic-fixtures-run.out:

| fixture | result |
|---|---|
| `nc2_stale_explicit` | exit 1, `stale-revision` on `r.out` (record names `383c189…`, header `b0c9…`) |
| `nc2_two_receipts` | exit 1, two `stale-revision` findings (both headers name ancestors, not the tip) |
| `nc2_recorded_at_hex` | exit 1, `stale-revision` — the named 40-hex is graded literally (see §1 disclosure) |
| `nc2_lesson_only` | exit 1, `wrapped-claim` at `corpus/lessons/round-74.md :: 4:` |
| `zz-c2_wrapped-7fcb21` | exit 1, `wrapped-claim :: 6:` |
| `zz-c2_offset-7affcd` | exit 1, `offset-claim :: 5:` |
| `zz-c2_mixed_honest-765353` | exit 0, `bound_revisions=1` |

## 7. Incident: concurrent overwrite of the deliverable (disclosed)

At 2026-11-04 01:20:28 -0300 an unknown peer process overwrote
`tools/round74-receipt-claim-binding.py` with a different 24176-byte implementation
(sha256 `8d7329e735e10e00b0f3d1193ba25710d3814f69f671b6a0c34b5867718bb990`), preserved at
`receipts/overwritten-peer-version.py`. That version is **unimportable**: line 76 runs
`import round73_receipt_claim_binding`, but `tools/round73-receipt-claim-binding.py` is
hyphenated and no such module exists, so every invocation dies with
`ModuleNotFoundError: No module named 'round73_receipt_claim_binding'` (observed on all
seven critic fixtures). It also emitted `stale-claim`, outside the frozen enumeration. I
restored this seat's tested artifact byte-identically (sha256 back to `0f231fac…`, matching
the pre-overwrite tested digest) and re-ran the full selftest, the control scorer and the
live run afterwards.

Risk: if another process rewrites the path again, the C2 deliverable is lost again. The L1
should commit `0f231fac…` and re-check the path's sha256 before the gate.

## 8. Risks / limits

- The binding proves the claim matches the revision a receipt *names*; it does not prove the
  receipt's content honest (plan non-goal).
- `claims`/`unbound_claims` count paragraphs (the scoping unit), not lines; `bound_revisions`
  counts (paragraph, receipt) bindings.
- A citing paragraph that mentions the lane base revision (e.g. `868dd701…`) in the same
  paragraph as receipts will bind those receipts to the base and flag them. That is the
  frozen rule read literally; record authors should keep revision mentions in their own
  paragraph.
- No tool installs needed; no model/route touched.

## 9. Scratch

`/fast/scratch/hyaku/kama-r74/EX02ClaimV2/` (fixtures, selftest trees, receipts) deleted
after copying receipts and `SHA256SUMS` into
`.ufo/waves/round-74/w1/EX02ClaimV2/receipts/`.
