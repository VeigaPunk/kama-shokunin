VERDICT: C2 matches its frozen predicate and hash, but its `upstream` ledger verdict makes calibration depend on live network availability and is not independently verified by the fixture.

## Evidence

- `tools/round53-cited-path-check.py:74-79` states the PREDICATE. `.ufo/waves/round-53/preregistration.json` claim C2 has the same sentence (predicate field); exact equality confirmed. The counter hash from `sha256sum tools/round53-cited-path-check.py` is `1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080`, equal to C2 `counter_sha256`.
- Predicate-to-code mapping: `fixture` is `fx = nfx == SCENARIOS` at lines 481, 486; `lane` is `lok` from `evaluate()` at 482; `undisclosed`, `bad`, `stale`, and `dropped` are computed at 362, 346-359, and 369-380. `met = bool(fx and lok)` at 487, and `lok` is false if any of the four lane counts is nonzero (`381`). No unrelated count or external criterion decides `met`.
- Fixture discipline: temporary fixture repo is created beneath the counter's scratch temp directory (`386-388`, `473`); fixture Git commands use `git -C D` (`393-397`); it checks `rev-parse --show-toplevel` resolves to D before fixture commits (`410-412`); Git author/committer identity and `GIT_CONFIG_GLOBAL=os.devnull` (plus `GIT_CONFIG_NOSYSTEM=1`) are set for fixture Git calls (`389-391`). Main code uses `git -C repo` (`115-119`); it does not mutate the measured lane. Scratch is removed in `finally` (`499-500`).
- The two pre-freeze changes are present: anchor grammar supports comma-separated values (`26-27`, regex line 106 and parse lines 162-165); `upstream` is a class (`107`) with a URL check (`298-311`). The disclosed ledger uses pinned raw GitHub URLs (`registry/cited-path-corrections.tsv:22-26`).

## Finding — Medium: upstream class makes `met` network-dependent and weakly re-derived

At `tools/round53-cited-path-check.py:304-310`, every upstream row verdict performs a live GET (60-second timeout); inability to fetch returns a failed row, which contributes to `bad` and therefore changes `met` (`353-357`, `381`, `487`). This is a calibration verdict that should be reproducible from the frozen lane/fleet snapshots. It also checks only HTTP status 200, not that fetched bytes correspond to the pinned source revision or the expected upstream file; the docstring calls it a class “the counter can re-derive from git history” (`6-7`, predicate `76-77`), while this branch does not consult Git history. The fixture's eight cases do not exercise `upstream` (`435-447`), so this special network-dependent behavior has no fixture guard.

Recommendation: do not let live network availability decide the measured calibration result. Pin the upstream evidence locally (for example, a committed expected digest plus a deterministic check against available evidence), or move fetchability to an explicitly non-gating diagnostic. If retaining a network check, validate fetched bytes against a frozen expected digest and represent unavailable network as “could not evaluate,” not as a bad ledger row. This is a recommendation; the frozen counter must not be altered for this review.

## Verification gaps

- No counter execution was performed; this was a static counter-vs-preregistration review. Hash, source lines, and predicate mapping were inspected as stated above.

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/V5Review.md`
