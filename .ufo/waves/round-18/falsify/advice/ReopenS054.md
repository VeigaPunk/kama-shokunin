VERDICT: partial — the digest, the quoted warning and the `--host` clear reproduce byte-exactly, but the delivered S054 derivation generalizes last-wins beyond the opened bytes and drops the `--api-key` append and `--spec-type` no-warning caveats that the opening report had disclosed.

Seat: KamaR18.ReopenS054 (scout, read-only). Lane master
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Round-18 lesson, SCORECARD
§Round 18, KQ23/KQ24 and `runs/` read first. No production, fleet, frozen
evidence or old-lesson edits; no jj/git writes; no installs; no listeners
started. All reads absolute.

Axes: calibration (source-row statement vs opened bytes) moves down;
operability (exact-argv gate) does not move — the gate never relies on
server-side duplicate handling (see "Impact").

## Confirmed

### 1. Exact source digest and pin identity — CONFIRMED

- Retained bytes: `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources/llama-arg.cpp`
  → `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`,
  224650 bytes, 4833 lines (`wc -l`).
- Same bytes at lane master:
  `git cat-file blob 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/sources/llama-arg.cpp | sha256sum`
  → same digest, exit 0. Working-tree file is clean (`git status --porcelain` empty for it).
- Independent re-fetch of the cited URL:
  `curl -sSL --max-time 60 -o /tmp/kama-r18-falsify-ReopenS054/arg.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp`
  → exit 0, 224650 bytes, `sha256sum` = same `bf4c58…822d`.
