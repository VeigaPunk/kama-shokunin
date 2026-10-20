# CaseAudit07 — cases 14/15 literals vs the repaired corpus duplicate guard

Static, read-only audit. No project code was run: no `measure.py`, no classifier, no
`--selftest`, no guard harness. The only commands were reads: `jq`, `sha256sum`,
`diff`, `git cat-file`. Labels: **[observed]** means a direct file read,
**[receipt]** means a prior recorded run, and **[inference]** means reasoning from
the code path.

## Pinned inputs [observed]

| File | sha256 | Notes |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json` | `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` | 51 entries, all objects; every `name` matches `[a-z0-9_]+` with no other character; 51 raw-unique = 51 strip-unique |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py` | `38d1f5d216181bdb7693582027da83eace707f111f42dd32785d386ffe78fb02` | classifier, 531 lines |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py` | `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257` | runner after the repair, 493 lines; **changed during this audit** |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py` | `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` | runner before the repair; same bytes as my first read of `measure.py` |

`diff frozen/measure-before.py round-14/measure.py` shows exactly one change, inside
`corpus_problems`:

```
357a358,359
>     if len(declared) != unique:
>         problems.append("duplicate case names")
```

All `measure.py` line numbers below are for sha `46c5866d…`. The guard fixtures in
`tests/ollama-corpus-guard/` (12 files) appeared during the audit. None of them
mentions either assigned case name or `cases.json`.

## Assigned fixtures, exact literals [observed: `cases.json` lines 230–259, raw]

**Index 14 — `unknown_no_tags_match_but_ps_match`** (lines 231–244)

```
tags.models = [{"name":"qwen3:4b","model":"qwen3:4b","digest":"sha256:2222…2222"(64 hex)}]
ps.models   = [{"name":"llama3:8b","model":"llama3:8b","digest":"sha256:1111…1111"(64 hex)}]
expect = "llama3:8b"   expected_exit = 2   expected_finding = "unknown"
```

**Index 15 — `unknown_empty_tags_inventory`** (lines 247–259)

```
tags.models = []
ps.models   = [{"name":"llama3:8b","model":"llama3:8b","digest":"sha256:1111…1111"(64 hex)}]
expect = "llama3:8b"   expected_exit = 2   expected_finding = "unknown"
```

In the raw text, neither case has a duplicate JSON key at any level or a
`remote_model`/`remote_host` field. Each name occurs exactly once, at index 14 and
index 15.

## Runner path (`measure.py` @ `46c5866d…`) [observed code]

1. `load_cases` (109–128) reads the array envelope and returns 51 cases.
2. `corpus_problems` (350–364):
   - `declared` holds 51 stripped names (stripping changes nothing), so `unique = 51`.
   - Line 358: `len(declared) != unique` is `51 != 51`, which is **false**.
   - Line 360: `unique < 16` is **false**.
   - It returns `([], 51)`.
3. `run`: the call is at 374. Because `corpus == []`, the `if corpus:` branch at 377 is
   **not taken**. The run follows `elif tool_present:` (381) and calls
   `measure_case(root, 14|15, tool, case)` (384–385).
4. `measure_case` (211–347):
   - `case_problems` (139–150) returns `[]`: `expect` is a str, `expected_exit` is the int 2 (not a bool), `expected_finding` is a str.
   - `case_dir = root / f"{index:02d}"` (220), so the directories are `14` and `15`. They are named by index, not by case name.
   - Both captures are dicts, so `write_capture` (189–196) writes `json.dumps(value, ensure_ascii=False) + "\n"`. Case 15 therefore stages `{"models": []}`.
   - argv (230–235) is `python -I -B <tool> --tags <dir>/tags.json --ps <dir>/ps.json --expect llama3:8b`. **The case name is not passed to the child.**
