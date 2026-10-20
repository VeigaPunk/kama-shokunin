# CaseAudit15 — cases 30/31 vs the landed duplicate-corpus guard

Seat `KamaR15.CaseAudit15-3`, scout, read-only. Reviewed 2026-10-20 (UTC). No code,
runner, selftest, or verification command executed; no tools installed or upgraded.
No file written except this one.

## Reviewed state (pinned by sha256)

| Path | SHA-256 | Note |
|---|---|---|
| `.ufo/waves/round-14/measure.py` | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` | landed duplicate guard present, lines 350-364 |
| `tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` | matches round-14 `advice/Classifier.md` |
| `tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` | 51 entries, 51 unique names |

## Assigned cases (zero-based indexes 30, 31)

### Case 30 — `invalid_missing_tags_input`

```json
{"name": "invalid_missing_tags_input", "tags": null,
 "ps": {"models": [{"name": "llama3:8b", "model": "llama3:8b",
   "digest": "sha256:1111…1111"}]},
 "expect": "llama3:8b", "expected_exit": 2, "expected_finding": "invalid_input"}
```

### Case 31 — `invalid_remote_tags_with_missing_ps_input`

```json
{"name": "invalid_remote_tags_with_missing_ps_input",
 "tags": {"models": [{"name": "llama3:8b", "model": "llama3:8b",
   "digest": "sha256:1111…1111", "remote_model": "llama3-cloud"}]},
 "ps": null,
 "expect": "llama3:8b", "expected_exit": 2, "expected_finding": "invalid_input"}
```

Both literals are consistent with the code path below: `invalid_input` maps to exit `2`
in `tools/kama-ollama-evidence.py:91-98` (`FINDING_EXIT`).

## Exact branches

### Harness staging (`measure.py`)

- `measure.py:226-229`: `if case.get("tags") is not None` / `if case.get("ps") is not None`
  — a JSON `null` leaves the per-case `tags.json` / `ps.json` **uncreated**.
- `measure.py:230-233`: `argv` always passes **both** `--tags <path>` and `--ps <path>`,
  plus `--expect`. So the child sees two non-empty path strings; the absent file is the
  only signal. Case 30: `tags.json` absent, `ps.json` present. Case 31: `tags.json`
  present, `ps.json` absent.

### Classifier (`tools/kama-ollama-evidence.py`)

- `_run` at 483-514: `if not args.tags or not args.ps or not args.expect` (499) is false
  because both path strings are non-empty; the `missing_required_argument` branch (500)
  is **not** taken.
- 504-505: `tags_document = read_json_file(args.tags, 'tags')` runs first, then
  `ps_document = read_json_file(args.ps, 'ps')`.
- `read_json_file` 137-142: `os.open(...)` raises `OSError` (ENOENT) →
  `_fail(f'{label}_input_unavailable')`.
- 506-508: `except InputError as exc:` → `emit(classify_payload(args.expect,
  'invalid_input', [exc.code]))` → `return FINDING_EXIT['invalid_input']` = `2`.
- `classify_payload` 267-276 sets `verdict_exit = FINDING_EXIT['invalid_input']` = `2`,
  `schema = 'kama-ollama-evidence/v1'`, `readiness = 'unknown'`,
  `scope = 'offline-captures-not-runtime'`; `reasons` = the code token plus the two
  `CONSTANT_REASONS`. The harness does not assert reason text.

**Case 30 branch:** `tags_input_unavailable` (142, label `tags`). The `ps` file is never
read; `validate_capture`/`classify` are never entered. Exit 2 / `invalid_input`.

**Case 31 branch:** tags read succeeds (`read_json_file` parses JSON only; shape
validation happens later in `classify` → `validate_capture`), then `ps_input_unavailable`
(142, label `ps`). `classify` (218) is never entered, so the `remote_model` marker on the
selected tags entry is **never evaluated**; the remote branch inside `classify`
(`_remote_marker` → `remote_inventory`, exit 1) cannot fire. Exit 2 / `invalid_input`.

The literal expectations are therefore not merely compatible — they name the only branch
reachable for each case. Case 31 is the deliberate control proving remote-marker
precedence does not survive a missing ps input.

## Why the new corpus duplicate guard cannot alter these results

Landed guard, `measure.py:350-364`:

```python
declared = []            # only dict cases with a non-empty stripped string name
...
unique = len(set(declared))
problems = []
if len(declared) != unique:
    problems.append("duplicate case names")     # 358-359
