# R39-02 — C2 coverage pointer/no-op findings

## Axes
- **Coverage:** C2 is a narrow documentation/map addition; its 9→9 claim is explicitly non-promotional.
- **Calibration:** unchanged by this pointer/file/source-row predicate; no calibration evidence follows from the README pointer.

## Observations

- Frozen `preregistration-frozen.json` at base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea` defines C2 as three binary conditions: README round-39 coverage block names the amendment path, the amendment file exists at tip, and the amendment cites S472 which is present at tip and absent at base. The exact counter is README addition + file existence + S472 presence relative to base.
- Independent base lookups corroborated the negative control: the exact README pointer count was 0, `S472` count in base `corpus/SOURCES.md` was 0, and `git cat-file -e 6a4afdfe:corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` reported absent.
- In scratch tip `6a4afdfe` plus working changes, the exact predicate commands returned README pointer count 1, file present, and S472 row count 1. The visible README row maps that filename to the round-39 S472 `created`-metadata distinction; `SOURCES.md` contains the S472 row. Recorded `c2-noop.out` is `coverage_block=0 file_exists=0 cited_new=0 met=False exit=1`; `claim-after.out` records `round39_pointer=1 entry=1 S472=1` and base all-zero/false. This is a successful distinguishing no-op control for the frozen predicate, not evidence of any change in the numerical coverage score.
- The locally documented amendment says S472 is the OpenAI List models Markdown source and that `created` is catalog-creation metadata, not local serving identity. It explicitly says no current local endpoint or served artifact is inferred. This supports the scope boundary but does not demonstrate a newly covered runtime/capability surface.
- **Contradictory repository surfaces:** the lane scratch has the round-39 working changes, while `/home/vgpnk/Projects/shokunin/kama-shokunin` currently has no round-39 corpus pointer, no S472 row, no amendment file, and no round-39 SCORECARD section. Its w1 out directory already contains other attack reports. Thus the C2 predicate is met only in the lane's uncommitted working evidence; it is not yet observable in the integration-owner checkout. This is consistent with the scratch HEAD being exactly the frozen base and the changes being modified/untracked there, but it contradicts any statement that the integration checkout already contains them.
- The frozen predicate only establishes existence/presence and pointer naming. It does **not** test whether the new amendment adds substantively novel coverage beyond prior corpus/campaign knowledge, whether all claims in it are source-grounded, or whether capability/operability improves. Separate novelty assessment elsewhere reports the same distinction existed in the campaign artifact before this round; this points to possible thin novelty, not failure of the three frozen conditions.

## Bounded conclusion

C2's declared three-part binary predicate is reproducibly false at base and true in the scratch working state, so the no-op control distinguishes it. No contradiction was observed within that frozen predicate. The coverage increment remains a map/entry/source pointer at held score 9→9; substantive novelty and integration-owner landing are not established by this check. No calibration movement is evidenced. No change to predicates or repository content was made.

## Verification

Read-only observations: frozen and live preregistration, SCORECARD/LOG claims, base Git objects, scratch working files, exact predicate command results, and integration-owner checkout state. No tests, validation, installation, or commits performed.
