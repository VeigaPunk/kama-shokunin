# RowF13RefNamed — falsify report

Target: grid row `F13-ref-named-abbreviation` (fault) of
`tests/report-audit/repo-state-grid.py` at 245a37f69628c2c6bb29bbf17897d8fb5946c857.
Builder `f_ref_abbrev` (lines 371-378): lane commit LC cited in full plus a
fabricated 8-hex token `deadbee1`; a lane tag literally named `deadbee1` is
pointed at LC so `git cat-file -t deadbee1` resolves a commit. Expectation:
exit 2, stderr reason `names a ref` (CASES line 554, REASONS line 584).

## Verdict: row HOLDS for its fixture — but the channel is NOT closed

1. Premise real in frozen arm: YES, verified on an independently hand-built
   fixture (no grid import; fresh repos in /tmp/f13/w).
2. Expected outcome correct: YES, defensible (below).
3. Near variant current still gets wrong: YES — a ref whose target SHA
   *carries the cited prefix* evades the check and flips `failed`→`clean`.

## (1) Frozen arm — premise observed

Hand-built replica (shell, `git init -b master`, LC commit "round-1: work"
@1000 by kama-shokunin, fleet report citing `- <LC>` + `- deadbee1`,
`git tag deadbee1 <LC>`; premise `git cat-file -t deadbee1` → `commit`):

```
python3 /tmp/frozen-audit.py --lane-repo lane --fleet-repo fleet --json \
    --rounds 1 --no-errata     ->  exit 0, "status": "clean", defects: []
```

Frozen `lookup()` (frozen blob 4fe9339f…:tools/report-landing-audit.py,
lines 100-132) has no ref test at all: `cat-file --batch-check` resolves the
tag `deadbee1` to LC and the fabricated citation is laundered — repo-local
ref state turns a fabricated citation into a clean verdict. That is exactly
the axis-7 harm the row certifies; the grid's `frozen … NOT-MET` claim is
real (this arm exits 0 where fault expectation is 2).

Current auditor on the same fixture:

```
-> exit 2
could-not-evaluate: /tmp/f13/w/lane: citation deadbee1 names a ref
```

Mechanism: `tools/report-landing-audit.py:161-163` — bare `cat-file
--batch-check` returns `deadbee1` → LC's SHA, which does not start with the
token, so the resolution must have come through a ref. Matches expectation
(exit 2 + reason string `names a ref`).

## (2) Is exit-2-refusal the CORRECT expectation?

Yes, and it is the only honest answer available. `deadbee1` is genuinely
undecidable: it is a syntactically valid ≥7-hex abbreviation AND a real ref
name; git resolves refs before object prefixes (rev-parse rules 3-6), so
any "resolved" answer is a choice the *repository* makes, not the report
author. Exit 1 `landed-unresolved` would falsely claim the object is absent
(it provably resolves). Exit 1 `landed-ambiguous` would mislabel the kind
of ambiguity. Silent resolution (frozen's behavior) is precisely what lets
a repo-local tag launder fabricated citations. Exit 2 "could-not-evaluate"
matches the auditor's own exit contract (":43-45 — errors are never
verdicts") and the declared rule "ref-named citations are refused"
(:52). Correct, not merely what current does.

## (3) FALSIFIED near-variant: same-prefix ref target evades the check

The check is `if not peel and not parts[0].startswith(token)`. When the ref
target's own object id starts with the token, ref-resolution and
prefix-resolution are indistinguishable, and the refusal is skipped — yet
git still resolved through the ref, with observable consequence:

Fixture (/tmp/f13/vh, built by hand):
- `git hash-object -t commit -w` two commits sharing 7-hex prefix `2be3304`
  (CA=2be330488d0834256c845a1f9160155595a710a3, subject `note 19143`;
  CB=2be3304b4edad96f5ab3fc3f7bffba6e83e0591c, subject `note 33149`).
- `update-ref refs/heads/master $CA`; fleet report cites `- 2be3304`.

Observed (env -i PATH=/usr/bin GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1, current auditor at 245a37f6):

```
no tag:   cat-file --batch-check 2be3304 -> "2be3304 ambiguous"
          auditor -> exit 1, defects: landed-ambiguous, "status": "failed"
git tag 2be3304 $CA:
          cat-file -> 2be330488d… commit  (resolved THROUGH the ref)
          auditor -> exit 0, "status": "clean"   <— defect masked
frozen arm, tagged: exit 0;  frozen arm, untagged: exit 1
```

A single lane-local `git tag` suppresses a real `landed-ambiguous` defect —
the identical axis-7 violation class (repo-local ref state flips the
verdict) that F13's expectation certifies against, and it violates the
documented contract "ref-named citations are refused" (:52): this citation
*is* ref-named, git *did* resolve via the ref, and no refusal fired. The
row's graded fixture passes, but the channel closure is a coincidence-gated
heuristic, not a rule.

Secondary, same `lookup()` path — git-version fragility: on git 2.56.0,
`f72f8a6^{commit}` resolves the *unique* commit among a commit+blob
collision pair directly ("2be3304^{commit} missing" per the docstring at
:133 is no longer what git does). For a commit+blob prefix collision with
no ref at all, the peeled pass overwrites the bare-pass `ambiguous` with
`found` and the auditor reports clean (verified, /tmp/f13/va: `f72f8a6`
bare→`ambiguous`, `f72f8a6^{commit}`→commit, auditor exit 0). The selftest
survives only because its ambiguity pair is two blobs (:707-721, peel can't
disambiguate). Net: `landed-ambiguous` is now unreachable for
mixed-type ambiguity even before refs enter the picture — the bare-pass
result is designed to be visible but `status[token] = "found"` (:164)
blindly overwrites it.

Cheap sibling variants checked — all correctly refused (exit 2 +
`names a ref`), i.e. the common shapes are closed:
- `.git/deadbee1` pseudo-ref file (rev-parse rule 1) — refused.
- `git branch deadbee1` — refused.
- `git update-ref refs/deadbee1` (bare `refs/<name>`, rule 6) — refused.
- annotated tag `2be3304`/`f72f8a6` → commit (tag object SHA doesn't carry
  the token) — refused.

## Residual risk / not verified

- Whether the same-prefix-evasion should refuse (exit 2) rather than accept
  is arguable where no ambiguity exists (tag P → commit whose SHA starts
  with P, benign-looking accept at /tmp/f13/vb, exit 0) — but with a
  colliding object the defect masking above is unambiguous.
- Fleet-side mirror of the same-prefix trick: identical code path
  (repos=(lane, fleet), same `lookup`), so implied by code + mechanism, but
  not executed (my fleet fixture build broke on unexported identity vars
  mid-run; lane-side mechanism is already proven).
- Did not verify git-version floor claim for the `^{commit}`
  disambiguation change (host git is 2.56.0 only; auditor floor is ≥2.45 —
  the "git answers missing for an ambiguous short name" comment may be true
  on 2.45 and stale on 2.56).
- Frozen exits on variant fixtures were spot-checked (vh: 1 untagged / 0
  tagged) only.

## Files written

- This report: `.ufo/waves/round-23/falsify/advice/RowF13RefNamed.md`
- Scratch (outside lane): /tmp/f13/{build-f13.sh,variants.sh,grind.py,
  grind2.py,w,va,vb,vc,vd,ve,vf,vg,vh}, /tmp/frozen-audit.py,
  /tmp/probe/r, /tmp/kama-r23w2/RowF13RefNamed (clone, HEAD verified
  245a37f69628c2c6bb29bbf17897d8fb5946c857)

Tool installs: none.
