# ReviewSelftest — `kama-ollama-evidence.py --selftest` (round 14)

Static, contract-level review. No classifier, `cases.json`, or harness existed at review time:
`find` found no `tools/kama-ollama-evidence.py`, no `tests/ollama-evidence/`, and no
`cases.json` in the lane. Nothing was executed, built, or tested. Unrun != pass.

Sources: `.ufo/waves/round-14/spec.json` (items Classifier, Fixtures, Harness, ReviewSelftest),
`SKILL.md` lines 191-292 (served-id normalization, anti-patterns 3, 9, 10), and the round-12
precedent `.ufo/waves/round-12/advice/ReviewSelftest.md` (F1-F11) and round-13
`advice/ReviewExit.md` (F1-F3).

## Axes

A. Oracle independence: expected exit and ID come only from committed literals.
B. Child-CLI reality: the selftest exercises the real process boundary, not in-process helpers.
C. Vacuity: a zero, short, or malformed fixture set cannot pass.
D. Exit/ID discrimination: each case asserts both observed exit and observed finding ID.
E. Exit-code collision: selftest results cannot be mistaken for domain verdicts.
F. Spec determinism: every literal has one unambiguous expectation.

## Findings (severity order)

**F1 — high (axis E): selftest exit codes collide with domain verdict exits.**
The spec gives the selftest result `verdict_exit` 0/1. Exit 0 is the classifier's only
identity-positive code (`loaded_same_digest`). A selftest `clean` run therefore exits 0, and
a wrapper like `if tool --selftest; then …` reads it as loaded identity. A selftest failure
exits 1, the same code as `available_not_loaded`, `remote_inventory`, and `identity_conflict`.
Obligation: the selftest must not reuse the domain exit codes as its pass/fail signal, or
every consumer must be required to read `finding_id`. Owner decision; the contract does not
settle it. Recommended: selftest outputs a distinct schema (see F5), and its process exit
is reserved (for example 3 for `selftest_failed`, 0 only with `finding_id: clean`).

**F2 — high (axis C): vacuous pass.**
The spec requires `--selftest` to pass only when the child CLI matches the committed literals.
Nothing in the spec stops `cases.json` being missing, empty, truncated, or duplicated, which
would yield `passed=0 failed=0` and `clean`. Obligations:
- A missing or unparsable `cases.json` is `selftest_failed`, never `clean` and never skip.
- Count must be at least 16 (the Fixtures minimum), with no duplicate `name`.
- Each case must contain all six keys: `name`, `tags`, `ps`, `expect`, `expected_exit`,
  `expected_finding`. A missing key fails that case.
- Zero records executed is `selftest_failed`.

**F3 — high (axis A): oracle independence.**
The contract requires literals from `tests/ollama-evidence/cases.json`. The selftest must:
- compare observed exit to the case's `expected_exit` literal and observed `finding_id` to
  the `expected_finding` literal;
- never derive expectations from classifier functions, observed output, or a shared
  generator. Fixtures must author literals from the contract text, not by copying the
  classifier's output;
- not import the classifier in-process. Each case must spawn the child CLI.
Each record must also assert, for every case including the exit-0 case, `readiness == "unknown"`
and `scope == "offline-captures-not-runtime"`. The `loaded_same_digest` case is the one where
readiness could leak, so it needs this assertion most.

**F4 — high (axis F): spec ambiguities block literal assignment.** Any value Fixtures pins
becomes the oracle, so these need one owner decision each before cases are written:
1. Remote plus digest conflict. A remote tags or ps marker gives `remote_inventory` "regardless
   digest", but "differing matching digests" gives `identity_conflict`. Which wins when both
   hold? [Recommended: `remote_inventory` wins, because the spec says "regardless digest".]
2. Duplicate selected entries with differing digests. The spec says duplicate selection fails
   closed to `unknown`/`invalid_input`, but also says differing digests give `identity_conflict`.
   [Recommended: duplicate selection wins, giving `invalid_input`, because uniqueness is a
   precondition for any identity comparison.]
3. Name vs model conflict within one selected entry where one field equals `--expect`. Is it
   `identity_conflict`, or an alias match? The spec does not decide this.
4. Exit-2 IDs. `unknown` and `invalid_input` share exit 2. Each fixture must pin the ID, not
   just the exit.

