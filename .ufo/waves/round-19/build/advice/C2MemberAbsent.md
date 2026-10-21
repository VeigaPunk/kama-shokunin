VERDICT: confirm - at HEAD `f1790e2` an absent member reports `absent`, is never counted as rejected, and forces exit 1 (exit 2 when the baseline is invalid). The silent default-set drop found at `7229fa9` is fixed at `5b108c1` and still fixed at `f1790e2`; one Low gap remains: the docstring defines exit 1 only as "a mutant survived".

# C2MemberAbsent: absent-member grid check (round 19)

**Question.** Ask `install-tree-grid.py` for a member absent from the receipt tree; confirm the `absent` status and the exit rule.

**Versions verified** (one script, `out/reproduce.sh`, one log per source):

| tag | source | grid sha256 | gate sha256 |
|---|---|---|---|
| A | my copy, 03:20 (HEAD `8bf99ca` + round-19 working tree then) | `467d44d8…` | `afc9e79b…` |
| B | HEAD `7229fa9` | `49a42f81…` | `10912f24…` |
| C | working tree 03:39:10, uncommitted (= my proposed patch, byte-identical) | `e3a48957…` | `10912f24…` |
| D | HEAD `5b108c1` (= working tree 03:40:51) | `2acfec23…` | `10912f24…` |
| F | HEAD `f1790e2` (03:42:45), **current at report time** | `2acfec23…` | `a0dc1d07…` |

The lane changed repeatedly during this run: three commits and four working-tree rewrites. Each snapshot was checked with `cmp` or `git show <rev>:<path> | sha256sum`. Nothing after `f1790e2` is covered. The only lane write is this report, as the trailer requires.

**Receipt and pins.** `.ufo/waves/round-18/live-recovery/receipt-1.json` (sha `89728a02…`; v3; pass; 51-member tree; tree sha `6c216313…`). Pins equal receipt-recorded values and on-disk hashes: server `b6a31a8e…` (installed `llama-server`), probe `36b64978…`, tool `83eac5c0…`, impl `e404b91a…`. Model `270cba1b…` is receipt-recorded only; the model file was not re-hashed.

**Reproduce.** `bash /tmp/kama-r19-C2MemberAbsent/out/reproduce.sh` (A), or `SRC=lane-now|lane-wt|lane-wt3|lane-f1790 bash …/out/reproduce.sh` (B–F). Logs: `out/reproduce*.log`. Hashes: `out/index.sha256`.

## Results (exit per step; `###` labels in the logs)

| step | run | A | B | C | D | F |
|---|---|---|---|---|---|---|
| 00 | gate, real receipt, all pins | 0 | 0 | 0 | 0 | 0 |
| 01 | absent only, tree pin on | 1 | 1 | 1 | 1 | 1 |
| 02 | absent only, pre-pin | 1 | 1 | 1 | 1 | 1 |
| 03 | present `libggml-base` + absent | 1 | 1 | 1 | 1 | 1 |
| 04 | absent only, `--json` | 1 | 1 | 1 | 1 | 1 |
| 05 | two absent | 1 | 1 | 1 | 1 | 1 |
| 06 | zero model pin (baseline INVALID) + absent | 2 | 2 | 2 | 2 | 2 |
| 07 | default members, pin on (control) | 0 | 0 | 0 | 0 | 0 |
| 08 | default members, pre-pin (control) | 1 | 1 | 1 | 1 | 1 |
| 09 | gate, receipt without `libllama.so.0.7.0` | 0 | 0 | 0 | 0 | 0 |
| 10 | default members, that receipt, pin on | **0** | **0** | 1 | 1 | 1 |
| 11 | explicit members, that receipt, pin on | 1 | 1 | 1 | 1 | 1 |
| 12a | gate, receipt without any default | 0 | 0 | 0 | 0 | 0 |
| 12b | default members, that receipt, pin on | **0** | **0** | 1 | 1 | 1 |
| 13 | receipt path does not exist | 1 | 1 | 1 | 2 | 2 |
| 14 | lane `--selftest` | – | 0 | 0 | 0 | 0 |

