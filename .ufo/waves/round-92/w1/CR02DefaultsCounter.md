# CR02DefaultsCounter — attack on frozen C1 counter (round 92 w1)

## Scope
- Object: `tools/round92-server-defaults.py` blob at F/M1/tip `a49e8984bb1e90274b7ee123e027ff2f8a858e26d3c7e3e5a414c8f5f02101f6`
  (identical at F, M1 and tip: `counter-freeze.out`), the 15 rows R01–R15 of `SKILL.md`
  `## Serving defaults (round 92 revision)` at M1 (`18153ebb…`), and the pinned binary
  `/home/vgpnk/.local/opt/llama-b12177/llama-server` sha256 `ba272ee3…`.
- Population/axes: C1 depth (KQ146 / B1–B7 / H1–H3). No lane file touched; counter never modified.
- 18 fixture repos under my own scratch, each `git init` + `rev-parse --show-toplevel` asserted, lane
  `SKILL.md`+`corpus/SOURCES.md` at M1 with the stated mutation(s) only; counter run unmodified.
- Sources for the K2 row read: the five S593–S597 URLs fetched live once
  (`sha256` equal to the SOURCES anchors for all five), plus `llama-server --help` (753 lines).

## Commands and outputs
1. `python3 tools/round92-server-defaults.py --repo . --rev 18153ebb… --binary …/llama-server` in the lane
   → `SERVER_DEFAULTS rows=15 bound=15 unbound=0 duplicates=0 engines=3 fetch_failures=0 help_checked=7
   help_disagree=0 supersedes=14 … rev=18153ebb…`, exit 0 (`c1-repro.out`). Measured predicate reproduces.
2. `python3 out/CR02DefaultsCounter/c1-attack.py --lane <lane> --work <scratch>/fx --binary <bin> --rev 18153ebb…`
   → 13/13 cases as expected, exit 0 (`c1-attack.out`).
3. `… c1-attack2.py …` → F12, F13 as expected, exit 0 (`c1-attack2.out`).
4. `… c1-attack3.py …` → F14 as expected, exit 0 (`c1-attack3.out`).
5. `… c1-attack4.py …` → F16, F17 as expected, exit 0 (`c1-attack4.out`).
6. `npx --yes markdown-it 15.0.3` on the M1 section + one indented forged row → the row renders as
   `<td>9999</td>` (`render-f6.out`). Tooling note: npx-only, nothing installed persistently.
7. Help-matcher probe over the real `--help` (`help-matcher-probe.out`): `help_default('-c')='0'`,
   `-cb=None`, `-cram='8192'`, `-n='-1'`, `-np='-1'`, `-to='3600'`, `--timeout='3600'`; 0 blocks with two
   distinct numeric defaults; no flag matched by an earlier block's first line except the `-----` separators.
8. Lane load during runs: `up 4 days, load average: 33–41` (no timing cell; nothing time-sensitive here).

## Findings

**1. DEFECT (largest): the value cell is not verified — only its first number token as a substring of the
cited line. 14 forged tables exit 0.**
`grade()` B2 is `nums[0] in lit` (`round92-server-defaults.py:170`), and H1 compares only that number
(`:200`). The unit/free text after the number is never compared to anything.
- F16 — R02 (a *help-checked* row) value `3600 h` for a 3600-**second** default → `bound=1
  help_checked=1 help_disagree=0`, exit 0 (`c1-attack4.out`). Same class: R10 `5 s` for 5 **minutes**
  (F1), R15 `5 min` for a 5-second keep-alive.
- Digit substrings pass too: R09 `11434`→`1`, R13 `512`→`12` (F2), R14 `600`→`6` (F2b), exit 0 each.
  Six of the eight non-help rows admit a wrong number; all 15 rows admit a wrong unit.
- Consequence: `bound=15 help_disagree=0` means "the first digit string occurs on the cited line", not
  "the default is stated". This is *not* the disclosed V7 limit (which is only about which vLLM line is
  read).

**2. DEFECT: H1 is selected by the engine cell's first word, so `llama b12177` skips H1–H3 entirely.**
`if eng == "llama.cpp"` (`:192`), with `eng = words[0].lower()` (`:188`) and B4 only requiring that word as
a URL substring. F8: R04 engine cell `llama b12177`, value `8` (for 8192), plus one added help-checked row
to keep `help_checked=7` → `rows=16 bound=16 engines=4 help_checked=7 help_disagree=0`, exit 0. The same
dodge is how `engines` is inflated: "llama" and "llama.cpp" count as two engines (`:268`).

**3. DEFECT: H1 checks only the first backticked option of the flag cell, and any option with a colliding
default passes.** `opts[0]` (`:193`, `:199`), `help_default` returns the first block whose *first line* matches
(`:141-150`).
- F3: R07 flag `-t` (threads) instead of `--parallel`, value -1 (both print `default: -1`) → exit 0.
- F11: R02 flag cell `` `--timeout` `-t` `` → exit 0; the wrong second alias is never read.
- Defaults that collide in this help: `-1` ×7, `0` ×15, `8192` ×2 (`-cms`, `-cram`), `48` ×4, `1024` ×2.

**4. DEFECT: H2 checks only the URL substring `/tools/server/` (`:195`) plus B6 — never that the value is derived
there.** F7: added row with flag `-`, source S597, line 272 (`ctx_http.get ("/cors-proxy",
ex_wrapper(res_403));`), parameter `` `res_403` ``, value `4` → `rows=16 bound=16`, exit 0 — a fabricated
"derived default" bound to a 403 handler. The only guard is B7 (the parameter's backticked token must
appear on that line), which is self-consistent, not true.