- Pin ↔ release mapping: `git ls-remote --tags https://github.com/ggml-org/llama.cpp b11755`
  → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755`, exit 0.
  So "llama.cpp command-line parser @ 704366d76 (release b11755)" holds.
- Minor provenance note (not a defect): `sources/pins.json` has no
  `llama_arg` record (its `sources`/`documents` keys are only the nine
  SourcePins web documents); the arg.cpp provenance is the committed blob
  plus the S054 row digest, and it re-fetches identically.
- The S054 digest cell matches the committed `corpus/SOURCES.md` blob at
  lane master (`git show 1c325b2e…:corpus/SOURCES.md | sha256sum` =
  `8b2907bd2667c49df199f546a494e4f985d14bc7e12527bf721ef4cc1a79cdb1`,
  identical to the working-tree file; the row contains the digest twice,
  at `corpus/SOURCES.md:66` and the search-scope line).

### 2. Repeated-flag warning and unknown-flag throw — CONFIRMED (with an undisclosed exemption)

`nl -ba .ufo/waves/round-18/sources/llama-arg.cpp | sed -n '829,837p'`:

```
829  if (arg_to_options.find(arg) == arg_to_options.end()) {
830      throw std::invalid_argument(string_format("error: invalid argument: %s", arg.c_str()));
831  }
832  if (!seen_args.insert(arg).second) {
833      const bool skip = (arg == "--spec-type");
834
835      if (!skip) {
836          LOG_WRN("DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)\n", arg.c_str());
837      }
```

- Unknown token: throw at 830, matching "unknown flag throws at 829-830".
- Quote at 836 is verbatim and 16 words (≤25).
- The same block is duplicated at 1225-1229 in `common_params_to_map` with
  the identical `--spec-type` skip.
- Exemption: repeated `--spec-type` is accepted **without any warning**
  (line 833). The S054 derivation cell's "repeated flag only warns at
  832-837" is therefore false for that flag; the opening report
  `build/advice/ScoutLlamaArgParse.md` F1 had disclosed "`--spec-type` is
  the sole warning exemption", but the S054 row omits it.

### 3. `--host` clear — CONFIRMED

`nl -ba` lines 3334-3349: option `--host` at 3335, handler lambda 3337,
`params.hostnames.clear();` at **3338**, CSV re-push 3339-3344, and an
empty-list throw at 3345-3347. Each occurrence clears the vector, so the
last `--host` occurrence wins for the list — the S054 statement is correct.
The row's cited range "3337-3343" contains the clear (3338) but stops
before the empty-list throw at 3345-3347; a cosmetic range imprecision,
not a falsification.

## Falsified

### 4. "Last value wins" is not scoped to assign-style handlers — FALSIFIED

`corpus/SOURCES.md:66`, S054 derivation cell (verbatim):
"A repeated flag such as a second `--port` or `--host` is accepted with a
warning and the last value wins, so the server cannot be relied on to
reject a smuggled flag; kama therefore re-derives exact launch argv in the
gate (lane policy)."

The predicate is stated of "a repeated flag" generally (the examples
scope by illustration, not by exclusion), and the row's own declared scope
("how llama-server … treats a repeated or unknown command-line flag")
covers flag semantics, so the counterexamples below sit inside that scope:

- `--api-key`, `common/arg.cpp:3533-3541`: the handler loops
  `parse_csv_row(value)` and runs `params.api_keys.push_back(key);`
  (3538). A second `--api-key` **appends**; it does not replace. The
  generic warning at 836 still fires for it, so the warning's
  "only last value will be used" is misleading for this option.
- `--api-key-file`, `common/arg.cpp:3544-3561`: every non-comment line is
  `params.api_keys.push_back(key);` (3554) — repeated occurrences
  accumulate file-sourced keys.
- `--spec-type`, `common/arg.cpp:4315-4324`:
  `params.speculative.types.insert(params.speculative.types.end(), …)`
  (4321) — append, and warning-suppressed at 833/1226.
- `--n-pl`, `common/arg.cpp:3303`: `params.n_pl.insert(params.n_pl.end(), …)`
  — append.
- Pinned consumer confirmation: fresh fetch of
  `tools/server/server-http.cpp` @704366d76 (sha256
  `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`)
  lines 260-285: `auto middleware_validate_api_key = [api_keys = params.api_keys]…`
  and `std::find(api_keys.begin(), api_keys.end(), req_api_key) != api_keys.end()`
  (285). Every appended key authenticates; the last one does not supersede
  earlier ones. `server.cpp:355` likewise guards on `params.api_keys.empty()`,
  not on a single key.

So the accurate statement is: duplicate flags are never rejected; assign-style
handlers (`--port`, `--host`, and other scalar handlers) last-win, while
append-style handlers (`--api-key`, `--api-key-file`, `--spec-type`,
`--n-pl`) accumulate — and `--spec-type` repeats are not even warned.

### 5. The disclosed `--api-key` append caveat is suppressed in delivered text — FALSIFIED (as "not suppressed")

- The opening seat disclosed it: `build/advice/ScoutLlamaArgParse.md` F2
  ("`--api-key` appends, it does not overwrite … push_back … duplicate
  `--api-key` accumulates keys (no last-wins), and env + CLI accumulate
  together. The generic override warning printed for this option is
  therefore misleading") and O3 (both env and CLI keys authenticated in
  one run). F1 also disclosed the `--spec-type` exemption.
- Delivered corpus contains no version of that caveat:
  - `corpus/SOURCES.md:66` — row and derivation as quoted above; no
    `--api-key` append and no `--spec-type` exemption.
  - `corpus/knowledge/llamacpp-loading-lifecycle.md:250` — only
    "S054 shows why server-side duplicate warnings are not rejection."
  - `corpus/lessons/round-18.md:50` — Gate row only "reject; admit S054
    last-wins warning".
  - `grep -rn 'api-key\|api_key\|api_keys' corpus --include='*.md'` returns
    only `llamacpp-loading-lifecycle.md:35` ("A loading server with
    `--api-key` therefore answers 503, not 401"), which is unrelated.
- Result: a reader of the delivered row would believe a second
  `--api-key` is overwritten, exactly the security-relevant case the row
  is used to justify; the row's own examples (`--port`, `--host`) are the
  only flags for which the last-wins predicate holds.

## Impact on the lane claims (bounded)

- C1 exact argv is **not** harmed: the v3 validator compares the whole list,
  `tests/llamacpp-live/check-receipt.py:500-515` builds the exact
  `expected_argv` and rejects `argv != expected_argv`, so duplicate/extra
  flags are refused by lane policy independent of server last-wins or
  append semantics. The forged-receipt controls retain the targeted
  cases: `tests/llamacpp-live/controls.py:701-749` (k20 extra
  `--api-key X` before the fixed tail; k22 duplicate `--host 0.0.0.0`),
  with gate-only forgery grading at `controls.py:1700-1747`; official
  `runs/controls-selftest.stdout` = `selftest: 70 cases, 0 failure(s)`,
  `runs/controls-selftest.exit` = 0.
- The knowledge-doc use of S054 ("warnings are not rejection") remains true
  and is in fact strengthened by the append/silent-exemption facts.
- What fails is the source row's own derivation and the claim that the
  caveat was retained: the append semantics make duplicate `--api-key`
  *more* dangerous than last-wins, not less, and the row currently records
  the opposite generalization.

## Smallest fixes (advice only; L1 owns admission)

1. `corpus/SOURCES.md:66` derivation: scope last-wins to assign-style
   handlers (`--port`, `--host`) and state the exceptions in the same
   cell: `--api-key`/`--api-key-file` append keys, `--spec-type`/`--n-pl`
   append, and repeated `--spec-type` is warning-exempt (833).
2. Carry the `--api-key` append caveat into
   `corpus/knowledge/llamacpp-loading-lifecycle.md` (and, if the Gate row
   keeps "last-wins warning", qualify it as the warning text, not a
   universal parser behaviour).
3. Optional: cite the `--host` range as 3337-3348 to include the
   empty-list throw at 3345-3347.

## Limits

- Source-level verification only; no llama-server was run (no bounded
  experiment was named for this seat). The append behaviour is established
  from pinned parser and server source plus the opening seat's O3
  observation, not re-observed here.
- Fresh fetch is byte-identical over curl's default TLS validation; no
  independent repository signature was checked for arg.cpp.
- `pins.json` does not contain a llama_arg record; the digest chain is the
  committed blob + row + fresh fetch, all matching.
- No packages installed or updated. Scratch under
  `/tmp/kama-r18-falsify-ReopenS054` (and the one stray
  `/tmp/kama-r18-arg-upstream.cpp`) removed after writing; no listener or
  server process was started by this seat (`pgrep -af
  'kama-r18-falsify-ReopenS054'` empty; no port opened).