5. Grading (296–325): the case passes when all of these hold:
   - process exit == 2
   - `finding_id` == `"unknown"`
   - `schema` == `kama-ollama-evidence/v1`
   - `verdict_exit` == process exit
   - `readiness` == `unknown`
   - `scope` == `offline-captures-not-runtime`

## Classifier branch (`tools/kama-ollama-evidence.py` @ `38d1f5d2…`) [observed code]

- **`_run` (483–514):** argparse succeeds; this is not `--selftest`; tags, ps and expect are all non-empty (499).
- **`read_json_file` (137–169):** tags (504) and ps (505) are regular UTF-8 files. `_pairs` (124–130) finds no duplicate key, and there is no NaN or Infinity.
- **`classify` (218):**
  - `validate_capture('tags')` (220, 172–187): object with `models` as a list.
    - Case 14: one object entry with string name, model and digest.
    - Case 15: `[]` is accepted (179 only rejects a non-list), and the entry loop runs zero times.
  - `validate_capture('ps')` (221): one valid object entry.
  - `_matching` (190–192) uses exact `==` on `name` or `model`:
    - Case 14: `qwen3:4b` ≠ `llama3:8b`, so `tags_matches = []`.
    - Case 15: an empty list, so `tags_matches = []`.
    - Both cases: `ps_matches` has length 1.
  - 226: `len(tags_matches) > 1` is false.
  - 228: `len(ps_matches) > 1` is false (the length is 1).
  - **231: `if not tags_matches:` is true.**
  - **232: `return 'unknown', ['no_tags_entry_matches_expected_name']`.**
  - Lines 233–264 are unreachable: ps identity, digest presence, remote markers, the available branch and digest equality are never evaluated.
- **`classify_payload` (267–276)** returns:
  - `finding_id: "unknown"`
  - `verdict_exit: FINDING_EXIT['unknown'] == 2` (line 96)
  - `readiness: "unknown"`
  - `scope: "offline-captures-not-runtime"`
  - `reasons: ["no_tags_entry_matches_expected_name", "capture_timing_unknown_exports_not_asserted_simultaneous", "ps_expiry_not_evaluated"]`
- **Exit:** 514 returns 2; `main` (517–519) and then `sys.exit(main())` (531) give process exit **2**.

The documented precedence in the module docstring (33–35) is: "no tags match (unknown,
even when a ps entry matches or conflicts)". Case 14 pins the "ps entry matches" part of
that rule. Case 15 pins the empty-inventory version of the same branch.

The literal pair is consistent: `FINDING_EXIT['unknown'] == 2`. The classifier
selftest's `_valid_case` (329–344) requires `FINDING_EXIT[expected_finding] == expected_exit`.

The exit code alone does not separate the two outcomes. `invalid_input` also exits 2
(line 97), so a regression could still produce exit 2, for example:
- an unstaged ps file gives `ps_input_unavailable`;
- a duplicate ps selection gives `duplicate_ps_entries_match_expected_name`.

The `finding_id` comparison (`measure.py` 304–307) is the check that tells them apart.

## Why the repaired guard cannot change the 14/15 results [inference from observed code]

1. **Only two lines changed, and only in `corpus_problems`.** `measure_case`, the fork in
   `run`, staging, argv and grading are byte-identical to the pre-repair runner. The
   classifier sha is also unchanged.
2. **The guard is a pure check on names that runs before any child.** It reads
   `case.get("name")` and builds `.strip()` copies in a local list. It never changes
   `cases` and never reads `expect`, `tags`, `ps` or `expected_*`. Its only effect is
   which side of the `if corpus:` fork (377) the run takes.
3. **The new check is false on the committed corpus.** The corpus has 51 declared names,
   all unique. Uniqueness was checked with a strict character-class test, not an
   anchored regex, so an embedded newline could not slip through. Both assigned names
   are unique. The cases that share `expected_finding: "unknown"` are indexes
   `[13,14,15,16,17,18,37,38,39,46]`; the shared finding and the shared `expect` do not
   matter because the guard keys only on names.
