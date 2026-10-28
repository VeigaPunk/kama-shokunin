# X02Regress1 — C2 sensitivity, planted regressions part 1 (3 rows)

Base tree: freeze commit f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (scratch clone, `git archive` of HEAD; mutant trees = copies of its tools/ tests/ registry/). No lane file edited. No tools installed.

## Deliverables (out dir `.ufo/waves/round-64/b/out/X02Regress1/`)
- `capability-regress-r64.part1.tsv` — cap, tool_path, find, replace; TAB-separated, no header, no tab inside a cell, every find is a single physical line with no leading/trailing whitespace, occurs exactly once in its tool.
- `verify_part1.py` — the driver that produced the table below (usage in its docstring; pass the tip-tree dir, a scratch dir, the r63 registry tsv, the part1 tsv, the repo).
- `verify_run1.txt`, `verify_run2.txt` — two full runs; `diff` shows them identical (no flake).

## Per-row evidence (row run template from registry/capability-claims-r63.tsv, executed on unmutated and mutated copy; %T = copy of tree, %S scratch, %R repo, TIPREV=HEAD)
| cap | find -> replace (one line) | find count | importable | unmutated: exit / pattern / line | mutated: exit / pattern / line |
|---|---|---|---|---|---|
| sources-registry (tools/sources-append-only.py, pattern `45/45 selftest cases passed`) | `if new is None:` -> `if new is None and False:` (drops the removed-row violation in `diff_registries`) | 1 | yes | 0 / present / `45/45 selftest cases passed` | 1 / absent / `43/45 selftest cases passed` |
| ollama-offline-evidence-replay (tools/kama-ollama-evidence.py, pattern `"failed": 0`) | `if tag['digest'] != ps_entry['digest']:` -> `if False and tag['digest'] != ps_entry['digest']:` (drops the tags/ps digest-mismatch check in `classify`) | 1 | yes | 0 / present / `{"schema": "kama-ollama-evidence-selftest/v1", "finding_id": "clean", "verdict_exit": 0, ... "failed": 0 ...}` | 1 / absent / `finding_id": "selftest_failed", "verdict_exit": 1` |
| live-llamacpp-lifecycle (tools/kama-llamacpp-live.py, pattern `"outcome": "pass"`) | `all(value == 'llamacpp' for value in owners)` -> `all(value == 'llama' for value in owners)` (models `owned_by` constant in check `models_owned_by_llamacpp`) | 1 | yes | 0 / present / `"outcome": "pass", failed_checks=[]` | 1 / absent / `outcome=fail failed_checks=['models_owned_by_llamacpp']` (real pinned llama-server was started and torn down by the unmutated tool; the failing check is exactly the edited one) |

"importable" = `py_compile` plus `exec_module` of the mutant's module body succeeded (the `__main__` guard does not run). Each edit changes exactly one line and keeps the line count (driver prints `differing_lines=1 line_count_same=True`). None deletes the pattern string: the pattern is produced by the tool's own run and now genuinely does not appear.

## Candidates tried that did NOT flip (survivors, not used)
- sources-append-only: `if len(cells) != len(header):` -> `< len(header)` (row-width check, 45/45 still passes: selftest has no too-wide row case) — survived exit 0.
- kama-ollama-evidence: `len(records) >= MIN_CASES` -> `>= 0` (case-count floor) — survived exit 0.
These are real selftest gaps in the bound tools (usable as honest "survivor" evidence), not part of the table because they do not satisfy the flip requirement.
Other flipping candidates found (not delivered, spare): sources `if old[c] != new[c]` -> `==` (17/45); `if rid in rows_by_id:` -> `and False` (44/45); ollama `'identity_conflict': 1,` -> `0` and `len(ps_matches) > 1` -> `> 2`; llamacpp `== 501` (metrics) -> `== 200` and `model_sha256_post == model_sha` -> `!=` (all flip outcome to fail, exit 1).

## Rows that cannot be made to fail by a one-line edit
None of the three. (The remaining nine registry rows were outside this assignment.)

## Notes for the C2 counter builder
- The live llamacpp tool reads `registry/endpoint-consumers.tsv` under its own tree: a mutant scratch tree needs `registry/` as well as `tools/`; with only tools/ the run exits 2 `setup-error` (registry-unreadable), which would be a false flip for the wrong reason. My driver copies tools/, tests/, registry/. The ollama selftest needs `tests/ollama-evidence/cases.json` (tree-relative to the tool).
- Copy trees with `symlinks=True`: the `.ufo` tree holds self-referential symlinks (round-36 MutRowPipe) that make a plain `shutil.copytree` of the whole repo recurse; do not copy `.ufo`.
- Mutation exit is 1 for all three (a failed check/violation exit), never 2/setup-error, so the flip is attributable to the edit.

Counter line: part1 flipped=3/3 (sources-registry, ollama-offline-evidence-replay, live-llamacpp-lifecycle), find_once=3/3, identical on 2 runs.
