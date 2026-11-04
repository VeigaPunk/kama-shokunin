# EX03Accepted — C3 implementation

Axes: freshness (hash-bound historical grading), operability (explicit exit map and preserved audit verdict), calibration (pre-commit red is not called green).

## Files changed

- `tools/round75-append-accepted.py`: frozen C3 predicate verbatim; executes frozen audit JSON with exit 0/1 tolerated; optional `--audit-json`, `--register`, `--json`, `--selftest`; grades exact event/hash/count/class coverage and declaration bindings. Prints the audit summary without hiding `unrestored`. Exits 0 clean, 1 findings, 2 evaluation/CLI failure.
- `registry/append-only-accepted.tsv`: 389 mechanically generated hash rows covering 53 undisclosed events; commit subjects obtained by 42 successful `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --format=%s <commit>` calls (one per distinct commit). Each row preserves the audit's mechanical `in-place-edit` class. Notes distinguish the S547-backed CRLF->LF normalization reason from the other historical header/prose acceptance reason.
- `registry/append-only-declarations.md`: five explicit append-only declarations with reasons.
- `registry/append-only-contract.tsv`: only five `declared_at` cells changed.
- This report and its seat-trailer pointer report.

Largest event: `ea33a78f2b0bcbbebcde60d2851a81c54746baa8`, `corpus/SOURCES.md`, 639 deleted lines, **288 distinct undisclosed hash entries covering 362 lines**. 362 is a line count, not the number of register rows for that event. All events combined have 389 register rows.

## Retained measured evidence

Audit command (TMPDIR explicitly `/fast/scratch/hyaku/kama-r75/EX03Accepted`):

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --json
exit=1
schema=append-only-audit/v3 definition=v6
to=0908bab5cbf0ab6b435144fc525a3e18443dc08f
summary commits=576 files=143 events=223 restored=87 partial=0 unrestored=53 ungraded=78 disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0 ungraded_lines=330 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
```

The 576 commits include the freeze commit, unlike the base control's 575. JSON stdout SHA256: `782a6b681ff800d395785388673255fe8adcc8387e67166ed190d695de68a6db`. Its rows were consumed mechanically into the register; transient JSON was removed with scratch.

Real-lane operational command (same explicit TMPDIR):

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-append-accepted.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
exit=1
summary commits=576 files=143 events=223 restored=87 partial=0 unrestored=53 ungraded=78 disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0 ungraded_lines=330 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=5
APPEND_ACCEPTED_FINDING bad-declaration SCORECARD.md corpus/README.md:761: declared_at corpus/README.md:761 does not say append-only for SCORECARD.md
APPEND_ACCEPTED_FINDING bad-declaration corpus/QUALITY.md corpus/README.md:761: declared_at corpus/README.md:761 does not say append-only for corpus/QUALITY.md
APPEND_ACCEPTED_FINDING bad-declaration corpus/README.md corpus/README.md:761: declared_at corpus/README.md:761 does not say append-only for corpus/README.md
APPEND_ACCEPTED_FINDING bad-declaration corpus/SOURCES.md SKILL.md:578: declared_at SKILL.md:578 does not say append-only for corpus/SOURCES.md
APPEND_ACCEPTED_FINDING bad-declaration corpus/lessons/*.md corpus/README.md:1239: declared_at corpus/README.md:1239 does not say append-only for corpus/lessons/*.md
```

Frozen `tools/append-only-audit.py` SHA256 before (`sha256sum tools/append-only-audit.py`) and after (Python hashlib reading the same bytes), both:

```text
2b9285bfdeeeeda4ef763583ab1e869276ebd10202772630aaaca939f38ff4ee
```

## Integration dependency and disagreements

The frozen audit reads the contract and declarations from committed HEAD blobs. Therefore the real lane remains correctly red with five bad declarations until L1 commits the new declaration file and contract changes. No git/jj mutation was performed. [INFERENCE] After that integration commit, unchanged history and these binding declarations should produce `APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0`, exit 0. This is **not a measured green receipt**.

The freeze's detail requests appending declarations to `corpus/README.md`, while the assigned item requests `registry/append-only-declarations.md`. L1 explicitly ruled to follow the latter because SCR02 owns corpus/README; the predicate remains untouched. No historical corpus file or frozen tool was edited.

## Parent-owned checks (not run by this seat)

The fleet developer instruction forbids build/lint/tests/formatters during the editing wave and reserves post-integration checks to the parent. Consequently selftests and scratch fixture tests were implemented but **not executed**, despite the item requesting them. The real-lane operational counter above was executed as explicitly requested; its red result is retained, not suppressed.

Run after integration:

```text
python3 tools/round75-append-accepted.py --selftest
python3 tools/append-only-audit.py --repo . --json
python3 tools/round75-append-accepted.py --repo .
```

Selftest contains honest coverage plus wrong-hash, restored-event, wrong-class and 53-line/no-hash cheat arms, and additional short/excess count, unknown event, duplicate, missing-entry and bad-declaration arms. Each negative arm checks exit 1 and its finding class; parent must establish all are red and the overall selftest green. All contract declarations `ok=True` remains a parent check after committing.

LSP was unavailable: the mounted tool inventory exposes no LSP definition/reference/refactor interface. No supported symbol lookup was silently treated as an empty result. No tools installed or updated. One contract patch was rejected for an unrecognized snapshot anchor; a fresh ranged read supplied the real anchor and the patch then applied. The rejected edit changed no bytes.

## Self-evaluation

Accuracy 4/5: exact observed red verdict and unchanged audit digest retained; integration-green remains unobserved. Completeness 4/5: all scoped implementation paths supplied; parent-owned selftest/fixture proof remains pending by instruction. Clarity 4/5: measured and inferred outcomes separated; report is longer than the core receipt. Actionability 4/5: exact parent commands supplied; commit must precede real declaration grading. Conciseness 4/5: duplicate full finding lines retained for provenance. Overall 4.0/5. Highest-impact improvement is parent execution of selftests and post-commit audit/counter, not weakening the red pre-commit verdict. Would the user agree? Yes, subject to that explicit integration gate.

Scratch `/fast/scratch/hyaku/kama-r75/EX03Accepted` removed before terminal handoff. No live clone was made; no fixture git mutations were needed.