4. **Names never reach the child.** argv has only `--tags`/`--ps`/`--expect`, and the temp
   directory is named by index. The name is used only as a record label (`case_name`
   131–136; record field at 328).
5. **When the guard fires, it does not reclassify.** It only fires if a duplicate is
   introduced into `cases.json`. Then 14 and 15 become unmeasured records
   (`observed_exit: null`, `observed_finding: null`, `passed: false`, reason
   `corpus: duplicate case names`) and the run exits 1. This is the intended fail-closed
   behavior; neither case receives a different finding.

## Earlier recorded results [receipt]

Source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/acceptance.json`
(`ok: true`, `measured_commit e545ed99aaa519196a2a7779b0a293b2ce4c765c`,
`recorded_at 2026-10-20T06:38:39.980974+00:00`). At that commit (checked with
`git cat-file`):
- `measure.py` = `fda61e00…`, the pre-repair runner;
- the classifier = `38d1f5d2…`, the current bytes;
- `cases.json` = `4a4de0b8…`, the current bytes.

| Run | Overall | Index 14 | Index 15 |
|---|---|---|---|
| `final_corpus` (default tool) | exit 0, 51/51 passed, unique 51 | exit 2 / `unknown` / verdict 2 / passed | exit 2 / `unknown` / verdict 2 / passed |
| `precedence_red` (`frozen/precedence-before.py`) | exit 1, 49/51 passed | exit 2 / `unknown` / passed | exit 2 / `unknown` / passed |
| `selftest` (classifier `--selftest`) | exit 0, 51/51 passed | exit 2 / `unknown` / passed | exit 2 / `unknown` / passed |
| `capability_absent` (tool `frozen/before/...` absent) | exit 1, 0/51 passed | `unsupported` / exit null | `unsupported` / exit null |

`capability_absent` is a control run with the tool missing. It is not a classification
result.

These literal results were therefore recorded with the exact pre-repair runner bytes and
the current classifier and corpus bytes. That the repaired runner gives the same results
is an inference from the two-line diff. I did not observe a post-repair run.

## Contrary evidence and caveats

- **Nothing contradicts** the 14/15 literals or the branch they take.
- **The sibling report `CaseAudit08.md` (read, not edited) has a factual error.** It says
  round-14 `acceptance.json` shows all 51 cases `unsupported` with `passed 0`. That is
  only the `capability_absent` control record; `final_corpus` recorded 51/51 passed with
  the current classifier sha. Two smaller issues in that report:
  - Its list of `unknown` indexes is wrong. It gives "13/14/15/18/38/39/40/47"; the actual
    list is `[13,14,15,16,17,18,37,38,39,46]`.
  - Its note that "the duplicate rejection was not yet present" is now out of date.
- **The two duplicate checks differ (outside this scope; no risk to 14/15).**
  - The classifier's `--selftest` duplicate check (359–365) compares raw names, and its size check (356) uses `len(document) >= 16`.
  - The runner compares stripped names and counts unique names.
  - Both checks agree on the committed corpus because no name contains whitespace.
- **The guard skips some entries (outside this scope).** Entries that are not dicts, or
  whose name is not a string or is blank, are left out of `declared` (353–355). This
  does not matter for the committed corpus, where all 51 entries are dicts with
  non-blank names.

## Limitations

- This is a static analysis only. The post-repair result is inferred, not observed.
- `measure.py` was edited by someone else while I was auditing; the first read had sha
  `fda61e00…` and a later one had `46c5866d…`. The `46c5866d…` sha held when I
  re-checked it just before writing this report. If more edits land, such as the
  R2 partial-output wording, re-pin and confirm that lines 350–425 and `measure_case`
  still behave the same.
- Only indexes 14 and 15 were read in full. Corpus-wide reads covered names, shape and
  `expected_finding` only.
- No tools were installed or upgraded. Nothing was written except this report.
