# C-WT1 observed (frozen base 0df800e) — wrong-type citation used as a Landed commit

Measured with the r23-base auditor blob `0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`
(sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`, identical to the
working-tree copy at measurement time).

Reproduce:

```
python3 .ufo/waves/round-24/build/out/CaseWrongTypeCitation/build_case.py \
    --out .ufo/waves/round-24/build/out/CaseWrongTypeCitation/results
python3 .ufo/waves/round-24/build/out/CaseWrongTypeCitation/prove_containment.py
python3 .ufo/waves/round-24/build/out/CaseWrongTypeCitation/capture_git_semantics.py
```

Fixture (deterministic; every timestamp is pinned):

| item | value |
|---|---|
| lane commit `LC` | `db796f8b820bf3825c58832419138cdba23206a7` ("round-1: work", kama-shokunin, author time 1000) |
| lane blob `T` (cited as a Landed commit) | `6e98d181389d343031fd578c6a775ce0889a8b0d` (`HEAD:f`, `cat-file -t` → `blob`) |
| fleet report | `.ufo/reports/round-1/kama.md`, first add at author time 2000, 239 bytes |
| report Landed section | cites `LC` and `T` (both 40-hex), no other hex token |

## Frozen results

| arm | marking | hole | exit | defect kinds | token | stderr |
|---|---|---|---|---|---|---|
| `full` | none | – | **1** | `landed-unresolved` | `6e98d181…8b0d` | – |
| `non-promisor-unrelated-hole` | none | unrelated missing blob | **1** | `landed-unresolved` | `6e98d181…8b0d` | – |
| `promisor-lane-only` | lane metadata only | – | **2** | – | – | `could-not-evaluate: …/lane-promisor-lane-only: partial clone (remote.origin.promisor)` |
| `promisor-fleet-only` | fleet metadata only | – | **2** | – | – | `could-not-evaluate: …/fleet-promisor-fleet-only: partial clone (remote.origin.promisor)` |
| `promisor-metadata` | lane + fleet metadata | – | **2** | – | – | `could-not-evaluate: …/lane-promisor-metadata: partial clone (remote.origin.promisor)` |
| `promisor-metadata-unrelated-hole` | lane + fleet metadata | unrelated missing blob | **2** | – | – | `could-not-evaluate: …/lane-promisor-metadata-unrelated-hole: partial clone (remote.origin.promisor)` |

`full` arm JSON summary: `defects=1`, `uncorrected=1`, `by_kind={landed-unresolved:1}`,
`unresolved-full-hash=0`, `landed-omitted=0`, `landed-ambiguous=0`,
`landed-section-missing=0`, `required_commits=1`, `cutoff=2000`, `post_report_commits=0`,
`status=failed`.

The `non-promisor-unrelated-hole` arm shows that an unrelated missing blob (referenced by a
post-report tree, deleted from the store, cited nowhere) does **not** change the verdict at
base: exit 1 with the same single defect. That anchors the P10 row — "any hole ⇒ unknown"
would be a candidate-introduced regression.

All fixture premises passed in every arm (`premises_ok=true`), and the object inventory of
both repositories was identical before and after the auditor ran
(lane 3 objects / 0 packs, fleet 6 objects / 0 packs) — no lazy fetch, no transport.

## Expected candidate outcome (r24)

All six arms: **exit 1**, exactly one defect, kind `landed-unresolved`, token `T`.
`exit 2` on the four promisor arms, or an extra `unresolved-full-hash` defect on any arm,
fails the case.
