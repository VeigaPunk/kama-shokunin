# FinalCase41 — PG42-unused-missing-blob-fabricated-in-notes-plain

VERDICT: PASS — no falsification found. At pin 92063cfc60e217fa7e2098c568578119b16a1b95 the current arm meets the registered
live expectation for PG42; its declared graded twin is None, so no twin document exists to compare. Scratch only
/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/; durable writes: this file + out/FinalCase41/ only.

PINS: auditor tools/report-landing-audit.py b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f (= registered producer
identity); grid promisor-grid.py 30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270; manifest
promisor-grid-expectations.json d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1 (= registered primary manifest);
population 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88, 47 graded + 1 open row (PG40); pinned PG41/PG42 manifest
entries byte-equal to oracle-snapshot-before-inspection.json (no expectation drift).

RUN A (1 cell): TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase41/tmp python3 tests/report-audit/promisor-grid.py --arm
current --case PG42-unused-missing-blob-fabricated-in-notes-plain --json --out <out/FinalCase41> --keep -> exit 0.
Premise verified by hand: the lane tree names notes/unused.txt blob b2c475fe… and `git cat-file -e HEAD:notes/unused.txt` fails (the
unused blob is genuinely absent); report Notes = "fake 0123…4567", absent from lane and fleet; Landed cites lane commit 9bad795e… (resolves).
RESULT: exit 1 (=expected 1); kinds ["unresolved-full-hash"]; defect token 0123456789abcdef0123456789abcdef01234567 ($fake resolved);
document status "failed", 1 uncorrected defect; met_amended true, met_original true; problems / amended_problems / original_problems
all []; objects_acquired {lane: [], fleet: []}; stderr empty; traceback, internal_error, timed_out, leaked all false; twin null =>
no twin document compared (no twin-equality claim is made).

RUN B (2 cells, the only other grid cell): same command plus --case PG41-unused-missing-blob-fabricated-in-notes-promisor -> grid exit 0,
graded 2, violations 0, twin_compared 2, twin_mismatch [], twin_equal True both directions, identical normalised verdict documents
(doc sha 4ebb742f50a6f295…), PG41 exit 1 met, no objects acquired.

CONTROL A (direct, pinned auditor, own fixture, no grid): two fixtures from the pinned builder
c_unused_missing_blob_fabricated_notes_plain differing only by drop=("unused_blob",): with hole vs without hole — exit 1 both,
documents_equal true (byte-identical), acquired {} both, stderr empty. The unused hole does not move the verdict at all.

CONTROL B (mechanism, pinned auditor functions, same fixtures): lane missing_ids={b2c475fe…} (the unused blob), lane opaque_ids=[],
unknown_citation(fake)=[], opaque_hole=None — neither refusal root fires, so the fabricated token's absence is a proved absence ->
unresolved-full-hash finding, exit 1. Matches oracle-supplement-2 ("Blob-only unrelated holes do not do so"); no blanket completeness precondition.

RESIDUALS: PG42's frozen, original and amended views coincide (all exit 1), so this cell cannot discriminate the amended policy — it is a
no-harm/control cell; discrimination lives in PG41 (policy) and the opaque-tree cells, not run here. Frozen arm not executed (current arm
only). Gitfloor H2 untouched, still open. No score promotion or self-admission; the original unknown-citation clause stays
WITHDRAWN/NOT-ACHIEVED. No tool installs, no network. PM08 not applicable (manual only).