**5. DEFECT: line semantics are substring-only, so a log/format string binds as the derivation.**
F4: R08 moved from `server.cpp:129` (`params.n_parallel = 4;`) to `:127`, the `SRV_TRC("%s", "n_parallel
is set to auto, using n_parallel = 4 and kv_unified = true\n")` format string, literal shortened to the
quoted fragment → exit 0. Same mechanism would bind any comment that repeats the parameter name.

**6. DEFECT: `duplicates=0` can be false — the (S,line) pair is compared as text.** `pair =
(cells[5], cells[6])` (`:254-261`), then `int(line)` (`:210`). F5: added R16 = R01 at line `0632` (same
line 632) → `rows=16 bound=16 duplicates=0`, exit 0, although the docstring says "a repeated (S<nnn>,
line) pair … is counted in duplicates". (`c1-attack.out`)

**7. DEFECT: `supersedes=14` does not enforce "replaced row for row".** `sup` is a set gathered from any
bound row's cell 8 (`:269`). F12: R15 deleted and `T14` appended to R01's supersedes cell →
`rows=14 bound=14 … supersedes=14`, exit 0 (`c1-attack2.out`); i.e. T14's row can be absent while the
counter reports the round-91 table fully superseded. Decision text is correctly **not** read (F14: `T14`
in R01's decision cell → `supersedes=13`, exit 1, `c1-attack3.out`).

**8. NOTE: a rendered row that is indented 1–3 spaces is invisible to the population.** `ROW_RE` anchors
`^\|` (`:62`); the docstring itself says "a row is a line starting in column 0", but the claim says
"rendered rows". F6: ` | R16 | … | 9999 | …` added to the section → `rows=15`, exit 0, while a GFM
renderer puts it in a `<td>` (`render-f6.out`). Rows in comments/fences are likewise dropped silently
(correct per docstring, but nothing reports that a row-looking line was skipped).

**9. NOTE (false red): non-numeric defaults cannot be declared at all.** B2 requires a digit token, so a
correct row about `--reuse-port` (`false`; help `default: disabled`) is rejected: F10 → `rows=16 bound=15
… why=value-not-in-literal`, exit 1 (`c1-attack.out`). Same for help blocks with non-numeric defaults
(`-cb` `enabled`, `-fa` `'auto'`, `-tb` `same as --threads` — `help-matcher-probe.out`). KQ146 coverage is
silently numeric-only.

**10. NOTE: the disclosed V7 limit understates its reach by one row.** vLLM declares
`VLLM_HTTP_TIMEOUT_KEEP_ALIVE: int = 5  # seconds` at `envs.py:111` inside `if TYPE_CHECKING:` (line 14),
exactly like `VLLM_ENGINE_READY_TIMEOUT_S` at `:26`. F17: R15 bound to line 111 → exit 0
(`c1-attack4.out`). The claims file names only envs.py:26/812; the limit applies to R14 **and** R15.

**11. NOTE: row read (K2) — all 15 rows are exact; one pointer is coarser than its own convention.**
`rows-verified.md` gives each row's verbatim source line, help default and context: R01–R07 and R14/R15
match both source and binary; R08's `params.n_parallel = 4;` is the assignment inside the non-router
branch (server.cpp:116/129), and R07's cited shared default really is `common.h:464` (`= 1`). The single
imprecision: R11's decision says "(doc comment line 146; zero or negative = forever)" while
`Zero or Negative values are treated as infinite` is config.go:**147** (146 is the block's first line;
R10 cites its range 126-128 explicitly). Parameter, value and data line (150) are exact, so I do not
treat it as K2-fatal; smallest safe correction if L1 wants strictness: `line 146` → `lines 146-148`.

**12. NOTE (holds): matcher behaved correctly on the three named panic cases** — `-c` vs `-cb`/`-cram` are
distinct blocks, `-to` and `--timeout` both resolve to 3600, no option's first line is matched by a later
flag, no block carries two distinct numeric defaults, and the block scan (`:143-144`) reads only an option's first line, so description text cannot inject a `default:` (`help-matcher-probe.out`).

**Counter freeze/drift:** blob is byte-identical at F, M1 and tip; `SKILL.md` section digest and
`corpus/SOURCES.md` digest are equal at M1 and tip (`counter-freeze.out`) — no K1/K3 drift, and the
measured 15/15 is still valid at the tip.

## Deliverables (all under `.ufo/waves/round-92/w1/out/CR02DefaultsCounter/`)
- `c1-attack.py` / `c1-attack2.py` / `c1-attack3.py` / `c1-attack4.py` and their `.out` (18 cases).
- `c1-repro.out` (M1 replay, exit 0), `counter-freeze.out`, `help-matcher-probe.out`, `render-f6.out`,
  `rows-verified.md` (per-row source/binary read with the exact comment lines).

VERDICT: holds — C1's frozen predicate reproduces at M1 and all 15 rows are exact against the byte-identical pinned sources and the pinned binary; the frozen counter is nevertheless not a KQ146 discriminator (14 forged tables exit 0: unverified units/values, engine-name and H1/H2 bypasses, line-substring semantics, `duplicates`/`supersedes` text defects), which is a round-93 counter-depth finding, not a row defect.
