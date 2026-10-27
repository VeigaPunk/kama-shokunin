# Hexrun census receipts

Commands were run against the shared scratch clone `/fast/scratch/hyaku/kama-r51/X4Hexrun/lane`; lane was not modified.

## Frozen build rev, before proposed rows

`python3 tools/hexrun-census.py scan --repo <clone> --rev 138af25b963450b6520794995605fa7dbbcd87e0 --details`

```text
tokens=2051 distinct=340 lane_oid=232 md5_blob=1 upstream_ok=94 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=2
exit=1
detail: 9e38a3615cbe01719bb990390903c61faf39b0b2 len=40 occurrences=1 class=unknown
detail: f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 occurrences=2 class=unknown
```

Same summary appears in frozen `.ufo/waves/round-51/measured/hexrun-build.out` for tip `73bf2a7a17104a62a3e442912c8776cbd8dedbd5`: `unknown=2`, exit 1.

## Scratch fixture with both proposed rows and evidence

Fixture commit `480ff87e12dff2b80a60d1879789722c990a6400`, parent `138af25b963450b6520794995605fa7dbbcd87e0`; added only two evidence `.txt` blobs and two ledger rows.

`python3 tools/hexrun-census.py scan --repo <clone> --rev 480ff87e12dff2b80a60d1879789722c990a6400 --details`

```text
tokens=2051 distinct=340 lane_oid=232 md5_blob=1 upstream_ok=96 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=0
exit=0
detail: 9e38a3615cbe01719bb990390903c61faf39b0b2 len=40 occurrences=1 class=upstream_ok
detail: f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 occurrences=2 class=upstream_ok
```

## Existing round-50 evidence alternative

At the frozen build rev, `.ufo/waves/round-50/w1/out/X5Digest2/evidence/f8cdb853aaff29393faeb0b6d4c2a2296778b698.json` is already a blob (15,592 bytes) and contains both the token and `VeigaPunk/shokunin`. Using an override ledger with one row binding that evidence under repo cell `VeigaPunk/shokunin` classifies f8cdb853 as `upstream_ok`; output: `upstream_ok=1 ... unknown=106`, exit 1 (the override contains only a header and that one row, so other unledgered tokens are expected). Its companion `proposed-hexrun-ledger-row.tsv` is a draft, not a landed registry row: the frozen 109-line `registry/hexrun-ledger.tsv` has no f8cdb853 row. This alternative avoids adding a new evidence blob for f8cdb853; the two-row fixture above instead demonstrates a uniform round-51 evidence convention.

## Negative evidence-path control

An override row for 9e38a361 pointing at `registry/digest-ledger.tsv` yields `ledger_bad=1`, and its detail is `class=ledger_bad` (exit 1). This confirms the evidence path/token/repo checks are active.

## Tool and C2 preservation

`python3 tools/hexrun-census.py selftest` → `selftest pass=18 fail=0`, exit 0.

`python3 tools/round51-append-audit-v6-check.py --repo <clone> --tip 480ff87e12dff2b80a60d1879789722c990a6400 --scratch <scratch>` → `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0; lane detail: `tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58`.

Full output: `c2-on-fixture.out`. Census evidence files are under `evidence/`; proposed rows are in `proposed-hexrun-ledger-rows.tsv`.
