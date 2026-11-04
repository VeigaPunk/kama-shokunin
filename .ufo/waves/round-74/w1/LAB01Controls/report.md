# LAB01Controls — kama round 74 w1 control verification and do-nothing probes

Seat: LAB01Controls (revenger/lab, calibration axis). Scope: control verification of the
round-74 freeze + do-nothing probes + one named junk-row cheat per claim. No lane source
files edited; no mutating git commands anywhere; all fixtures under
`/fast/scratch/hyaku/kama-r74/LAB01Controls/` (deleted after receipts were copied here).

Freeze read first, in full: `plans/round-74-claims.md` (sha256 pinned in
`.ufo/waves/round-74/controls/freeze.txt` line 2). No disagreement with the freeze found;
one fixture-semantics wrinkle observed (§C3 wrinkle) — reported, not edited.

## Tooling

No installs/upgrades needed. Used: python3 3.x (system, Arch), git (system), coreutils.
All invocations ran with absolute paths; fixture git writes used the fixture identity
`-c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false` and asserted
`git rev-parse --show-toplevel` == the fixture dir before the first commit
(build-survivors.py:67-72 does this itself; my probe variants re-asserted).

## (1) Fixture rebuild + before-receipt verification — PASS

Commands (verbatim):

```
mkdir -p /fast/scratch/hyaku/kama-r74/LAB01Controls/fixtures
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-74/controls/build-survivors.py \
  --work /fast/scratch/hyaku/kama-r74/LAB01Controls/fixtures \
  --meta /fast/scratch/hyaku/kama-r74/LAB01Controls/fixtures-meta.json
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-74/controls/score-survivors.py \
  --meta /fast/scratch/hyaku/kama-r74/LAB01Controls/fixtures-meta.json \
  --lane /home/vgpnk/Projects/shokunin/kama-shokunin
```

Rebuild printed the 8 expected FIXTURE lines + META (receipt: `receipts/score-survivors-rerun.out`).
Scorer output, pasted in full:

```
BASE_C1 c1_invisible exit=0 round=71 rows=3
SURVIVORS c1 base_round=71 base_rows=3 v2_killed=0 v2=absent clean=n/a
BASE_C2 c2_wrapped exit=0 verdict=GREEN RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
BASE_C2 c2_offset exit=0 verdict=GREEN RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
SURVIVORS c2 base_green=2 v2_killed=0 v2=absent clean=n/a
BASE_C3 c3_edited exit=0 verdict=GREEN PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
SURVIVORS c3 base_green=1 v2_killed=0 v2=absent clean=n/a
```

Byte-for-byte match against the committed before receipt — `diff` silent, sha256 identical:

```
$ diff score-survivors-rerun.out .ufo/waves/round-74/measured/before/score-survivors-base.out && echo "BYTE-FOR-BYTE MATCH"
BYTE-FOR-BYTE MATCH
$ sha256sum score-survivors-rerun.out .../score-survivors-base.out
1a7903f371f1ead368d790738092597df37711de5be028d21a3c26b422a2a486  score-survivors-rerun.out
1a7903f371f1ead368d790738092597df37711de5be028d21a3c26b422a2a486  .../score-survivors-base.out
```

`1a7903f3…` is exactly the receipt pin in `freeze.txt` line 7. All three SURVIVORS lines
reproduce with v2=absent (no v2 instruments exist yet at base — correct for the before state).

fixtures-meta.json vs freeze pin (`freeze.txt` line 6): the **committed**
`.ufo/waves/round-74/controls/fixtures-meta.json` sha256 is `e7d316ec…` == pin, verified:
`sha256sum .ufo/waves/round-74/controls/fixtures-meta.json` → `e7d316ec0c1e2c76fa3677b5aed92a2c264e03d137a3a1cf2e6fe49c9500c004`.
My rebuilt meta under the seat scratch root differs only in (a) fixture path strings
(`…/LAB01Controls/fixtures/…` vs the committed default `…/controls-work/…`) and (b)
commit-id fields (`receipt_rev`/`tip`/`recorded_rev`), because git commit hashes embed
timestamps — the SURVIVORS lines contain no paths and are byte-identical (above).

