# KamaR14.SafetyInputs — untrusted exported-metadata input review (sentinel)

Scope: how `tools/kama-ollama-evidence.py` handles the `--tags`/`--ps` paths and file bodies; no acquisition, network, environment, or endpoint reads; no leakage of secret content. Static, contract-based review. Nothing was executed.

## Status of evidence
- When I reviewed (three `ls` checks, ending around 03:27), `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json` and `.ufo/waves/round-14/measure.py` did **not exist**. Under the contract that means **pending**, not a defect. Every finding below comes from the contract text (`spec.json` "Classifier shared interface") and Python stdlib behaviour, not from the shipped code. L1 should check each one against the landed file.
- Prior art: `tools/kama-probe.sh` acquires data live with `curl` to `127.0.0.1:$port` (lines 285, 317) and reads `$HOME`/`$UFO_SRC` (lines 531–564). The new tool must not reuse or call any of that. It is offline only.
- Boundaries: PROVINCE.md:40 sends credential material to kagi. served-identity-crosswalk.md:73 says "no credentials read".
- Recommendations went to KamaR14.Classifier, KamaR14.Fixtures and KamaR14.Harness by peer message. I edited no files.

## Findings (severity · exploit path · impact · smallest remediation)

1. **HIGH — duplicate JSON keys hide a remote marker.**
   - Exploit: `json.loads` keeps the last value for a repeated key. A selected ps entry such as `{"name":"m","model":"m","digest":"d","remote_host":"h","remote_host":""}` parses with `remote_host == ""`. A remote entry then classifies as `loaded_same_digest`, exit 0.
   - Impact: a false local-loaded finding.
   - Fix: pass an `object_pairs_hook` that rejects duplicate keys, mapping the result to `invalid_input`, exit 2.

2. **HIGH — truthiness or type confusion on remote markers.**
   - Exploit: if the code tests `if entry.get("remote_host"):`, then `false`, `0`, `[]` and `{}` all read as local.
   - Fix: allow only absent, `null` or `str` for `remote_host`/`remote_model`. Any other type is `invalid_input`, exit 2. Note that `bool` is a subclass of `int`, so check with `type(x) is str`.
   - The same rule applies to `name`/`model`/`digest`: they must be non-empty `str`, otherwise exit 2.

3. **MEDIUM — echoing body values leaks secrets.**
   - Exploit: `remote_host` can be a URL with userinfo, e.g. `https://user:TOKEN@host`. Model names and other fields are attacker-controlled.
   - Fix: `reasons` should hold only fixed codes, such as `ps_remote_host_present` or `tags_digest_mismatch`. Never put field values, file excerpts or exception messages that quote input into them. Only `expected_model`, which comes from the caller's argv, is echoed.
   - Do not print input paths either (avoids leaking home-directory layout); use `tags`/`ps` labels.

4. **MEDIUM — non-regular files and unbounded reads.**
   - Exploit: `--ps /dev/stdin`, a FIFO, or `--tags /dev/zero` can hang or exhaust memory, with no timeout.
   - Fix: open with `os.open(path, O_RDONLY|O_NONBLOCK)`, then `fstat` and require `S_ISREG`; otherwise `invalid_input`. Read at most `cap+1` bytes (for example 4 MiB) and treat anything over the cap as `invalid_input`. Decode strict UTF-8.
   - Reject `-`/stdin. Do no `~` expansion and use no default paths.
   - A missing or unreadable file is `invalid_input`, exit 2. A missing ps file must never give `available_not_loaded`.

5. **MEDIUM — no acquisition, network or environment surface.**
   - The tool must not import `urllib`, `http`, `socket` or `ssl`. It must not read `OLLAMA_HOST`, `os.environ`, `~/.ollama` or any endpoint, and must never resolve or dereference `remote_host`.
   - `subprocess` belongs only in `--selftest`, called as `[sys.executable, "-I", __file__, ...]` with `shell=False`. The `-I` flag stops `PYTHONPATH` and user-site injection into the child.

6. **LOW — selftest and harness fixture paths.**
   - Write case bodies under `tempfile.TemporaryDirectory()` with fixed filenames inside an integer-index subdirectory. Never use the case `name` from `cases.json` as a path component, because a name like `../x` would be path traversal.
   - Resolve `cases.json` relative to the script directory, not the cwd.
   - A case meant to test "missing ps" should point at a nonexistent path inside the temp directory, never at a host path.

7. **LOW — JSON edge cases and output crashes.**
   - Use `parse_constant` to reject `NaN`/`Infinity`.
   - Emit output with `json.dumps(..., ensure_ascii=True, allow_nan=False)`. A lone surrogate such as `"\ud800"` is valid input for `json.loads`, but with `ensure_ascii=False` it raises when written to stdout and produces a traceback.
   - `ensure_ascii=True` also escapes ANSI and control bytes, so they cannot inject into a terminal.
   - Wrap top-level errors so that no traceback is printed and the result is exit 2 `invalid_input`.

8. **LOW — no normalization.** Compare name, model and digest as exact `str` values. No `strip`, case-folding, `sha256:` prefix handling or GGUF basename mapping; this matches the contract.

## Suggested fixtures (sent to Fixtures; expected values are my contract reading, owner decides)
- The duplicate-key remote mask → exit 2 `invalid_input`. This needs raw-text bodies; if the harness can only serialize objects, record it as a gap.
- `remote_host: false` on an otherwise matching pair → exit 2, not 0.
- `remote_host: true` → exit 2.
- `" sha256:abc"` vs `"sha256:abc"` → exit 1 `identity_conflict`.
- A userinfo URL in `remote_host` → exit 1 `remote_inventory`, and stdout must not contain the secret token.

## Follow-up: Harness (measure.py landed; checked statically, not run)
- Harness adopted item 6. Confirmed in the code: `measure.py:223` runs the child as `sys.executable, "-I", "-B"`, and `:242` sets `shell=False`. Harness reports that each case's temp directory is named by integer index, with fixed `tags.json`/`ps.json` files; null inputs point at a nonexistent path inside the temp directory.
- Remaining LOW: when a case fails, `:301-303` attaches `stderr_tail`/`stdout_tail`. These can include input text if the classifier echoes it. The inputs are committed, non-secret fixtures, so this is acceptable as long as the tails stay bounded.

## Limits
- I made no execution, test, build or network access, read no secrets, environment or config, and installed or updated no tools.
- Only the harness lines quoted above were checked against code. Items 1–5 (the classifier itself) are still unchecked. L1 should check them when the final gate runs, after `tools/kama-ollama-evidence.py` lands.
