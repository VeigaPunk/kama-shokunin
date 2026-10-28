# A07C2Template — C2 run-template binding attack

**Axis:** calibration. **Result:** a registry row may bind the exact frozen manifest template yet receive a passing execution verdict without running the target check.

## Counterexample

`score()` enforces exact template identity: `round62-c2-counter.py:222-226` compares `row['run']` to `tpl['run']`, and `run_bound()` does not execute the row’s run text; it executes `placeholders(tpl['run'], ...)` (`:249-260`). This blocks registry-field command substitution, but leaves the interpolated paths unquoted in a `bash -c` command.

The strongest concrete injection is through `--work`, because `tip_tree` is `<work>/tip` (`:374-383`, `checkout_tip()` at `:351-363`) and `%T` is inserted verbatim (`:184-186`). `run_bound()` then executes the resulting string with Bash (`:259-260`). A crafted work path can terminate the intended Python command and print the manifest’s expected pattern, with a final successful status; the counter only checks that pattern in combined stdout/stderr and `rc == 0` (`:265-271`). Its sensitivity check merely removes that text from the captured output; it does not establish that the intended check produced it.

## Exact local reproduction

Using the frozen source copied from `git show master:tools/round62-c2-counter.py` at tip `65d7cad0fce90e34de37527cde22e97b63b118bf`, I imported the copied module and called `run_bound()` for the manifest’s `sources-registry` / `census` template with:

- `tip_tree = /fast/scratch/hyaku/kama-r62/w/A07C2Template/tip; echo '45/45 selftest cases passed'; true #`
- a dummy file at `<tip_tree>/tools/sources-append-only.py` (so the lexical target-liveness check passes)
- the unchanged manifest template `python3 %T/tools/sources-append-only.py --selftest`

Observed exact return tuple:

```text
(True, '45/45 selftest cases passed', True, False)
```

The command produced the required pattern and status zero from the injected `echo`/`true`; the intended selftest did not run. The tuple means `verdict=True`, decisive pattern recorded as observed, `sensitive=True`, and `dead=False`. This is a direct semantic bypass of the claim that a bound row’s own check was executed live. It is not a registry-row mismatch: the template remains exact.

## Smallest safe correction

Do not interpolate these path placeholders into shell source. Execute an argv vector (e.g. parse frozen templates into fixed argv elements and substitute `%T`, `%S`, `%R`, `TIPREV` within individual elements) with `subprocess.run(argv, shell=False, ...)`; or, at minimum, shell-quote every substituted value with `shlex.quote` before `bash -c`. The argv approach also prevents paths containing spaces from changing argument boundaries. Add a regression control that supplies a work path containing `; echo '<frozen pattern>'; true #` and requires the genuine tool’s output/behavior, not injected output, to determine the verdict.

No tools were installed or updated.
