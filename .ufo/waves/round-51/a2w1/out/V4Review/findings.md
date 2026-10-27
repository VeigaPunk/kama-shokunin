# V4Review — C2 frozen counter

Verdict: the declared frozen revision does not contain the v6 counter described by this assignment; replaying that revision fails both legs before the v6 assertions can be exercised.

## High — counter at frozen tip is v5, so the frozen C2 predicate is not measured

Evidence: ran

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
 --repo /fast/scratch/hyaku/kama-r51/V4Review/lane \
 --tip 804bde75164444bdf0fe6783d7aa45774bf562bd \
 --scratch /fast/scratch/hyaku/kama-r51/V4Review \
 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V4Review/frozen-c2.out
```

Exit 1. Receipt shows `fixture=0 lane=0 scenarios=0/9`; fixtures call `--disclosures` and the tip's tool rejects it, and the lane tool reports `definition v5 threshold 20` (counter lines 162-167, 407-414; captured full output `frozen-c2.out`). This is consistent with the source at that tip being pre-build. It means the frozen tip specified for review cannot substantiate C2's v6 claim; importantly this is not evidence of a defect in the *post-build* v6 implementation. The review target needs an unambiguous built counter revision/receipt before claims about its implementation can be concluded.

## Review of requested implementation points

- `lane()` uses `--no-renames`, so rename records are intentionally represented as delete/add and do not require the two-path rename numstat form. However it decodes `--numstat -z` into text and naïvely splits each record on tabs (lines 306-312), unlike `append-only-audit.py:numstat` which uses `split(b"\\t", 2)` and surrogateescape. A declared contract path containing a literal tab is legal to its own NUL-delimited path machinery but makes this counter skip the record (`len(parts) != 3`), then later incorrectly reports the ledger row unseen or omits independent checks. This is a concrete parser mismatch, but the lane contract does not establish such a path, so it is residual risk rather than a lane-specific false verdict demonstrated here.
- `kept = parent-line Counter - deleted Counter` (351) correctly handles duplicate lines as a multiset for whole-file grading. It compares against the tip cache (352-359), matching the frozen predicate’s `tip - kept` bound. Cache keyed by path is valid because tip is fixed.
- Restricted-region branch (366-371) only bounds ledger counts against deleted graded-key counts; it does not independently prove exact unheld-at-tip counts. This matches the explicitly weaker frozen predicate for region-restricted files (docstring lines 45-47), not an implementation divergence.
- Class check compares all non-permitted deleted occurrences by hash (340-348); ledger class must be one of the possible per-occurrence classes. If identical bytes have different classes in one event, membership permits either class for ledger rows. Not demonstrated on lane data; the frozen rule defines class mechanically per occurrence but the ledger schema aggregates by hash, so mixed-class same-key edits are an ambiguity worth testing if present.
- `seen` records every applicable deletion event before checking whether tool event exists (314-315); ledger with a genuine deletion event can be recognized even when the counter discovers a missing tool event. No-event ledger keys are rejected (372-375).
- The fixture tally folds four bad-disclosure subcases into one scenario (252-256). With all four passing, `n` includes them individually and subtracts four then adds one, giving nine as intended; if any fails, the aggregate is not credited. Construction gives each case an isolated intended mutation. Since frozen tip lacks the `--disclosures` CLI, those expected cases never actually run there.

## Verification gaps

Semantic LSP status/references/definition/diagnostics were unavailable in this seat's tool environment; source inspection is not semantic-server evidence. The v6-specific fixture/lane behaviors cannot be validated against the assigned frozen tip. No proposed patch: no safely attributable implementation defect in the requested post-build v6 code was established from that revision.
