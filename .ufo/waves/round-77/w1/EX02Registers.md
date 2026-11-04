# EX02Registers — C2 implementation

Axes: freshness (complete accounting), calibration (honest evidence), operability (reused audit/parser contracts).

## Changed files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-append-registers.py`: new counter, verbatim predicate blockquote, path imports of all three inherited modules, actual audit invocation, independent topological introduction histories, previous-extant-version row-set rotation comparison, line-bound accepted grading, exempt class/count/parent-section grading, permitted/out-of-region/restored/disclosed buckets, exactly-once accounting, JSON output, finding diagnostics, CLI error map, and seven selftest arms.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/append-only-exempt.tsv`: nine appended rows; header and existing rows unchanged.
- This exclusive report.

## Retained evidence

Read the entire frozen plan before implementation. Read-only command `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` exited 0 and printed `7d60e2ab58866a0366937d61c9712483be57b36e`.

Computed all nine section lists with the imported audit's `sections`, `split_lines`, and `deleted_lines` functions against each event's first-parent blob. Eval completed successfully; this was data derivation, not a counter verification. Derived rows, in assigned order:

| Event prefix | Count | Parent sections |
| --- | --- | --- |
| 900e31b762d5 | 1 | `## Axes` |
| 11c08bdc0064 | 1 | `## Axes` |
| b919f0cb35f4 | 3 | `## Axes` / `## Planned` |
| ac1c8538e391 | 2 | `## Axes` |
| ba9f724800b7 | 2 | `## Axes` / `## Capabilities` |
| 461d2adbf2b3 | 1 | `## Axes` |
| 661622b50b6b | 1 | `## Axes` |
| 417bbf811f29 | 1 | `## Saturation` |
| c1ae92d56f61 | 2 | `## Axes` |

No tools installed or upgraded. No lane git mutations, fixture runs, scratch trees, background jobs, or dispatches. No LSP tool is mounted in this seat; symbol resolution used the actual Python source, not an empty LSP response.

## Verification ownership and missing receipts

Developer fleet instructions prohibit running builds/lint/tests/formatters during the editing wave and reserve verification to the parent. Consequently the requested counter executions and selftest were **not run**; no exit code or passing output is claimed, and the following receipt files were not fabricated:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/measured/after/c2-registers.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/measured/after/c2-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/measured/after/c2-registers.json`

Parent commands, from `/home/vgpnk/Projects/shokunin/kama-shokunin`:

1. `python3 tools/round77-append-registers.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7` — exit unobserved.
2. `TMPDIR=/fast/scratch/hyaku/kama-r77/EX02Registers python3 tools/round77-append-registers.py --repo . --selftest` — exit unobserved; create that scratch directory before invoking and remove it afterward. Each fixture is removed in `finally`.
3. `python3 tools/round77-append-registers.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 --json` — exit unobserved.

## Risks and frozen wording

- Predicate lines 101–103 say rows operate under their own introduction cutoff; scope ruling (a), lines 113–116, explicitly admits a row when its event is an ancestor of the audit revision and permits append growth. The implementation follows that explicit admissibility sentence: independent earliest introduction hashes are provenance/rotation boundaries; row ancestry is checked against `--to`. This interpretation is stated in the module docstring and communicated to SC02Lesson. It does not silently impose the older counter's strict pre-introduction rejection rule.
- Register contents deliberately come from the current working tree while audit/contract/history are pinned to `--to`: otherwise the nine newly appended rows could never cover the requested frozen pre-edit audit. CRLF is preserved for grading rather than normalized by text I/O.
- The permitted-overclaim selftest mutates an actual fixture audit event to assert both `permitted == deleted` and `graded == 1`, then requires an unaccounted finding. This is a counter-grade mutation arm, not a claim that the frozen audit emits inconsistent counts.
- No measured green claim is made until the parent runs the commands above.

## Self-evaluation

Accuracy 3/5: parser-derived section evidence exists, but runtime counter behavior is unobserved. Completeness 3/5: implementation and seven arms supplied; three requested receipts intentionally absent under verification ownership. Clarity 4/5: cutoff ambiguity is explicit, but the frozen wording remains conflicting. Actionability 4/5: exact pending commands and receipt paths listed; parent still must execute them. Conciseness 4/5: report retains only scope, evidence, commands, and material caveats. Overall 3.6/5. Highest-impact next action is the parent's integration gate and receipt capture; the user should agree that unexecuted checks cannot be represented as green evidence.
