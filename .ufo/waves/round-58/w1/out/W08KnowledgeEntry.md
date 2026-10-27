# W08KnowledgeEntry — report

Axis: operability + calibration. Deliverable: draft of `corpus/knowledge/battery-execution-evidence.md`
(59 lines, output-file only, no production file touched).

## Commands and outcomes (all run, none inferred)

1. `git -C <lane> show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:tools/round58-battery-exec-check.py` — read whole checker; exit 0.
   `--counter` test is line 131: `sum(1 for s in f["sub"] if "--counter" in s)` over an argv *list* → exact element membership.
2. `git -C <lane> show <tip>:.ufo/waves/round-56/preregistration.json` — roster = 3 legs (control, positive-control, kill); exit 0.
   Matches `kills == 1 and controls == 2` and `legs=3/3` below.
3. `read https://docs.python.org/3/library/sys.html` + urllib fetch — S517 section extracted verbatim; exit 0.
   Quoted spans: "only on call and return", "The function is thread-specific ...", "'c_call' A C function is about to be called".
4. `S=/fast/scratch/hyaku/kama-r58/W08KnowledgeEntry python3 exp.py` (receipt:
   `w1/out/W08KnowledgeEntry/probe.receipt.txt`) — exit 0, three throwaway fixture repos, each `git init -q` with
   `rev-parse --show-toplevel` asserted equal to the fixture before commit.
   - genuine battery → `roster_match=1 kills=1 controls=2 executed=1 legs=3/3 met=True`, checker exit 0.
   - battery + `os.posix_spawn("/usr/bin/touch", ...)` inside a watched `run` frame → `met=True`, exit 0, and the
     marker file **exists** afterwards: the harness runs an unwrapped path and does not notice.
   - battery with `raise SystemError(...)` after `main()` → `met=True`, exit 0: `result.json["error"]` is written but
     never read by the parent (`frames = json.load(open(res))["frames"]`).

## What the entry states

Establishes: `run`/`assert_mutant_breaks_detection` frames whose `co_filename` is the battery, first parameter bound
to the roster label, and a `--counter` argv element issued under that frame; plus loading under `__name__ ==
"__main__"`. Roster equality is separate *static* AST literal comparison.
Does not establish: that a leg ran (canned `CompletedProcess(argv, 0, "ld_audit=detected\n", "")`); any leg result
semantics (mutant kill, assertion content, which counter `--counter` names); that nothing ran or wrote
(`os.posix_spawn`/`spawn*`/`exec*`/`ctypes` unwrapped, `open()` writes unswallowed); that the battery was exception-free;
multi-thread coverage.

## Findings — what each attacks

F1 (attacks C1's wording, not its score): "hermetic harness" is true only for the four patched entry points plus
`Popen`/`os.system`. A real process launch survives and is invisible, so the claim proves call shape, not isolation.
F2 (attacks C1's "0 evaluation errors"): that counter counts checker exit codes, not battery exceptions; a battery
that crashes after `main()` is `met=True`. C1 remains met as frozen — the freeze defines error = non-0/1 exit.
F3 (attacks the variant set as a limit): the 11 no-ops are all call-graph hollowness. A hollow-substance leg that still
passes a counter argv (wrong repo, wrong counter name, duplicate label) survives; reported as LIMIT per the kill rule,
no predicate change proposed.

## Bounds honoured

No git/jj mutation in the lane; fixture-only commits under `$S`, each with the toplevel assert. No `pacman`, no
installs (none needed). Scratch root removed after copying the receipt. No `corpus/` or tracked file written.

## Unrun

The frozen counter (`tools/round58-c1-counter.py`) was not executed by this seat — C1's measured numbers are the
executor seats' receipts, not mine. `tests/round58-battery-variants/` was not enumerated.

## Artifacts

- `.ufo/waves/round-58/w1/out/W08KnowledgeEntry.md` (this report)
- `.ufo/waves/round-58/w1/out/W08KnowledgeEntry/battery-execution-evidence.md` (entry draft, 59 lines)
- `.ufo/waves/round-58/w1/out/W08KnowledgeEntry/probe.receipt.txt` (three probe runs, verbatim)
