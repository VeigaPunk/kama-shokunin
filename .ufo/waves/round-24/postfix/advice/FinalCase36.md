# FinalCase36 — PG36-unused-missing-blob-plain (postfix wave3, pinned 92063cfc60e217fa7e2098c568578119b16a1b95)

VERDICT: the registered result HOLDS at the pinned candidate — no defect found in this lane; one coverage caveat (PG36 cannot discriminate the two-root diagnosis's scoping).

Provenance (observed): clone `/fast/scratch/hyaku/kama-r24/postfix/FinalCase36/clone` (`git clone --no-hardlinks` from the local repo, no network), detached at the pin; `tools/report-landing-audit.py` sha256 `b9be4f42…3b26f` (pinned identity, equals `auditor_sha256` in every run), `tests/report-audit/promisor-grid.py` `30483830…3f270`, manifest `promisor-grid-expectations.json` `d86b7bea…14cd1` (= grid `MANIFEST_SHA256`, 47 cases + 1 open row PG40); python 3.14.8, git 2.56.0; no installs.

Executed (current arm only; cells = PG36 + its declared twin partner PG35):
1. `python3 tests/report-audit/promisor-grid.py --arm current --case PG36-unused-missing-blob-plain --case PG35-unused-missing-blob-promisor --json --out <out>` → grid exit 0, stderr 0 bytes. PG36: exit 0, `met_amended` true, `met_original` true, defects `[]`, kinds `[]`, reason_class null (stderr empty), document `summary.status=clean`, results[0] round 1 required 1 round_commits 1, `objects_acquired {lane:[],fleet:[]}`, twins `{PG35:true}` `twin_equal true`, `twin_mismatch []`, no traceback/timeout/internal_error/leak. Exit class vs registered expectation: same-verdict-exit (0→0).
2. Same selection with `--keep` (own TMPDIR) → exit 0, rows semantically identical (per-case dict diff empty). Fixture kept, origin untouched.

Premise verified independently on the kept PG36 fixture (`git --no-lazy-fetch` only): lane plain (no promisor config), one commit `9bad795e8e7cbabfa1b3e699c5b461ad62271391`, tree = `corpus/SOURCES.md 051975b0…`, `f 56d7b323…`, `notes/unused.txt b2c475fe…`; that unused blob is genuinely absent (`cat-file -e` → exit 1), the two cited blobs are present, fleet plain with one citation (the lane commit), no errata rows, no missing fleet objects.
Diagnosis visibility (walks replicated by hand): store-wide walk over all present objects → `?b2c475fe…` (the hole IS seen); root-pinned `--filter=blob:none` walk → no opaque hole; fleet → nothing missing. So exit 0 is not an artefact of an invisible hole.
Mechanism (clone source, read-only): the missing/opaque sets are consulted only through `unknown_citation()`/`opaque_hole()` called from `refuse_unknown()` and `apply_errata()` (tools/report-landing-audit.py:482-519, 641-647, 776-805) — i.e. only for a token no store resolves. PG36's single citation resolves → the diagnosis is never consulted → no completeness precondition; resolved citations keep the registered result.

Controls (new-source regression controls, NOT the candidate; mutant digests in `out/FinalCase36/run-summary.json`):
- C1 blanket completeness precondition at the audit entry (any unservable object refuses): auditor exit 2, refusal, no verdict document (`document null`, `defects null`), `met_amended false`, grid exit 1 → PG36 does discriminate "holes as audit-completeness precondition" (normal→refusal-2).
- C4 blanket precondition at the refusal site (resolved citation loses the registered result when any hole exists): exit 2 refusal, document null, `met false`, grid exit 1 → same regression class detected at the second site.
- C3 hole-blind diagnosis (`missing_reachable` returns empty sets): PG36 still exit 0 / met true → PG36 alone cannot distinguish "correctly scoped two-root diagnosis" from "no diagnosis at all".

Residual risk / gaps: PG36 is a no-harm control — it exercises no refusal path, so it gives no evidence that the two-root diagnosis excludes unrelated/unselected/opaque holes for UNRESOLVED citations; that power lives in the unresolved-token cells outside this lane (PG22/PG25/PG33/PG34/PG37, and the ungraded PG40 whose traversal scope is contested by manifest design) — not exercised here. Wrong-type/absent-citation retention is likewise outside this cell. Frozen arm not run (current-arm bound). No production writes beyond this advice file and `out/FinalCase36/`.

Report: .ufo/waves/round-24/postfix/advice/FinalCase36.md