**F5 — medium (axis E): output schema namespace.** `finding_id` is the verdict key on the
classifier output (`loaded_same_digest`, …) and also the selftest result key (`clean` /
`selftest_failed`). The selftest result also lacks `readiness` and `scope`. Use a distinct
schema name such as `kama-ollama-evidence-selftest/v1`, so a selftest record cannot be parsed
as a verdict.

**F6 — medium (axis A/C): discriminating literals for normalization.** SKILL.md step 2 applies
GGUF basename and `.gguf` stripping, and anti-pattern 3 is the raw-string trap. The classifier
must not reuse that rule. Required literal cases, each expecting `unknown`/exit 2 unless noted:
- `--expect Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` vs a tags `name` of
  `/scratch/models/…/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS.gguf` with the same digest;
- a case-variant `qwen3-…` vs `Qwen3-…`;
- an exact alias match (model field equals `--expect`, name differs, one selected entry),
  pinned to whichever decision F4.3 reaches.
Without these, an implementation that imports the probe normalization passes the selftest.

**F7 — medium (axis B): child-process hygiene for the selftest.** Round-12 F1, F11 and round-11
`measure.py:576-578` apply: `sys.executable` plus `Path(__file__).resolve()`; `cwd` set to the
temp dir; `timeout=` on every child; a scrubbed environment; and `OSError`,
`TimeoutExpired`, and JSON-decode failures recorded as failed records, not tracebacks. A child
that exits 0 with empty stdout, or non-JSON stdout, is a failed case. The selftest must never
pass `--selftest` to its child (recursion).

**F8 — medium (axis D): exact stdout and stderr.** Each record should assert that stdout is
exactly one JSON object and that stderr is empty for exit 0/1 cases. Exit-2 cases assert the
literal ID and empty traceback text. A mismatch on either exit or ID fails the record; neither
is sufficient alone.

**F9 — medium: write scope.** The shared interface says "no writes beyond stdout", but the
child CLI takes file paths, so the selftest has to write temp inputs. State that carve-out
explicitly: writes only inside `tempfile.TemporaryDirectory`, removed on every exit path. It
must never write or read the committed `cases.json` or any repo file, other than reading
`cases.json`. This mirrors round-12 F9.

**F10 — low: duplicate oracle.** `measure.py` and `--selftest` both run the same `cases.json`.
The contract allows both, but they must not share a comparison helper, or a common-mode error
passes both. Recommended: keep one comparison definition, and have the harness be the gate
(as the Harness seat already states).

## Not verified / gaps

- No selftest, child invocation, fixture, or harness was run. Every finding is from the spec
  text and precedent.
- Registry rows for the classifier (`L1 documents map`) do not exist yet. Not checked.
- The pending classifier and fixtures may already resolve F1-F4. Re-review against the actual
  files when they land.

## Recommendations to owners (bounded)

- Classifier (`KamaR14.Classifier`): F1, F2, F5, F7, F9. Use an empty-vacuity guard, child-only
  execution, and a distinct selftest schema.
- Fixtures: F3, F6, and the F4 decisions once made. Literals from contract text only.
- Main: F4 decisions (remote vs conflict precedence; duplicate vs differing digests; name vs
  model in one entry; selftest exit reservation for F1).

Tools installed or updated by this seat: none.

## Addendum — L1 rulings (KamaR14, received after review)

Rulings adopted as the oracle; they supersede the recommended defaults in F4:

1. Order: schema validity and duplicate selected entries first -> `invalid_input`, exit 2.
2. Selected name/model nonempty conflict -> `identity_conflict`, exit 1, even when a remote marker is present. This differs from the F4.1 default in this report, which had remote winning. Ruling stands.
3. Then a valid nonempty `remote_model` or `remote_host` string in either selected entry -> `remote_inventory`, exit 1, before unequal digest.
4. Missing or invalid digest is malformed -> `unknown` exit 2 or `invalid_input` exit 2, per an owner policy not yet pinned. Literals for this case cannot be written until that policy is pinned.
5. Otherwise differing digest -> `identity_conflict`, exit 1.
6. Selftest outer `clean` 0 / `selftest_failed` 1 is accepted as intentional. F1 is downgraded to a documented residual risk: any consumer reading only `$?` can still misread selftest exit 0 as `loaded_same_digest`. The distinct `finding_id` and record schema (F5) remain required.

Open after rulings: the digest-missing owner policy (ruling 4), and the exact "nonempty conflict" test (both fields present and unequal, or either present and unequal). Owners: Classifier (`KamaR14.Classifier`) for the implementation, and the Fixtures owner for literals.
