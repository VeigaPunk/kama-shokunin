# F02C1ShowEndpoint — w2: A09 H3 reproduced; C1 `/api/show` fault is invisible to tool, verifier, and counter
Baseline gate: pristine tool fresh-nonce live run exit 0 MODEL_OK 16/16 checks, show 200 (findings/base.json).
v1 (one-line patched copy, `/api/show`→`/api/showX`, genuine v0.40.11 server 404s it): exit 0 MODEL_OK, captures.show={404,"404 page not found"}, 16/16; receipt differs from baseline only in show (p1.json).
v2 (genuine request, capture rewritten to 404 post-capture): exit 0 MODEL_OK, 16/16 (p2.json) — acceptance independent of how the 404 arose.
Verifier: pristine round60-c1-counter.py verify() accepts all three receipts (verify_bad=[]) and still accepts with captures['show'] deleted — REQUIRED has no show id, parses skip show, capture loop checks internal sha256 only.
End-to-end: scratch fixture repo, patched tip c9786681 (1-line diff vs pristine 09e82ddf): counter `live_ok=1/1 fake 2/2 stale 1/1 tamper 3/3 log 1/1 errors=0 met=True` exit 0 (counter-patched.out).
Freeze predicate does NOT require show: freeze.txt has zero "/api/show" (only the word "shown", line 47); C1-r60 = verifier acceptance + 7 controls rejected, errors=0.
"captures the HTTP surfaces (… /api/show)" exists only in tool docstring lines 9-10; no W1 rows.tsv quotes api/show; C2 counter's lone "show" is `git show` — no frozen instrument grades show.
Class-mates: v1-model-single and v1-models-empty are observations-only, statuses never graded anywhere (H3 is a class, not one endpoint).
Reading: C1-r60 as frozen is not falsified (insensitive by construction); the defect is docstring-vs-grading — grade show (status 200 + modelfile names qualified model) or document it non-graded like v1-models-empty.
Gaps: 200-with-malformed-body show faults untested; counter's own live receipt deleted by its rmtree. Evidence: findings.md + 3 receipts, patch.py, verify_run.py, 2 counter .out files in this dir; scratch removed, ports closed, lane untouched, no installs.
-- F02C1ShowEndpoint, 2026-10-27
