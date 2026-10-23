# Round-27 frozen-counter mutation probe

## Result

Best frozen single-fixture score: **registered 2 / counted 2** (the genuine two-row pilot). **Meets target: no**; target remains 15. No low-work target-meeting control was demonstrated.

**13 killed / 2 survived / 0 inconclusive**, across 15 independently named mutant copies and 12 fixture cases. The 204 real counter invocations comprised 12 pristine, 180 mutant and 12 restored runs. Every invocation exited 0, stderr was empty, and there were no timeouts.

No frozen counter repair, predicate amendment, live source edit, integration, shipping, or alternate runtime was performed. Only this seat's sandbox and evidence directory were written.

## Control shape and expected detector

The fixture set contains the supplied two genuine pilot rows and deliberately defective variants. Each negative case violates exactly one clause, confirmed by its sole frozen `why` rejection; h has one accepted predecessor plus the rejected row. Cases are separate lanes so duplicate pilot-based faults cannot be masked by clause-h source/signature deduplication.

A kill requires an observable change in the frozen CLI output/exit on a baseline-valid case; counter hashes, lane filenames and nondeterministic HTTP body hashes are not the detector. An invalid pristine baseline would be inconclusive. Every pristine fixture had the expected acceptance/rejection, and every restored stdout/exit matched pristine.

The full detector is the same real counter CLI on every case: pinned binary/model/source checks, healthy baseline/help/version, real control and request HTTP calls, and frozen counting logic. There are no mocked responses or substituted binaries. Each invocation takes the shared `flock` and `timeout -k 15 900`; it also has an 8-GiB address-space ceiling, 180-second CPU ceiling and per-UID process ceiling 32768. One counter is active per runner.

By explicit parent decision, counter-owned servers use the counter's unchanged loopback ports 47600–47619 under the shared lock; the 47700–47799 restriction applies to hand-started servers. No server was started by hand and no PORTS override was used.

### Frozen fixture outputs and per-row reasons

All outputs below have exit 0. `why = []` means accepted. These are observations, not expected-output substitutes.

| Fixture | Frozen stdout | Per-row why |
| --- | --- | --- |
| `pilot` | `registered 2 counted 2 target 15 met False not-counted []` | `E27-90: []; E27-91: []` |
| `a_signature_cell` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: a:no-skill-row` |
| `a_path_cell` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: a:no-skill-row` |
| `a_next_words` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: a:no-skill-row` |
| `b_short_signature` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: b:short-or-bad-char` |
| `b_held_at_base` | `registered 1 counted 0 target 15 met False not-counted ['E27-92']` | `E27-92: b:held-at-base` |
| `c_missing_sources_row` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: c:no-new-sources-row` |
| `d_wrong_literal_line` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: d:not-a-literal-on-line` |
| `e_healthy_request` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: e:not-shown` |
| `f_casefold_request_echo` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: f:in-request` |
| `g_failed_control_status` | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `E27-90: g:control-failed` |
| `h_same_next_action` | `registered 2 counted 1 target 15 met False not-counted ['E27-91']` | `E27-90: []; E27-91: h:same-next-action` |

## Mutant → frozen output versus mutant output → verdict

Every mutant was exercised on all 12 cases. Killed rows below show one actual witness plus all changed-case names. A survivor had identical stdout, stderr and exit on the entire fixture set; its full case-by-case comparison is in `summary.json`.