Control-script pins also re-verified: `build-survivors.py` → `9ecb77f8…` and
`score-survivors.py` → `451e51af…`, `probe-canon-base.py` → `2f6f9ac2…` — all == `freeze.txt`
lines 3-5. Base revision: `freeze.txt` line 1 pins `868dd701…`; current `master` is
`b0b903a0` (two freeze commits on top); `git merge-base --is-ancestor 868dd701 master` →
true (base unchanged, history only advanced).

Extra base re-verification (read-only): the frozen r42 `canon()` over the base blob
`868dd701:SCORECARD.md` (via `git show`, module imported in-process) prints
`BASE_C1 canon_round=71 canon_rows=17` == committed `measured/before/probe-canon-base.out`
(sha256 pin `bf1d9cd7…`).

## (2) Do-nothing probes against the frozen targets

### (a) C1 — no r42 `canon()` resolution over `c1_invisible` can reach total=7 — CONFIRMED

`probe-canon-base.py --repo <c1_invisible>`:

```
BASE_C1 canon_round=71 canon_rows=3
exit=0
```

Structural proof it can do nothing else: exactly one line of the fixture matches the frozen
regex `canonical list as of round\s+(\d+)\*\*` (r42 module lines 141-148) — line 9, the bold
round-71 heading. The two demonstrated tables (`### Capabilities demonstrated in round 73/74`)
do not contain the substring `canonical list as of round`, so `canon()` cannot match them at
any argument; over this file its only possible resolution is (71, 3):

```
$ python3 - <<'EOF'   # enumerate matches + hand census
canon-regex matching lines in c1_invisible: 1
  line 9: **Capabilities — canonical list as of round 71**
hand census (all table capability names): 7 ['digest-ledger', 'live-ollama-lifecycle', 'pin-watch', 'province-host-drift', 'receipt-claim-binding', 'round-scope-cases', 'sources-registry']
EOF
```

Hand census counts 7 distinct names (3 bold-71 + 2 demo-73 + 2 demo-74); canon() reports 3.
Control: the same probe over `c1_clean` (bold round-74 heading added) resolves
`BASE_C1 canon_round=74 canon_rows=7` — the base tool sees the full repertoire only when a
bold heading carries it, which is exactly R73-D1 and the frozen C1 hole.

### (b) C2 — the r73 counter cannot see wrapped/offset claims by line-level tweaks — CONFIRMED (5 escapes exit 0; 1 precise false positive)

Frozen line-scoping: `_claim_pass` (round73-receipt-claim-binding.py:197-212) lowercases each
line, requires a TIP_CLAIM_TOKEN on the line, and collects `TOKEN_RE` backtick citations from
that same line only; a line with a token but no citation `continue`s uncounted. Six tweak
variants were built as new commits on `cp -a` copies of the committed fixtures (toplevel
asserted before commit; fixture identity; receipt population untouched). Full receipt:
`receipts/c2-probes.out`. Verbatim results:

```
== c2_wrapped+comment ==    (HTML comment inserted inside the claim paragraph)
RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
exit=0
== c2_wrapped+case ==       (claim tokens uppercased: AT THE / REPORT TIP)
... claims=0 unbound_claims=0
exit=0
== c2_wrapped+reshape ==    (citation reshaped to section-relative `measured/a.out`)
... claims=0 unbound_claims=0
exit=0
== c2_offset+comment ==
... claims=0 unbound_claims=0
exit=0
== c2_offset+case ==
... claims=0 unbound_claims=0
exit=0
== c2_offset+reshape ==     (citation reshaped to bare `a.out`)
RECEIPT_TIP_FINDING stale .ufo/waves/round-74/a.out :: absent at f076b49e…
RECEIPT_CLAIM_BINDING round=74 cited=1 bound=0 unbound=0 shifted=0 stale=1 claims=0 unbound_claims=0
exit=1
== c2_wrapped+samelinedemo ==  (control: token + citation forced onto one line)
RECEIPT_CLAIM_FINDING stale-claim .ufo/waves/round-74/measured/a.out :: 6: report tip naming `.ufo/waves/round-74/measured/a.out`.
RECEIPT_CLAIM_BINDING round=74 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=1 unbound_claims=1
exit=1
```