if unique < MINIMUM_UNIQUE_CASES:               # 360-363, preserved
    ...
return problems, unique
```

Call site and ordering, `measure.py:367-385`: `corpus, unique_names =
corpus_problems(cases)` at 374; `if corpus:` at 377 records `unmeasured_record(...)` for
every case and skips the `elif tool_present:` branch at 381. The only child spawn in the
file is `subprocess.run` at 240 inside `measure_case`, which is reached only from 381-385.
`tool.is_file()`/`sha256_file` at 371-372 are filesystem reads, not processes. So a
rejected corpus spawns **zero** children, as the docstring (lines 13-14) and `LIMITS`
(line 77) promise.

For the original corpus the guard is inert:

1. **Name facts (data, not execution):** `cases.json` has 51 entries and 51 unique names;
   `invalid_missing_tags_input` and `invalid_remote_tags_with_missing_ps_input` each
   occur exactly once; zero names differ from their stripped form (checked with `jq`;
   `strip()` is identity here). Hence `len(declared) == unique == 51`, so neither the
   duplicate problem nor the `< 16` problem is appended.
2. **Guard input domain:** `corpus_problems` reads only `case["name"]`. It never reads
   `tags`, `ps`, `expect`, `expected_exit`, or `expected_finding`, and never rewrites the
   case list. A clean corpus therefore proceeds through `measure_case` with the same
   argv, the same null→absent staging, and the same exit/ID comparison as before the
   repair.
3. **No expectation rewriting:** the pass rule at 299-325 compares the child exit and
   `finding_id` to the fixture literals; the guard cannot substitute or normalize them.
   Cases 30/31 keep `2` / `invalid_input`.

Net: the repair adds an admission predicate over stripped case names. Cases 30 and 31
are admitted as before, spawn the same child invocations, and pass on the same
`*_input_unavailable` → `invalid_input` → exit 2 path.

## Contrary evidence / hazards

- **No contrary evidence observed.** The original corpus contains zero duplicate names
  and zero payload-duplicate groups (grouping all 51 cases by `del(.name)` yields no
  group larger than one), so neither the landed name-keyed guard nor even a
  content-keyed guard would change cases 30/31. The landed guard is strictly the
  name-keyed minimal form the round-15 spec asked for.
- **Do not key the guard on case content or on `case_name()` display fallbacks.** The
  corpus-guard fixtures clone one original case and replace only `name`; every valid
  control therefore has identical payloads under distinct names. Content-keyed dedup
  would falsely reject the valid controls and destroy "retain valid unique corpus
  measurement." The landed code avoids this by hashing nothing but stripped names.
- **Whitespace/Unicode scope of the guard:** `strip()` gives the whitespace-collision and
  tab-collision fixtures their red path; Unicode duplicates are caught by exact string
  equality after strip (no casefolding). That is a name-identity policy, not a claim
  about classifier content. Cases 30/31 contain no such characters, so no interaction.
- **`corpus_problems` only counts named dict cases.** An unnamed or empty-stripped case
  is excluded from `declared`, so it cannot create a duplicate problem. `cases.json`
  has no such entries; this is a limitation of the guard, not a defect for these two
  cases.

## Limitations

- Static reading only: no `measure.py`, classifier, selftest, or fixture command was run;
  claims about exits follow the literal code paths cited, not observed process results.
- The classifier file is byte-identical to the round-14 reported hash; `measure.py` is
  the round-15 landed state (mtime 2026-10-20 05:09:13 -0300). Any later edit by its owner
  would require re-pinning lines 350-364 / 374-385.
- Only indexes 30 and 31 were audited; the other 49 cases are out of this seat's scope.
