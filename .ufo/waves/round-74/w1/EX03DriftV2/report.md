# EX03DriftV2 — C3 build: `tools/round74-province-host-drift.py`

Seat: EX03DriftV2 (kama r74 w1, axis: freshness). Claim: **C3 — host-block
base-revision preservation** (`plans/round-74-claims.md` §C3, frozen).

## Deliverable 1 — the module

`tools/round74-province-host-drift.py` (new file, sha256
`118ae079a7f5a18fa40548940eea8d5e8b6fdfbf28c953c997b911f2dba6bad7`).

Composition, exactly as the predicate freezes:

- **Base leg**: runs the byte-frozen `tools/round73-province-host-drift.py`
  (`--repo <lane> --json`) as a subprocess; its findings (no-block / stale-host),
  graded triple, live triple and stale flag flow into the v2 verdict. Exit 2 when
  the base leg could-not-evaluate.
- **Preservation leg**: parses `recorded at <40-hex>` tokens inside
  `Round-<N> host-identity block (YYYY-MM-DD)` paragraphs (r73 block grammar
  unchanged) and, for **every** token-carrying block (not only the newest),
  compares the block text resolved at `<rev>` with the worktree block. Any byte
  difference — triple, date, anything before the token — is
  `PROVINCE_HOST_DRIFT_V2_FINDING edited-block <detail>` even when the edited
  block matches the live triple.
- Summary line: `PROVINCE_HOST_DRIFT_V2 blocks=<b> recorded=<s>/<m>/<id>
  live=<s>/<m>/<id> stale=<n> edited=<e>`; exit 0 only when the base leg is green
  and edited=0; exit 1 findings; exit 2 could-not-evaluate (PROVINCE.md
  unreadable, a `recorded at` rev unresolvable — named, CLI misuse). `--json`
  mirrors the r73 payload shape with v2 fields.

Two semantics fixed by the frozen round-74 record and fixtures (documented in
the module docstring):

1. **Token sentence stripped before comparison.** The token sentence (from
   `recorded at <rev>` to end of paragraph) is the pointer, not the payload. The
   lane's own newest block gains the token in the round-74 record commit *after*
   the revision the token names (`868dd701…`, the freeze base); gaining the
   pointer is the honest flow and must not self-fail. Every byte before the
   token is compared.
2. **Recorded-bytes resolution.** The recorded bytes are the ordinal-matched
   block's stripped text in the token rev's tree (`git show <rev>:PROVINCE.md`).
   The committed builder's c3 fixtures name the *seed* rev in the token — a tree
   that does not yet contain `PROVINCE.md` — so when the block is absent at the
   token rev the resolution walks forward (`git rev-list --reverse <rev>..HEAD
   -- <file>`) to the first commit carrying the block (the recording commit
   proper). A rev that does not resolve at all is could-not-evaluate (exit 2,
   named). This is the only reading under which both frozen fixture arms pass:
   naive `git show` alone would score c3_clean as a finding (block absent at the
   named rev) or skip c3_edited's edit entirely.

No frozen file was edited: `frozen-untouched.out` — `git status` shows only new
`tools/round74-*.py` files and `git diff` of the r73 tool is empty. No commits
made. Nothing installed (python3/git already present; pacman guard respected, no
transactions needed).

## Deliverable 2 — selftest and committed-builder fixtures

Selftest (`selftest.out`, fixtures under the scratch work dir, git identity
`-c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false`,
toplevel asserted before first commit):

```
PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0
```

Arms: clean-token (c3_clean replay), edited-date (c3_edited replay, base leg
green + v2 exit 1 edited-block), no-block → 1, stale-host passthrough → 1,
unresolvable rev → 2 naming the rev, older-block-edited (newest live, older
token block edited → 1 naming round=72), missing file → 2, CLI misuse → 2,
predicate byte-equality, token-gained-honest (live-lane record shape).

