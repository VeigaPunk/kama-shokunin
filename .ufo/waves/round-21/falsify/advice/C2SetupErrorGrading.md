VERDICT: partial - setup-error receipts gate INVALID (exit 1) and the new defaults add no link problems, but `install_links_sha256: null` with `{}` grades VALID on a complete run and no selftest case covers the setup_error rule.
Attacked: check-receipt.py setup_error and install_links grading at committed a6617149 (lines 307-310, 442-458, 1474-1496, 2372-2383) against the producer initial receipt dict (tools/kama-llamacpp-live.py 1305-1342) and its install-tree-unpinnable raise (1375-1379). Analysis used a scratch clone pinned to a6617149 (deleted). Lane files were not edited; one read-only `git status` was run on the lane (may refresh the index stat cache, no content change).

## Hand-built receipts
Base: committed .ufo/waves/round-21/runs/b76727f3/live-receipt.json (blob e1fc04ab...). Fixtures in out/C2SetupErrorGrading/; full gate output in gate-runs.txt.
- base, unmodified: VALID, exit 0.
- setup-error-faithful.json (producer raise-state: setup_error set; server, probe.sha256, tool.sha256 and checks at initial defaults): `INVALID ...: 33 problem(s)`, exit 1. Line 1: `setup_error is 'install-tree-unpinnable:glibc-hwcaps:not-regular-or-symlink' (a complete run has setup_error null)`.
- setup-error-only.json (base + setup_error + outcome 'setup-error'): `INVALID ...: 1 problem(s)`, exit 1.
- setup-error-null-links.json (as above + install_links {} and install_links_sha256 null): `INVALID ...: 1 problem(s)`, exit 1.
- setup-error-outcome-pass.json (outcome 'pass'): `INVALID ...: 2 problem(s)`, exit 1 (adds `outcome 'pass' != re-derived 'setup-error'`).
- complete-null-links.json (setup_error null; links {} / null): `VALID`, exit 0.
- complete-null-tree-digest.json (install_tree_sha256 null): `VALID`, exit 0.
- empty-checks-setup-null.json: `INVALID ...: 17 problem(s)`, exit 1 (`outcome 'setup-error' != re-derived 'pass'`).
- internal-fault-nonstring.json (internal_fault 5): no verdict line; Python AttributeError at check-receipt.py:1480; exit 1.
- Pins: complete-null-links + --expect-install-links-sha256 <committed digest> -> INVALID, exit 1; + --require-install-links -> VALID, exit 0.
- Selftest on the pinned gate: `selftest: 11 VALID and 1 NOT-EVALUATED ... 91 mutations`, exit 0.

## Answers
1. Setup-error grading is one rule: any non-null setup_error hits bad() (307-310); INVALID is printed and exit 1 returned (2372-2376). Never VALID (2382) or NOT-EVALUATED (2380). The string is opaque to the gate and printed via !r. The derived outcome is 'setup-error' (1486-1487), matching the producer's outcome, so no other rule fires for a complete-looking receipt (setup-error-only: 1 problem).
2. The new defaults add nothing to setup-error grading: install_links {} / null passes via allow_none=not links (455) with an empty loop (setup-error-null-links = setup-error-only = 1 problem). The faithful shape's extra lines come from the empty install_tree (390-392) and null realpath/sha256/probe/tool, not from links.
3. The defaults are NOT consistent with the gate's own contract for complete receipts: see F2.

## Findings
F1 Medium - setup_error rule has no selftest case. Scratch mutant without lines 308-310 (out/C2SetupErrorGrading/mutant-no-setup-error-rule.diff): --selftest exit 0; setup-error-only.json -> VALID, exit 0; setup-error-null-links.json -> VALID, exit 0. The producer's full faithful shape stays INVALID only via 32 incidental problems. The selftest's only setup_error key is base null (1771); v3-internal-fault-not-mirrored (2166-2168) exercises the mirror rule, not this one.
F2 Medium - install_links null leniency. Line 455 `allow_none=not links` (added a29bb84, round 21) accepts a null digest with an empty map: complete-null-links VALID (exit 0), and VALID with --require-install-links. This contradicts the comment at 442-444 ("every soname symlink must be recorded, digested"). The producer cannot write it: install_links() returns digest None only with problems (pure call on an unlistable dir: `({}, None, ['listdir:No such file or directory'])`), and a complete run records links_digest({}) = 44136fa3..., which the gate recomputes identically (pure check: equal, exit 0). Only --expect-install-links-sha256 catches it. The selftest covers only the non-empty null case (1994-1995). Candidate fix, not applied or tested: allow_none=False at 455 [INFERENCE: no regression run].
F3 Low, pre-existing - same leniency for the tree: allow_none=True (411; first commit with the string b8e485c, round 16). complete-null-tree-digest VALID, exit 0. Comment 407-408 says null only when listing fails, which a complete run never records (install_tree returns None only at 186-187; install_links then raises at 1378).
F4 Low - non-string internal_fault crashes the gate (1480): traceback, no verdict line, exit 1. The producer cannot write it (_record_internal writes 'internal:<Type>' strings, 932-934).
F5 Low, latent - empty checks: producer _outcome_exit([], None) = ('setup-error', 2) (pure check, exit 0; line 928) vs gate derived 'pass' (1492-1493). Not producer-reachable [INFERENCE: no early return in main()'s try region (grep 1288-1749); every normal completion appends checks at 1494-1554].
N1 Note - exit-code overlap. Producer: 0 pass, 1 fail, 2 not-evaluated, 2 setup-error (916-928). Gate: 0 VALID, 1 INVALID (setup-error lands here), 2 unreadable (2349), 3 NOT-EVALUATED (2381). Consumers must not mix the two tools' codes.
N2 Note - the gate reports setup failure as a generic INVALID with no separate classification. The message does say why ("a complete run has setup_error null").

## Verification gaps
- Producer main() not executed (bounds: no live launch). The faithful fixture is hand-built; build_fixtures.py ast-checks it against the producer's initial dict (31 top-level, 8 server keys, 27 literal defaults equal; exit 0). Runtime emission shape is [INFERENCE] from 1375-1400, 1561-1562, 1704-1705.
- Scope is committed a6617149 only. The lane working tree has uncommitted modifications (`git status`: M tests/llamacpp-live/check-receipt.py, tests/llamacpp-live/install-links-grid.py, tools/kama-llamacpp-live.py, tools/report-landing-audit.py). I did not analyze them; a verdict on the working tree may differ from these findings.
- install-links-grid, install-tree-grid and the official run were not re-run.

## Commands (exits)
git clone + checkout a6617149 (0); gate --selftest on the pinned gate (0); gate on base (0); build_fixtures.py (0); run_gate_matrix.sh (0; per-case exits in gate-runs.txt); check_producer_gate_pure.py (0); mutant --selftest (0); lane `git status --porcelain` (0).
Tools: none installed; /usr/bin/python3 3.14.8 used as-is.
Artifacts: out/C2SetupErrorGrading/ - build_fixtures.py, check_producer_gate_pure.py, run_gate_matrix.sh, 9 fixture JSONs, MANIFEST.sha256, DIFFS-vs-base.txt, build-output.txt, gate-runs.txt, pure-checks.txt, mutant-no-setup-error-rule.diff.
