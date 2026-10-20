VERDICT: confirm — the nine-file/72-row matrix set recomputes to `bf9068d8…` and the probe to `36b64978…` at round start `e75cf68`, at current `1c325b2`, and in the worktree; only `check.py`/`fault-controls.py` changed, so no JSON row, probe comment or alias path was repinned.

## Findings

**F1 — Matrix set identity reproduced independently (pass).** Formula taken verbatim from `.ufo/waves/round-16/measure.py:286-290` (SHA-256 over the sorted lines `f"{name} {sha256(bytes)}\n"`). Recomputed from `git show <rev>:tests/probe-verdicts/*.json` at both commits and from worktree bytes:

| revision | files | rows | set SHA-256 |
|---|---|---|---|
| `e75cf680b53484a61709ee1b2787d8dbc6419f74` (round start) | 9 | 72 | `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` |
| `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (current) | 9 | 72 | `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` |
| worktree | 9 | 72 | `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` |

Original pin is `.ufo/waves/round-16/measure.py:281` (`EXPECTED_MATRIX_SHA256`) and `.ufo/waves/round-16/acceptance.json:10` (`matrix_set_sha256`), introduced by commit `726f737` (round-16 falsify repairs) and carried unchanged through `cff9e62`, `54a2926`, `e75cf68`, `1c325b2`. Also independently recorded at `corpus/lessons/round-17-verifier-spotcheck.md:79`.

**F2 — Per-file member hashes (pass).** Nine members identical across start/current/worktree and 1:1 equal to the recorded members in `.ufo/waves/round-18/runs/c2-survivors.json` JSON path `inputs.matrix.members` (9/9):

```
AuthAndDead.json        670d539002ecf00579a1529d3a4b5ed0ab50ea645db853cc69cc8e61cf8e5b6a
EnvelopeShapes.json     c6fe95222039abdb1d21248a9278df9fd20f86a52f19b67973042d2a4e8c814e
ForeignControls.json    d5c94b03f0a35f7787cdd60aa74e2d88c8df342ab0d0b96ff2cdaa946a9a9b61
LoadingEnvelope.json    12bc261c595115446dbf592d1ff479c1351229f504a0016f5ef8c0ab05306f03
LoadingRace.json        5644e10ed47ad8521eeadc3b9137553d5303790447575085580e6570ad95c108
NearMissTriple.json     9b19301159bcadb03098edef2931998593b5c4c2f028f6ce0c0afb832e8b09db
NonLoadingStatuses.json 0136baa119aa1e6e74d1423318ddf9275755de0345210601af5765e84e3d922a
Overbroad503.json       680582e1b6585741cbf20513cc055077812f76e88a20d8e77c8faed9b84744b2
ReadyControls.json      ef572d186e699ccd1a10728b53e13742800963f2f0aedfd02a7f9f80c133f3ba
```

`git ls-tree -r --name-only` at both commits lists exactly these 9 JSON plus `check.py` and `fault-controls.py`; worktree `ls -1 tests/probe-verdicts/*.json | wc -l` → 9. No extra file could silently join `load_matrix`'s `*.json` glob (`tests/probe-verdicts/check.py:157`).

**F3 — Probe identity, including every comment line (pass).** `tools/kama-probe.sh` is `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` in the worktree and at `e75cf68`, `1c325b2`; git blob `ce45ea8e53ee75d558615eeb4327faa2ed286a03` is identical at `726f737`, `cff9e62`, `54a2926`, `e75cf68`, `1c325b2`. Only one copy exists in the tree; `.ufo/waves/round-18/frozen/tools_kama-probe.sh` has the same SHA-256 and `sha256sum -c .ufo/waves/round-18/frozen/SHA256SUMS` verifies all ten entries (`…: OK` each). Original pin `.ufo/waves/round-16/acceptance.json:9`. Byte identity means the probe's comment block (e.g. the MODEL_LOADING contract text at `tools/kama-probe.sh:32-38`) and its `served_ids()`/`classify()` logic are literally unchanged.

**F4 — No tree-level add/delete/rename/mode repin (pass).** `git diff --raw e75cf68 1c325b2 -- tools/kama-probe.sh tests/probe-verdicts/` prints exactly two lines, both `:100755 100755 … M` (`check.py`, `fault-controls.py`) — no add, delete, rename or mode change. `git status --porcelain -- tools tests corpus SCORECARD.md QUALITY.md` is empty (only falsify-wave scratch and raw source tarballs are dirty elsewhere).

**F5 — Row count and breadth intact (pass).** 72 tests, 72 unique names; family counts `AuthAndDead 7, EnvelopeShapes 9, ForeignControls 8, LoadingEnvelope 8, LoadingRace 9, NearMissTriple 8, NonLoadingStatuses 7, Overbroad503 8, ReadyControls 8`; verdict histogram `FOREIGN_SERVICE 37, MODEL_LOADING 17, MODEL_OK 8, UNAUTHORIZED_SERVICE 5, MODEL_MISMATCH 3, DEAD 1, NOT_HTTP 1`. This matches `.ufo/waves/round-16/measure.py:282-283` (`EXPECTED_TESTS = 72`, `EXPECTED_LOADING = 17`) and the round-17 "72/17 breadth" figure.

**F6 — No alias or normalization path added (pass).** `grep -n "alias" tools/kama-probe.sh tests/probe-verdicts/check.py` returns no hit; the two `fault-controls.py:131,136` hits are the preserved row name `LoadingEnvelope.canonical-alias`, which still exists in `LoadingEnvelope.json` (as does `AuthAndDead.closed-port-connection-refused`, used at `.ufo/waves/round-18/c2/survivors.py:58`). Grading remains exact equality, not alias-tolerant:
- `check.py:493-495` `record["verdict"] == expected["verdict"]`, `record["reason"] == expected["reason"]`, `record["probe_exit"] == expected["exit"]`
- `check.py:498` drift re-derivation; `check.py:490` exact served-model equality; `check.py:392` `method == "GET"` on `/v1/models`; `check.py:415` grades `rows[0]`.

`git diff -U0 e75cf68 1c325b2 -- tests/probe-verdicts/check.py | grep '^@@'` confines changes to imports, `bind_closed_port` port note, `run_probe` timeout/PID-group handling, JSON decoder exception widening (`json.JSONDecodeError` → `(ValueError, RecursionError)` at `probe_output_row`), a `grade(..., timeout=)` parameter, and new selftests. Constants `DEFAULT_PROBE`, `SCHEMA = "kama-probe-verdicts/v1"`, `PROBE_TIMEOUT = 30`, `HANDLER_TIMEOUT = 10`, `EXPECTED_KEYS`, `VALID_EXITS = (0, 2)` are identical at both revisions.

**F7 — Official artifacts agree with the recomputation (pass).**
- `.ufo/waves/round-18/runs/probe-matrix-identity.json`: 10/10 entries `same: true`, `before_sha256 == after_sha256` equal to the values recomputed here. `.ufo/waves/round-18/runs/run.py:64-66` builds `before` from `git show e75cf68:<rel>` and `after` from worktree bytes — a genuine start-vs-current comparison, not a self-comparison.
- `.ufo/waves/round-18/runs/c2-survivors.json` JSON path `inputs.matrix`: `files 9`, `set_sha256 p(bf9068d8…)`, `pinned_set_sha256 bf9068d8…`, `pinned_ok true`; `.ufo/waves/round-18/c2/survivors.py:762-769` raises `OwnFault` on any mismatch or file-count drift.
- fault-controls selftest stdout tails in `c2-survivors.json` contain exactly one distinct `matrix_sha256` (`bf9068d8…`) with `matrix_files 9` and `matrix_tests 72`.
- `runs/c1-measure.json:478` records probe sha `36b64978…`; 12 fields across the 32 `runs/commands.json` records carry the same probe sha; `commands.json` `measured_commit = c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (ancestor of `1c325b2`; both endpoints are byte-identical so every intermediate commit is covered).

## Residual limits (none change the verdict)

1. **`probe-matrix-identity.json` alone is deletion-blind.** `run.py:64` iterates the *current* glob, so a removed JSON would leave no "before" comparison. In the same official run a deletion still fails twice: `c2/survivors.py:762-769` (pinned `files == 9` and set digest) and the `r16-measure-clone` command, where `.ufo/waves/round-16/measure.py:305-309` returns `EXIT_FAIL` on digest mismatch. No file is missing here.
2. **The identity record reads worktree bytes, not HEAD blobs.** Closed separately: worktree == HEAD for all ten paths at `1c325b2`, and the tracked worktree is clean for `tools`/`tests`.
3. **Static only.** This item named no runtime experiment beyond recomputation, so I executed no harness/probe run. Probe-behavior constancy is established by byte identity plus the unchanged blob since `726f737`; alias *behavior* therefore had no editable surface, and the only changed grading surface (`check.py`) was audited line-by-line above.
4. **Context, not a defect:** `b8e485c` (round-16 feature commit) had an earlier matrix state (digest `ad8f44d3…`, probe `6edd3c4c…`). The "original" for this chain is the post-falsify round-16 pin from `726f737`, which is what rounds 17 and 18 carry. No repin happened inside round 18.

## Commands executed (clone `/tmp/kama-r18-falsify-MatrixProbeBytes` @ `1c325b2`, all exit 0)

- `git clone -q … /tmp/kama-r18-falsify-MatrixProbeBytes && git … switch -q -c seat/MatrixProbeBytes 1c325b2…` → HEAD `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
- `for p in <9 json> tools/kama-probe.sh; do git show e75cf68:$p | sha256sum; git show 1c325b2:$p | sha256sum; sha256sum $p; done` → start=cur=work for all ten
- `python3` recomputation of `matrix_set_digest` from git blobs at `e75cf68`, `1c325b2`, `b8e485c`, worktree → `9 files / 72 rows / bf9068d8…` at the first two and worktree; `ad8f44d3…` at pre-falsify `b8e485c`
- `git diff --raw e75cf68 1c325b2 -- tools/kama-probe.sh tests/probe-verdicts/` → two `:100755 100755 … M` lines only
- `git ls-tree -r --name-only {e75cf68,1c325b2} tests/probe-verdicts/ tools/kama-probe.sh` → identical 12-path inventory
- `git rev-parse {726f737,cff9e62,54a2926,e75cf68,1c325b2}:tools/kama-probe.sh` → `ce45ea8e…` at all five
- `sha256sum -c .ufo/waves/round-18/frozen/SHA256SUMS` → all 10 `OK`
- `git log --oneline -S bf9068d8… -- .ufo/waves/round-16/measure.py` → sole commit `726f737`
- `grep -n "alias"` / constants / `git diff -U0 … check.py | grep '^@@'` as described in F6
- `ss -ltnp | grep -c kama-r18-falsify-MatrixProbeBytes` → `0`; `pgrep -af kama-r18-falsify-MatrixProbeBytes` → none; clone removed with `rm -rf`

No tools installed or upgraded. No listener was opened (only `bind_closed_port`-style code was read, never run); no process of this seat remains.