| Mutant (clause) | Witness / all changed cases | Frozen stdout | Mutant stdout | Verdict |
| --- | --- | --- | --- | --- |
| `a_id_only_skill_row` (a) | a_signature_cell; changed: a_signature_cell, a_path_cell, a_next_words | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `a_no_path_cell` (a) | a_path_cell; changed: a_path_cell | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `a_no_next_action_word_minimum` (a) | a_next_words; changed: a_next_words | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `b_no_signature_shape_or_novelty` (b) | b_short_signature; changed: b_short_signature, b_held_at_base | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `c_no_sources_row_validation` (c) | c_missing_sources_row; changed: c_missing_sources_row | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `d_no_literal_binding` (d) | d_wrong_literal_line; changed: d_wrong_literal_line | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `d_error_token_window_to_file_start` (d) | pilot shown; all 12 cases identical | `registered 2 counted 2 target 15 met False not-counted []` | `registered 2 counted 2 target 15 met False not-counted []` | **survived** |
| `e_no_live_error_acceptance` (e) | e_healthy_request; changed: e_healthy_request | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `f_literal_case_sensitive_occurs` (f) | f_casefold_request_echo; changed: f_casefold_request_echo | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `f_no_request_surface_echo_check` (f) | f_casefold_request_echo; changed: f_casefold_request_echo | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `f_no_baseline_or_help_check` (f) | pilot shown; all 12 cases identical | `registered 2 counted 2 target 15 met False not-counted []` | `registered 2 counted 2 target 15 met False not-counted []` | **survived** |
| `g_no_control_result_check` (g) | g_failed_control_status; changed: g_failed_control_status | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `g_no_control_status_check` (g) | g_failed_control_status; changed: g_failed_control_status | `registered 1 counted 0 target 15 met False not-counted ['E27-90']` | `registered 1 counted 1 target 15 met False not-counted []` | **killed** |
| `h_no_uniqueness_checks` (h) | h_same_next_action; changed: h_same_next_action | `registered 2 counted 1 target 15 met False not-counted ['E27-91']` | `registered 2 counted 2 target 15 met False not-counted []` | **killed** |
| `h_no_same_next_action_check` (h) | h_same_next_action; changed: h_same_next_action | `registered 2 counted 1 target 15 met False not-counted ['E27-91']` | `registered 2 counted 2 target 15 met False not-counted []` | **killed** |

### Surviving mutants: coverage findings, not frozen-counter bypasses

- **(d) `d_error_token_window_to_file_start`** changes the four-line look-back to the entire preceding file. None of these fixtures has an otherwise-valid cited literal with no ERROR_TOKENS in the prescribed four-line window. Pilot E27-90 has its `throw` on the cited line, so this weakening is invisible. The suite does not exercise the window boundary.
- **(f) `f_no_baseline_or_help_check`** removes `f:in-baseline-or-help`. None of these otherwise-valid signatures overlaps the healthy baseline/log/help/version. The request-echo fixture E27-90 only exercises `f:in-request`, not this separate scan. The suite does not exercise baseline/help contamination.

No weakness in the unmodified counter was demonstrated by these two survivors. They identify missing fixture coverage, not permission to change C1 or claim that the frozen counter accepts bad rows. The uppercase nested-key echo witness kills both the literal-only occurrence mutant and the disabled-request-surface mutant; the failed-control witness returns a different error message, so disabling just control status is independently observable.

## Mutations and hashes

Each named copy changes one syntax-located behavior-bearing point. The whole frozen source, named mutant sources, individual unified diffs, exact replacement expressions and full mutated hashes are preserved in `frozen-count-c1.py`, `mutants/` and `mutants.json`.

Frozen original SHA-256, before and after:

`382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6`

