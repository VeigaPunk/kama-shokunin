VERDICT: confirm — the page gives "No tests were collected" = exit 5 and failures = exit 1, but it shows NO pytest release version; the only version token on it is the Sphinx generator's `9.1.0`.

# ScoutPytestExitCodes — recon: pytest exit-code convention (operability axis)

Page: https://docs.pytest.org/en/stable/reference/exit-codes.html — fetched 2026-10-20, HTTP 200
(`readthedocs-http-status` meta, HTML line 42). Quotes below are line-anchored in the served HTML
(saved at `/tmp/pyexit.html`, 2026-10-20; scratch, disposable).

## Answers to the assigned questions

### 1. Code for "no tests were collected"

> `Exit code 5:` — "No tests were collected"

URL lines 329–330. Verbatim HTML: `<dt ...>Exit code 5<span class="colon">:</span></dt>` /
`<dd ...><p>No tests were collected</p>`.

### 2. Code for failures

> `Exit code 1:` — "Tests were collected and run but some of the tests failed"

URL lines 317–318.

Note the phrasing: exit 1 explicitly requires that tests *were collected and run*. That qualifier is
the textual basis for the separation — failure is only claimable once something was observed.

### 3. Pytest version shown: none — this is a trap

- The page carries **no pytest release version** in its rendered body or footer. The only
  version identifier in the served HTML is the docs channel:
  `<meta name="readthedocs-version-slug" content="stable" />` (line 42). The version-selector text
  itself is injected client-side (`readthedocs-addons.js`, line 42), so it is absent from a
  server-side read.
- The page's only bare `9.1.0` is the **generator**, not pytest:
  `<!-- Generated with Sphinx 9.1.0 and Furo 2025.12.19 -->` (line 10).
  This is a live hazard: pytest 9.1.0 is also a real release (changelog 2026-06-13), so a grep-based
  reader would "confirm" a pytest version from a Sphinx comment and be wrong twice over.
- Pinning the release behind `stable` needs a **second** page:
  https://docs.pytest.org/en/stable/changelog.html line 316 — `pytest 9.1.1 (2026-06-19)` is the
  first (newest) heading. [INFERENCE] `stable` served 9.1.1 at access time; the exit-codes page
  itself does not prove it.
- **Consequence for the SOURCES row (S051–S053 per `build/make_spec.py:245`):** a row citing this
  page must record `stable` as the doc channel (or cite `changelog.html:316` for the release) and
  must not claim a version located on the exit-codes page. A `Gate` line quoting "9.1.0" here would
  be a fabricated version anchor.

### 4. Two lines: how "nothing observed" stays distinct from "failed"

1. pytest spends a **dedicated terminal status** on the empty run — exit 5, "No tests were
   collected" — separate from exit 1, "some of the tests failed"; the two are distinct members of
   the public `pytest.ExitCode` enum (`from pytest import ExitCode`, line 337), not a flag on 1.
2. But the distinct code is still **non-zero**, so the convention only buys disambiguation, not
   success: any consumer that tests `exit != 0` alone still scores "nothing observed" as failure —
   the same trap C1's gate exit 3 (`NOT-EVALUATED`) inherits.

## Full table as served (for the C1 comparison)

| code | text (<=25 words) | URL line |
|---|---|---|
| 0 | "All tests were collected and passed successfully" | 314–315 |
| 1 | "Tests were collected and run but some of the tests failed" | 317–318 |
| 2 | "Test execution was interrupted by the user" | 320–321 |
| 3 | "Internal error happened while executing tests" | 323–324 |
| 4 | "pytest command line usage error" | 326–327 |
| 5 | "No tests were collected" | 329–330 |
| 6 | "Maximum number of warnings exceeded" | 332–333 |

Preamble: "Running `pytest` can result in seven different exit codes" (line 312). The page also notes
the no-tests-collected code is project-overridable via the `pytest-custom_exit_code` plugin
(line 344) — upstream treats 5 as a convention, not a law.

## What this precedent does and does not buy C1

- **Supported claim (sourcing-safe):** "a mature test runner keeps 'nothing observed' distinct from
  'failed' by allocating it a separate non-zero exit code (5 vs 1, with distinct enum members), and
  scopes 'failed' to runs that actually collected and ran tests." That is exactly the shape of R4
  (today zero observation exits 1 — the anti-pattern pytest avoids) and of the v3 contract's split
  of `passed:false` (1) from could-not-evaluate (2).
- **Not supported (do not cite this page for):** the lane's specific numbering. pytest assigns
  2 = user interrupt and 3 = internal error, while v3 assigns tool 2 = could-not-evaluate and gate
  3 = NOT-EVALUATED. Only the 1-vs-5 pair transfers; 2 and 3 are a **direct semantic collision** for
  any pytest-aware reader (lane gate 3 would read as a harness fault). The v3 codes may be
  justified on their own grounds, not as "following pytest".
- pytest has **no per-check null**: one run yields one code. v3's `passed: null` + per-check
  `not_evaluated_reason` + `outcome` is strictly finer-grained than the precedent, so the precedent
  validates the *principle* (observation-emptiness is a first-class status) but under-specifies the
  receipt.

## Lane observations that bear on the sourcing decision

- The lane does not use pytest at all: no `import pytest`/`conftest`/`pytest.ini`/`pyproject.toml`
  anywhere (`grep` over the lane returned nothing; `ls pyproject.toml setup.cfg pytest.ini tox.ini
  conftest.py` → all absent). The harnesses are standalone `#!/usr/bin/env python3` scripts with
  hand-rolled codes (`tests/llamacpp-live/controls.py:1`, `tests/probe-verdicts/check.py:1`).
  So this page is **convention precedent, not an implementation dependency** — the same category
  `build/make_spec.py:220` asks CritSourcedClaim to rule on.
- The frozen tool already has a **fourth code the docstring omits**: `tools/kama-llamacpp-live.py:1023`
  `return 3` on model-digest mismatch ("refusing to launch"), while the header's `Exit codes:` list
  (lines 17–21) declares only 0/1/2; the `--model-sha256` help agrees with the code, not the header:
  `mismatch -> exit 3` (line 954). Under the v3 contract (tool exits 0/1/2 only) this path must be
  folded into 2 or re-declared — otherwise the "uncontrolled exit code" count stays non-zero after
  the round.
- The gate today emits no 3: only `return 0|1|2` in `tests/llamacpp-live/check-receipt.py` (lines
  1347, 1352, 1386, 1397, 1399). Gate exit 3 (NOT-EVALUATED) is genuinely new, so its collision with
  pytest's 3 is a documentation decision, not a legacy.

## Limitations

- Read-only recon; no lane gate, measurement, or frozen copy was touched; no port bound; no installs.
- Version claim for `stable` is a one-sample read of `changelog.html` at 2026-10-20 and is marked
  [INFERENCE]; the exit-codes page alone cannot pin a release.
- No quote here exceeds 25 words; all quotes are from the two pytest URLs named above.

## Sourcing row this recon can back (for SourcesPython)

- URL: `https://docs.pytest.org/en/stable/reference/exit-codes.html`, accessed 2026-10-20.
- Located quote: "Tests were collected and run but some of the tests failed" (exit 1, line 318) and
  "No tests were collected" (exit 5, line 330).
- Claim scope: **empty observation gets its own non-zero status, distinct from failure** — not the
  lane's numbering, not a version pin.