Reading: five of six honest-bytes tweaks still exit 0 with `claims=0` — the claim remains
uncounted by ANY line-level game (comment insertion, case games, citation reshaping), because
the hole is paragraph-vs-line scope, not any token spelling. The one exit-1
(`c2_offset+reshape`) is a false positive reported precisely: the bare `a.out` citation
resolves section-relatively to `.ufo/waves/round-74/a.out` (r72 `_resolve_citation`,
round72-receipt-tip-binding.py:347-385), which does not exist at tip, so the BASE leg (not the
claim pass) flags `RECEIPT_TIP_FINDING stale`; `claims=0` shows the claim itself was still not
seen — the exit-1 reason is "citation path relocated to a nonexistent wave-root file", not the
wrapped/offset claim. The same-line control proves the r73 pass does grade a claim when token
and citation share a line (`claims=1`, stale-claim, exit 1) — so the five exit-0s are
line-scoping holes, not leniency.

### (c) C3 — r73 stays green on an edited block and on a history-scrubbed block — CONFIRMED (both exit 0)

Full receipt: `receipts/c3-probes.out`. Verbatim:

```
=== (i) r73 over c3_edited (date byte edited 2026-11-03 -> 2026-11-04, triple matches live) ===
PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
exit=0
--- c3_edited git log ---
861b6f4 edit the recorded date byte
00606f2 host block recorded at A
5740209 seed
--- block line at tip ---
Round-73 host-identity block (2026-11-04). Host triple: `uname -s` -> `Linux`; `uname -m` -> `x86_64`; `/etc/os-release` `ID` -> `arch`. recorded at 574020987a088484a311468d8dabfab9589eb299.

=== (ii) history scrub: recorded-at token DELETED from the edited block ===
--- scrubbed block at tip ---
Round-73 host-identity block (2026-11-04). Host triple: `uname -s` -> `Linux`; `uname -m` -> `x86_64`; `/etc/os-release` `ID` -> `arch`..
--- r73 over scrubbed fixture ---
PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0
exit=0
```

Reading: the r73 counter (frozen predicate, round73-province-host-drift.py:60) grades only
the newest block's triple vs the live triple and never reads git history, so (i) a date-byte
edit with matching triple is green — the base_green=1 hole the plan freezes — and (ii) even
after the `recorded at <rev>` token is deleted from the edited block (history scrub), the
counter stays green: nothing binds the block to its recorded revision.

**Fixture wrinkle (observation for L1/EX03DriftV2, not a freeze disagreement):** in the frozen
fixture the block's `recorded at <rev>` token names the SEED commit (`5740209…`), but the
block text first appears one commit later (`00606f2`); at the named rev the block does not
exist. The predicate's byte-identity check ("byte-identical block text at <rev> and at the
worktree tip", plan C3) therefore cannot require the block to exist at `<rev>` — under that
reading both `c3_clean` (must exit 0) and `c3_edited` (must exit 1) would be ungradeable.
The v2 leg needs a semantics that tolerates block-absent-at-`<rev>` (e.g. compare the block
as first committed against the tip, or treat absent-at-rev as clean) while still catching the
`861b6f4` date edit. The kill rule's expectations (c3_edited exit 1 edited-block, c3_clean
exit 0 edited=0) are still well-defined on the committed fixture bytes.

## (3) One named junk-row cheat per claim

