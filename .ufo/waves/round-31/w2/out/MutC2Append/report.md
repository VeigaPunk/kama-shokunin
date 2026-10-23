```RESULTS
All runs at kama lane commit 382d11b2107d335705875da1a4d889b074bd6fa6, from a fresh plain-git clone
at /tmp/kama-r31w2/MutC2Append/clone (clone git HEAD was bda324bb; the dispatch tip resolves there and
is its ancestor: `git merge-base --is-ancestor 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD` exit 0).
Frozen instrument: .ufo/waves/round-31/count-c2.py sha256 2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe
(re-verified after all runs). No server was started; no network used; no lane file was written.

[0] setup / read-only inspection
$ /usr/bin/git clone --quiet /home/vgpnk/Projects/shokunin/kama-shokunin clone
exit=0
  clone HEAD bda324bbc5c1d7db93553adb13c5f380492c3c93
$ /usr/bin/git rev-parse --verify --quiet 382d11b2...^{commit}   exit=0  -> 382d11b2107d335705875da1a4d889b074bd6fa6
$ /usr/bin/git merge-base --is-ancestor 382d11b2... HEAD        exit=0  (tip is an ancestor of clone HEAD)
$ /usr/bin/git rev-parse --verify --quiet 07794a4d...^{commit}   exit=0  -> 07794a4d30a54a60ebdff50ac76d12c6df40a0f1
$ /usr/bin/git show 382d11b2:SCORECARD.md > SCORECARD.tip.md     exit=0  1648 lines, sha256
  511b1fd8e979f037b490a5a2e354571c5ae6edbc35b15105574d0a5fcbddc849
$ /usr/bin/git show 07794a4d:SCORECARD.md > SCORECARD.base.md    exit=0  1570 lines / 117789 bytes
  prefix check: base is a byte prefix of tip (`startswith True`, suffix delta 7068 bytes)
$ /usr/bin/git checkout --quiet --detach 382d11b2107d3...        exit=0  working tree clean
  (base line 196 == tip line 196, so the round-10 rows I mutate lie INSIDE the base prefix)

[1] BASELINE — frozen C2 counter, unmutated bytes
$ /usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /tmp/kama-r31w2/MutC2Append/clone \
    --tip 382d11b2107d335705875da1a4d889b074bd6fa6 \
    --out /tmp/kama-r31w2/MutC2Append/receipt-baseline.json --list
exit=0
  rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
  tail (unresolved rows):
    C1: p1 line 266 p1:no-revision
    C1: p1 line 320 p1:no-revision
    C1: p1 line 379 p1:no-revision
  full stdout: baseline.out ; full JSON: receipt-baseline.json
  (reproduces the frozen reading in the round context verbatim)

[2] MUTANT A — one character in the round-10 C1 Claim cell (suggested mutation)
  file edit (clone only): `by appended dated corrections (plan claim 1) | freshness`
                       -> `by appended Dated corrections (plan claim 1) | freshness`
$ /usr/bin/git commit -am "mutant A: one char in round-10 C1 Claim cell"
exit=0   b304213ecb56dc9dcd3879e3529e953d95c1c0d9 ; SCORECARD.md sha256 668c6a165222dbd1f507ce5b...
$ frozen counter --tip b304213ecb56dc9dcd3879e3529e953d95c1c0d9 --out receipt-mutA.json --list
exit=0
  rows 30 base_mismatched 13 exempt 1 valid_corrections 9 false_corrections 1 unresolved 4 append_only False met False tip b304213ecb56
  tail:
    C1 — re-anchor stale source anchors by appended Dated corrections (plan claim 1): p1 line 196 p1:no-revision
    corr CR31:10:C1 re-anchor stale source anchors:p1 row=C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1) class=p1 ok=False
  met did NOT flip (False -> False); append_only True -> False; the correction key broke with the row id.

[3] MUTANT B — one character in the SAME row's measured cell (non-id), id kept intact
  file edit (clone only): `uncorrected stale-anchor rows 50 → 0 (42 active`
                       -> `uncorrected stale-anchor rows 50 → 1 (42 active`
$ /usr/bin/git commit -am "mutant B: measured number in round-10 C1 row (non-id cell)"
exit=0   3e1916e08b58b4486885bf236c80c7f40b806994 ; SCORECARD.md sha256 3c56a03af6bf4769...
$ frozen counter --tip 3e1916e08b58b4486885bf236c80c7f40b806994 --out receipt-mutB.json --list
exit=0
  rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only False met False tip 3e1916e08b58
  Every field but append_only is byte-identical to [1]; append_only True -> False. met did not flip
  (it was already False because of unresolved 3).

[4] MUTANT C — the attack append-only exists to stop: repair the three uncorrected rows IN PLACE
  three file edits (clone only), each appending the round's revision and an evidence path to the
  original row's last cell (lines 266, 320, 379):
    3285cdf7a50481694a36c4425cf32c915ab5e5f0 + .ufo/waves/round-11/acceptance.json
    33f46685b418af868259952884e34b93633820cb + .ufo/waves/round-12/acceptance.json
    641e1b6f1bef0e12d14c2e23388d7592ff0cb594 + .ufo/waves/round-13/acceptance.json
$ /usr/bin/git commit -am "mutant C: repair 3 uncorrected rows in place"
exit=0   dcae1977382e3da2ee2dacc89eefa79b7e72d191 ; SCORECARD.md sha256 f3384dba73d387a8...
$ frozen counter --tip dcae1977382e3da2ee2dacc89eefa79b7e72d191 --out receipt-mutC.json --list
exit=0
  rows 30 base_mismatched 10 exempt 1 valid_corrections 10 false_corrections 0 unresolved 0 append_only False met False tip dcae1977382e
  rows 30 (>=28), valid 10, false 0, unresolved 0 — the ONLY false predicate term is append_only.

[5] COUNTERFACTUAL INSTRUMENT — copy of the frozen counter with the append-only term neutralised
$ cp .ufo/waves/round-31/count-c2.py /tmp/kama-r31w2/MutC2Append/count-c2-no-append-clause.py
exit=0  (copy sha256 2d06f38d... identical to frozen)
  single line edit (copy only), line 270:
    `met = (rows_checked >= 28 and not unresolved and false_corrections == 0 and append_only)`
 -> `met = (rows_checked >= 28 and not unresolved and false_corrections == 0 and True)`
$ /usr/bin/python3 ./count-c2-no-append-clause.py --repo .../clone --tip <T>   (three tips)
exit=0 (each)
  T=382d11b...  rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
  T=3e1916e...  rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only False met False tip 3e1916e08b58
  T=dcae1977... rows 30 base_mismatched 10 exempt 1 valid_corrections 10 false_corrections 0 unresolved 0 append_only False met True  tip dcae1977382e
  full stdout: counterfactual.out

[6] MUTANT D — delete the appended correction section entirely
$ /usr/bin/git reset --quiet --hard 382d11b2107d3...   exit=0
$ head -n 1611 SCORECARD.md > sc-trunc.md && mv sc-trunc.md SCORECARD.md   exit=0   1648 -> 1611 lines
$ grep -c "claim-row evidence corrections" SCORECARD.md
exit=1 (zero matches — section gone)
$ /usr/bin/git commit -am "mutant D: delete appended correction section"
exit=0   332f20f01c8e4794dc514e1c04216f28bf4be57e ; SCORECARD.md sha256 91edc3cd1ab9c8bb...
$ frozen counter --tip 332f20f01c8e4794dc514e1c04216f28bf4be57e --out receipt-mutD.json --list
exit=0
  rows 30 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 332f20f01c8e
  append_only stayed True; the deletion is caught only by valid_corrections 10 -> 0 / unresolved 3 -> 13.

[7] RESTORATION — clone returned to its original bytes, lane instrument re-hashed
$ /usr/bin/git checkout --quiet --detach bda324bbc5c1d7db93553adb13c5f380492c3c93
exit=0
  git rev-parse HEAD        -> bda324bbc5c1d7db93553adb13c5f380492c3c93
  git status --porcelain    -> (empty)
  sha256sum SCORECARD.md    -> 511b1fd8e979f037b490a5a2e354571c5ae6edbc35b15105574d0a5fcbddc849
                               (identical to the 382d11b2 blob measured in [1])
$ sha256sum .ufo/waves/round-31/count-c2.py (lane)
  -> 2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe   (unchanged)
$ git -C <lane> status --porcelain | wc -l   -> 9  (all untracked other-seat/w2 artifacts; no tracked modification)
  Mutant commits remain addressable by hash in the scratch clone's object store.
```

FINDING: The append-only precondition is enforced by the frozen counter, not merely asserted — but it is enforced only over the base-commit prefix, and at the frozen tip it is not the term that decides `met`. A one-character in-place edit of an original claim row inside the base prefix flips `append_only` True→False with every other field unchanged (Mutant B); when the three uncorrected rows are repaired in place so that `unresolved` reaches 0, `append_only False` is the sole remaining false predicate term and neutralising only that term in an instrument copy yields `met True` (Mutant C + counterfactual). The suggested Claim-cell edit (Mutant A) additionally breaks the correction key (valid 9, false 1, unresolved 4) and, like B, does not flip `met` because the baseline already fails on `unresolved 3`; deleting the entire appended correction section leaves `append_only True` and is caught by `valid_corrections`/`unresolved`, not by the append-only property.

LIMITS: This probe exercises only the frozen C2 counter on SCORECARD.md at one tip (382d11b2); it does not run the C1 counter, any gate, the lane validator, or any live fixture, and it establishes nothing about C1 or C3. Mutant C is a constructed counterfactual state (three original rows rewritten in place, the ten reference corrections left intact); it is not the tip, it does not show the claim is met, and it is not an admissible repair — the frozen tip still reads `met False`. The counterfactual instrument (append-only term replaced by `True`) is a modified copy whose `met True` is inadmissible as a claim reading; it evidences only that the clause is the discriminator. The append-only property compares against the base commit's bytes only: it cannot detect in-place edits, deletions, or rewrites of bytes appended after 07794a4d (Mutant D is a 7,068-byte suffix deletion that passes `append_only`), so it is not a general immutability check. The collapse route by which a single appended correction naming row `C1` would resolve all three unresolved rows is noted but NOT tested here (separate defect, out of this item's scope). P1/P2/P3 semantics beyond what these arms exercise (e.g. P2-at-tip leniency, abbreviated-digest prefix acceptance) are untouched. The clone is a plain git clone of a jj-colocated lane, so jj state was neither measured nor mutated. No self-assessment, admission, or integration judgement is made; this is advisory evidence for the L1.

## Verdicts

| Arm | Mutation (clone only) | Frozen counter summary (exit 0) | Verdict |
|---|---|---|---|
| [1] baseline | none | `unresolved 3 append_only True met False` | measurement valid; reproduces the frozen reading |
| [2] A | 1 char in round-10 C1 Claim cell (`dated`→`Dated`) | `valid 9 false 1 unresolved 4 append_only False met False` | killed by append_only + correction-key mismatch; `met` unchanged |
| [3] B | 1 char in round-10 C1 measured cell (`50 → 0`→`50 → 1`) | `valid 10 false 0 unresolved 3 append_only False met False` | killed by `append_only` alone; all other fields identical to baseline; `met` unchanged (baseline already False) |
| [4] C | in-place repair of the three uncorrected rows (revision + evidence path appended) | `unresolved 0 append_only False met False` | killed solely by `append_only`; counterfactual [5] gives `met True` — decisive |
| [6] D | delete the appended correction section (7,068-byte suffix) | `valid 0 unresolved 13 append_only True met False` | append-only property SURVIVED (does not see suffix deletion); detected by `valid_corrections`/`unresolved` |

## What each observable proves

- `append_only` is the only field that changed between baseline [1] and Mutant B [3]: it is the sole observable of an in-place byte edit to the base prefix.
- `met` does not flip in [2] or [3] because the frozen tip already fails on `unresolved 3`; the append-only check is not the deciding margin at this tip. It becomes deciding exactly when the row-level checks pass ([4]).
- The counterfactual [5] isolates the clause: with `and append_only` replaced by `and True`, only [4] flips to `met True`; baseline and Mutant B stay `met False`. Therefore the append-only term is load-bearing, and its enforcement point is the base-prefix comparison in `main()`.
- Mutant D shows the boundary: `append_only` is a base-prefix check, not an append-only-history check; deletions in the appended region are policed by the correction/`unresolved` machinery instead.

## Restoration evidence

- Clone working tree clean at its original HEAD `bda324bbc5c1d7db93553adb13c5f380492c3c93`; `SCORECARD.md` sha256 `511b1fd8e979f037b490a5a2e354571c5ae6edbc35b15105574d0a5fcbddc849`, identical to the `382d11b2` blob measured before any mutation.
- Frozen lane counter `.ufo/waves/round-31/count-c2.py` sha256 `2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe` — unchanged.
- No tracked lane file was edited; `git -C <lane> status --porcelain` lists only untracked artifacts (other seats' receipts plus `w2/out/`).
- Mutant commits remain in the scratch clone object store by hash: A `b304213e…`, B `3e1916e0…`, C `dcae1977…`, D `332f20f0…`; diffs in `diffs.txt`, receipts in `receipt-*.json`, raw stdout/stderr in `*.out`/`*.err`, hashes in `hashes.txt`.

## Tooling

No tool install or upgrade was performed; nothing outside `uv`/`npx`/official-binary channels was needed. Only `/usr/bin/python3`, `/usr/bin/git`, and coreutils were used.