Committed builder, rebuilt in my scratch
(`build-survivors.py --work /fast/scratch/hyaku/kama-r74/EX03DriftV2/controls-work`),
`c3-committed-fixtures.out`:

- c3_edited: r73 base leg **exit 0 GREEN** (control that skips the claimed
  work); v2 **exit 1** naming `edited-block` with `resolved-at=6ef89fe…` and
  both texts (`2026-11-03` at recorded rev vs `2026-11-04` at tip).
- c3_clean: v2 **exit 0**, `edited=0`.

Counting command (`score-survivors.out`, run with the rebuilt fixtures-meta):

```
SURVIVORS c3 base_green=1 v2_killed=1 v2=present clean=True
```

## Deliverable 3 — live lane run (honest)

`live-lane.out`:

```
PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0   (base, exit 0)
PROVINCE_HOST_DRIFT_V2 blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0 edited=0   (exit 0)
```

**The leg is not vacuous, and I faked no token.** The seat spec expected no
`recorded at` token yet; in fact the worktree already carries the
round-74 record-commit staging (a sibling edit, uncommitted): the Round-73
block ends with `recorded at 868dd701bff531be6a36da742d3418f98818e5eb (round-74
freeze base; the v2 preservation leg compares the block text with this token
sentence stripped)` — which pins the strip semantics implemented above. The
preservation leg ran for real: the token rev resolves, the block exists there
(`git show 868dd701:PROVINCE.md` line 310), and the stripped texts are
byte-identical (`predicate.out` verification + `live-leg-probe.out`).

Liveness proof against the real lane history (`live-leg-probe.out`, scratch
clone): honest copy → exit 0; one date byte edited (`2026-11-03` →
`2026-11-05`) in the clone worktree → exit 1 naming `edited-block` with
`rev=868dd701…` and both texts.

## Grounding

- Predicate constant byte-equal to the plan's C3 blockquote:
  `predicate_equal: True`, 771 chars,
  sha256 `6d8197ee8b12b82a23192160ecc9af99194f95c6f8c2bc5c466b004c288c4ffe`.
- Module: `tools/round74-province-host-drift.py`
  (`118ae079a7f5a18fa40548940eea8d5e8b6fdfbf28c953c997b911f2dba6bad7`).
- Receipts in this directory (hashes in `SHA256SUMS`): `selftest.out`,
  `c3-committed-fixtures.out`, `score-survivors.out`, `live-lane.out`,
  `live-leg-probe.out`, `predicate.out`, `frozen-untouched.out`.
- Plan: `plans/round-74-claims.md:148-156` (predicate), `:158-171`
  (composition, exit map, kill rule). Frozen builder:
  `.ufo/waves/round-74/controls/build-survivors.py:222-239` (c3 shapes);
  before-receipt `.ufo/waves/round-74/measured/before/score-survivors-base.out:6`
  (`BASE_C3 c3_edited exit=0 verdict=GREEN`).

## Risks / disagreements

- **Forward-resolution is my derivation, forced by the frozen fixtures.** The
  seat-spec parenthetical says "`git show <rev>:PROVINCE.md`, same paragraph",
  but the frozen builder's fixtures put the token at the seed rev where that
  file does not exist; with plain `git show` either c3_clean fails (absence as
  finding) or c3_edited passes (absence skipped) — contradicting the frozen kill
  rule. Walking to the recording commit satisfies both arms and the predicate's
  "byte-identical at `<rev>` and at the worktree tip" for every block that
  exists at `<rev>`. Flagging here rather than editing anything frozen.
- The worktree `PROVINCE.md` token edit is uncommitted (sibling staging); my
  tool reads the worktree as the tip side, per the predicate. Once the L1 lands
  the record commit, the comparison path changes from "strip the gained token"
  to a plain rev-side compare — both are exercised by selftest arms 10 and 1/2.
- Scratch dir `/fast/scratch/hyaku/kama-r74/EX03DriftV2` deleted after receipts
  were copied here; nothing under `/tmp` is cited.