All three cheat scripts are scratch-only demonstrations (never installed as
`tools/round74-*.py`), receipt: `receipts/cheat-demos.out`.

### C1 cheat — "total counting the bold canon + demonstrated rows without the invisible check"

Demonstrated: parses every capability table, prints `total=7` (correct) with `invisible=0`,
exit 0, on the kill fixture:

```
SELFDESC_CANON_V2 canon_round=? canon_rows=? demonstrated=? total=7 invisible=0
exit=0
```

Mechanically fails the frozen kill arm: `score-survivors.py:84` requires `rc == 1` and
`SELFDESC_CANON_V2_FINDING invisible` in the output — this cheat cannot be killed-as-fixed
because it never computes the invisible set (it even leaves `canon_round=?` junk).
**Forbidden by the frozen wording** (plan C1 predicate, verbatim): "`invisible` names every
capability a demonstrated-capabilities table newer than the newest bold canonical heading
carries while the bold canon does not, requiring `invisible=0` so the record never relies on
a form its own reconciler cannot see; it exits 1 naming each
`SELFDESC_CANON_V2_FINDING invisible <round> <name>`" — a counter that always prints
`invisible=0` names nothing and derives `total` without the demonstrated-minus-bold
comparison the receipt label requires.

### C2 cheat — "v2 hardcoding fixture paths"

Demonstrated: keyed on the fixture directory basename; emits canned findings/lines for the
four fixture names (all four frozen scorer expectations met mechanically: wrapped→exit 1,
offset→exit 1, mixed_honest→exit 0 with `bound_revisions=1`, clean_realizable→exit 0), and on
a genuine wrapped claim in an unrecognised repo (`lane-emu`) it exits 2 — it grades no
paragraph and opens no receipt.
**Forbidden by the frozen wording** (plan C2 predicate, verbatim): "every blank-line-separated
paragraph of the round's self-record … that both cites a receipt and carries a tip claim … has
every cited receipt whose own `tip=`/`rev=` header … names `<rev>`" and "a paragraph that names
an explicit 40-hex revision binds each cited receipt whose header equals that revision (hex
compared case-insensitively)" — the universal quantifier runs over paragraphs of any repo's
self-record; a path-keyed cheat binds nothing to any revision and cannot generalise, so its
receipt line is a junk row that merely prints the label.

### C3 cheat — "tip commit touched PROVINCE.md ⇒ edited-block"

Demonstrated: composes the r73 base leg, then flags `edited-block` iff the tip commit's
diff-tree touches PROVINCE.md. Passes both frozen arms mechanically (c3_edited exit 1,
c3_clean exit 0) and then **false-positives on an honest append**: appending a NEW
round-74 block (the plan's own prescribed honest answer to a host move) exits 1.
**Forbidden by the frozen wording** (plan C3 predicate, verbatim): "every host-identity block
carrying a `recorded at <rev>` token has byte-identical block text at `<rev>` and at the
worktree tip, so that a block whose recorded triple, date or any other byte changed after its
recorded revision is a finding even when the edited block matches the live triple" — the
graded object is the block's bytes at the recorded revision vs the tip; a diff-presence
heuristic compares nothing at `<rev>` and cannot distinguish an edit from an append, directly
contradicting the plan's "appending a new block remains the honest answer to a host move,
never editing."

## Receipts

All under this directory:
- `receipts/score-survivors-rerun.out` — before-receipt reproduction (sha256 == freeze pin `1a7903f3…`)
- `receipts/c2-probes.out` — six C2 line-level tweak variants + same-line control
- `receipts/c3-probes.out` — r73 over c3_edited and over the history-scrubbed block
- `receipts/cheat-demos.out` — the three junk-row cheat demonstrations
- `receipts/SHASUMS.txt` — sha256 of the above + rebuilt fixtures-meta.json

Scratch dir `/fast/scratch/hyaku/kama-r74/LAB01Controls/` deleted after receipts were copied.
No tools installed or upgraded; no pacman transactions (guard respected).