| Mutant | Mutated SHA-256 | Restored SHA-256 |
| --- | --- | --- |
| `a_id_only_skill_row` | `4e7f30be26d761d7302c7e8b80927e58f27eec94763dfb1e6ad679b2eec5f82e` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `a_no_path_cell` | `c7f244966e56568fb37355b611f8ebb216d265fa806fd1a4d227ff933b2212a2` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `a_no_next_action_word_minimum` | `cc603d89b5aec883d61465b6db16e6e6d79420af5b64d98e8dc2edde8e4d9fd8` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `b_no_signature_shape_or_novelty` | `0c62b24af195851e562abc3141098e871ec74e10c080bf297fab302cefd8a54a` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `c_no_sources_row_validation` | `23ba10dca341dd41041160d65cf9f787e75d8fc182a55dfc6df8a673374c2e9e` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `d_no_literal_binding` | `502dad7a237db766a3d32b92e16a5d61d1b4888b3ecdd016d368b40b0cbe8a48` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `d_error_token_window_to_file_start` | `48f32d7eb05e1845af27b06143633fe4f5b5af1127b8263574e305aeebf53310` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `e_no_live_error_acceptance` | `8a7e080de863fc1e435153634c15de1499e03a41a6db9b6b02a0f0b631c1459a` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `f_literal_case_sensitive_occurs` | `f3f8003da251ab5a0f54d2342f18ed6293b6d8d4419dd0647f8337c2a8853b2f` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `f_no_request_surface_echo_check` | `bcc1770cb0b214aa1282cc78f50d1a5e34b4d2989e671092739ba9dbf14e9617` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `f_no_baseline_or_help_check` | `1489779b2670076584758c65fe4e36b82091f2f430352f459810ca54493ae14d` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `g_no_control_result_check` | `7fbf692adb7566cbfc5b3fb55439ece9328e48c39c353d68b9937a8107d1b9d6` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `g_no_control_status_check` | `096c40fa07d684f0d5bbf563ab73fda116fa1e01adc3cfb5b2a6e2b2dea56a80` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `h_no_uniqueness_checks` | `099bf2c14a8b8327168bf59fe3dec1f931928d248c84e2d6d37c63e78c837c61` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |
| `h_no_same_next_action_check` | `d6c0cd4ebe9244435280b68c9d1cb25843d9246feede3f48afb3c08f37461563` | `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` |

## Restoration and evidence

All 15 sandbox mutant copies were overwritten with the exact saved pristine bytes after scoring, and all 15 match the frozen SHA-256 byte-for-byte. The authoritative lane counter and sandbox frozen counter were never edited and retain that hash. Archived mutant evidence copies intentionally retain their named defects.

The full 12-case detector was then run on one actual restored scratch copy; all restored scratch copies are byte-identical, so the same restored-byte suite covers their common code. All 12 restored outputs/exit codes matched pristine. This is a shared pristine/restored baseline, not a claim of 15 additional restored sweeps. See `restoration.json` and `runs/restored/frozen/`.

All 204 counter runs exited normally and internally stopped their server process groups with port-closure checks. The supervisor had zero orphan groups to force-clean. No hand-started server or long-lived service remains from this probe.

Fixture and mutant input commit in the isolated sandbox: `80e073a473d6737419517cec041fac2535b3b300` (base `530eaa998735d226ec90cea9b0cf4242a6b9cb01`). The exact commit is exported into this evidence directory as `fixtures-commit.patch`; `fixtures-commit.json` records its scope. No git/jj writes were made in the lane or fleet repositories, as required.

- `fixtures/` and `fixtures.json`: all 12 SKILL/SOURCES/registry input cases and input hashes.
- `control-registry.json`, `control-skill-sources.diff`, `counter-stdout.txt`, `counter-exit-code.txt`, `receipt.json`: requested root pilot-control artifacts.
- `runs/<pristine|mutants|restored>/...`: every actual stdout, stderr, exit code, receipt and invocation metadata (including before/after hashes and cleanup).
- `baseline-attribution.json`, `summary.json`, `run-totals.json`: single-clause attribution, full comparison matrix and invocation totals.
- `provenance.json`, `restoration.json`: frozen commit/pins, bounds, port decision and exact restoration evidence.
- `run-probe.py`: the bounded detector driver; preserved evidence is not overwritten on rerun. Sandbox root SKILL/SOURCES/registry remain the intentional pilot fixture, not claimed lane changes.

## Tooling

No tools were installed or updated. The backend refused one asynchronous restored-run launch at its global background-job limit before running it; the same command was then run synchronously. This was not a behavioral detector failure and produced no additional counter invocation.

Report: `.ufo/waves/round-27/controls/KamaR27CtlCounterMutants/REPORT.md`
