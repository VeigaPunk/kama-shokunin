# FinalCase40 — PG41-unused-missing-blob-fabricated-in-notes-promisor (postfix falsification)
VERDICT: **PASS — no defect found** in the pinned candidate on this cell or its graded twin. Recommendation only, not an admission; the original unknown clause stays WITHDRAWN/NOT-ACHIEVED (Gitfloor H2 open, no score promotion).

## Pin and provenance (observed)
- Clone `--no-hardlinks` → `/fast/scratch/hyaku/kama-r24/postfix/FinalCase40/clone`, detached at exactly `92063cfc60e217fa7e2098c568578119b16a1b95` (`git rev-parse HEAD` = that OID); all fixtures/TMPDIR inside my own scratch.
- Producers executed (sha256): `tools/report-landing-audit.py` `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`; `tests/report-audit/promisor-grid.py` `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`; expectation manifest `d86b7bea…14cd1` (= grid `MANIFEST_SHA256`); population `612b0a74…ed88`, size 47. No proposal/default mutable producer. No tool installs (preinstalled python3/git only).

## Executed check (2 cells only, current arm)
`TMPDIR=<own> python3 tests/report-audit/promisor-grid.py --arm current --current tools/report-landing-audit.py --case PG41-unused-missing-blob-fabricated-in-notes-promisor --case PG42-unused-missing-blob-fabricated-in-notes-plain --json --keep --out <out>` → **exit 0**; violations 0, tracebacks 0, timeouts 0, harness_leaks 0.
- PG41 (observed): exit **1**, `met_amended=true`, `problems=[]`, kinds `["unresolved-full-hash"]`, defect `{kind: unresolved-full-hash, token: 0123456789abcdef0123456789abcdef01234567}` (= manifest `$fake`), reason_class null, stderr empty, `internal_error=false`, `objects_acquired {lane:[],fleet:[]}`.
- PG42 (observed): exit 1, met true, same kind/token, no acquisition.
- Twin: **both verdict documents exist** (no refusal) and are byte-identical after path normalisation (doc sha256 `4ebb742f50a6f295e4a766e812c41bdf51dadd9f91f54ba1dd4efcedec5c270e` both) → declared equality is a real document comparison, not two missing documents.
- Withdrawal visibility (observed): `original_view_unmet=["PG41…"]` / `withdrawn_original_failures=["PG41…"]`, `violations=[]`; the original exit-2 reading is reported unmet, not relabelled passed.

## Independent falsification of the two-root diagnosis (own fixtures, pinned auditor)
`probes.py` / `p7.py`; argv `python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo <fleet> --rounds 1 --json --no-errata`; all `objects_acquired` empty.
- P1 hole in the **other root** (fleet unused blob) + fabricated token in the fleet report, lane promisor-marked → exit 1, only `unresolved-full-hash`: an unrelated hole in either root is not a precondition.
- P2 **unselected** side-branch hole → exit 1, same single defect. Not a precondition.
- P3 **unused non-leaf** hole + unresolved token → exit 2, content-derived refusal naming the missing tree `33fd12ec…` (no `partial clone (`/`promisor pack`): the opacity rule still binds, and only on the unresolved path.
- P4 same opaque hole, all citations resolved → exit 0 clean, no refusal: no blanket closure precondition.
- P5 conclusively **wrong-type** citation (known blob) beside an unrelated hole → exit 1 with `landed-unresolved` for that blob: the finding is kept, not refused.
- P6 **resolved** full-hash citation beside an unrelated hole → exit 0 clean.
- P7 7-hex abbreviation prefixing the missing blob → exit 2 refusal naming that token; an unrelated abbreviation (`deadbee1`) → exit 1 `landed-unresolved`. Name-scoped in both directions.
- Static (observed): the diagnosis has exactly three call sites — `refuse_unknown` (full hashes, landed citations) and `apply_errata` — all reached only for tokens not `found`/`ambiguous`/`wrongtype`; `unknown_citation` matches `oid == token or oid.startswith(token)`; `opaque_hole` is consulted only after a token is unresolved. No global hole precondition in the source.

## Residuals / gaps (not exercised here)
- Registered neighbours PG22/PG37/PG44/PG47/PG48 and every other arm were **not** executed (lane bound: 2 cells); P3/P4/P5/P7 are my own fixtures, not those cells. P5's extra `landed-omitted` is fixture-induced (my Landed section replaced the real commit), not candidate behaviour.
- `[INFERENCE]` The 7-hex prefix boundary (P7) is defensible under git's abbreviation semantics but is not pinned by any registered cell; a coincidental prefix collision against an unrelated missing object would refuse. Gitfloor H2 open; preregistration `expected_after[3]` is not achieved by this cell.
- Raw evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/postfix/out/FinalCase40/` (`grid-current-pg41-pg42.json` +`.stderr`, `pg41-pg42-summary.json`, `population.json`, `candidate.json`, `probes.json`, `probes-p7.json`, `probes/*.json`); scratch `/fast/scratch/hyaku/kama-r24/postfix/FinalCase40/`.