Bold = silent exit 0 on the default set, before the fix. Under C–F step 06 prints `members=0` with no absent row (invalid-baseline rows are suppressed); exit 2 is unchanged. Step 13 is a traceback with exit 1 in A–C and a clean message with exit 2 in D/F. P-series (proposed patch on B's grid): P1 1, P2 1, P3 0, P4 1, P5 1 in every source. P0 (diff vs my patch) is 0 only for C, since C is byte-identical to it.

## Absent status: confirmed
`--members libllama-absent-probe.so.0.0.0` (not in `server.install_tree`) yields row `absent`. F L97-99: no gate run for it. The JSON row carries only `member` and `status` (step 04). Output `baseline=VALID members=1 rejected=0/1`, exit 1 (step 01).

## Exit rule: confirmed
F L123-125: baseline not VALID gives 2; otherwise `0 if rejected == len(rows) else 1`. Absent rows count in `len(rows)` but never in `rejected` (F L110), so any absent row forces exit 1 and exit 0 is impossible with one. Step 06 shows exit 2 takes precedence under an invalid baseline.

## Finding 1: silent default-set drop (Medium). Present at B, fixed at C/D/F
B L80: `members = args.members or [m for m in DEFAULT_MEMBERS if m in tree]`. B L81-82: if none are present, `members = sorted(tree)[:3]`. The absent branch (B L92-94) is unreachable for default names.
- Step 10: exit 0, `members=2 rejected=2/2`, no row for `libllama.so.0.7.0`.
- Step 12b: exit 0, `members=3 rejected=3/3` on `LICENSE`, `ggml-rpc-server`, `libggml-cpu-alderlake.so`.
- B's selftest always passes `--members` (B L155), so it never exercised this path.
- The real round-18 tree has all three defaults (step 07), so no recorded result changed.
- Latent risk: the runner's `tree-grid-pin` (run.py L67, source read, not executed) uses default members and passes iff exit 0 (run.py L95, source read). On a tree missing a default, B would pass with reduced coverage. [INFERENCE: how likely such a tree is.]
- Fix, now in HEAD: F L85 `members = args.members or list(DEFAULT_MEMBERS)`, fallback removed. Steps 10 and 12b now exit 1 with `absent` rows (C/D/F). Controls 07/08 and P3/P4 are unchanged.

## Finding 2: exit 1 for absent is not documented (Low)
The docstring (F L17-18) still defines 1 as "a mutant survived". Absent-only (step 01) and a survivor run (step 08) both exit 1; only the status word differs. The lane's selftest (F L186-187) now pins absent → 1, so the behavior is contract-by-test but not by docstring. Suggest documenting absent as "requested, not measured; counts as not rejected". [INFERENCE, untested] Exit 2 for requested-absent would keep 1 = "survived", but would change the selftest and any caller that reads the code.

## New behavior at D/F (informational)
- An invalid baseline now runs no members (F L96), so absent names are not listed in that case. Exit 2 still signals it.
- An unreadable receipt now exits 2 with a message (F L77-80), instead of a traceback with exit 1.

## Gaps and disclosures
- Lane moved during the run: commits `7229fa9` (03:34:47), `5b108c1`, `f1790e2` (03:42:45); working-tree writes at 03:33:02, 03:33:16, 03:39:10, 03:40:51. The gate at `f1790e2` adds seven lines (empty-tree rejection); no step changed.
- `pgrep` matched two `check-receipt.py` processes running from the lane path (PIDs 415891, 416261) that this work did not start. A copy-path check afterwards found none (leftover step, exit 1).
- One read-only `git status --short -- .ufo/waves/round-19/build/advice` ran in the lane. It may refresh the index stat cache; no content changed. Other lane git calls were `log`, `show`, and `rev-parse`.
- Not run: the lane's `run.py` (it writes lane artifacts); model-file hashing.
- Installs or updates: none.
