# X9Census — round-43 closure D3 (every warning class stated) + D4 (tip-side gate selftest receipt)

**Verdict: D3 discharged — `sources-census.sh validate` on the lane is clean of every error class (E01–E12 = 0) with two warning classes live and stated with counts (W04 = 93, W01 = 1) and W02/W03 = 0, exit 0 on both `--root` and `--file` invocations, and one defect: the 222-row registry carries 93 cross-scope duplicate-URL warnings (41.9% of rows), 33 of them for a single file. D4 discharged with a red receipt — `gate-registry-check.py --selftest` prints `GATE_SELFTEST pass=5 fail=1`, exit 1, at both the frozen base `77d1bbf5` and the tip `098df344`, so `SKILL.md:1325`'s documented `GATE_SELFTEST pass=6 fail=0` does NOT match; the failing arm is a non-hermetic lane-tip arm, not a fixture arm.**

Seat X9Census, leaf. Lane tree read-only; nothing edited in place. All artifacts under
`.ufo/waves/round-44/w1/out/X9Census/` (absolute: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Census/`).
Measured tip: lane `master` == `HEAD` == `098df344d977a9047ea346a01a93c307887570b0` (`lane-head.txt`); the assignment's freeze commit is `77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40`.

## 1. Census validate — commands and exit codes

| # | Command | Exit | Receipt |
|---|---|---|---|
| 1 | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | **0** | `census-root-kama.out` (95 lines), `census-root-kama.err` (empty) |
| 2 | `bash scripts/sources-census.sh validate --file /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` | **0** | `census-file-sources.out` (95 lines), `census-file-sources.err` (empty) |
| 3 | same as 1, rerun for determinism (`diff` against receipt 1) | 0 | `census-root-kama.rerun.out` — byte-identical, prints `DETERMINISTIC` |
| 4 | `bash scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` (row population) | **0** | `census-mode-kama.out` |

Invocation 2 differs from 1 only in the first TSV column: `file` where 1 prints the lane id `kama`. Every code, id and message is identical; the diff output is 95 paired lines and no content difference (`diff` transcript in this session, receipts side by side). So the two modes agree on the lane's registry; the lane label is the only divergence.

## 2. Every warning and error class, with counts

`sources-census.sh` defines 12 error classes and 4 warning classes plus the clean-lane line (`scripts/sources-census.sh:24-33`). Counts are lines in `census-root-kama.out` (`classes.tsv` is the machine table; "absent" = the class was not printed at all, i.e. zero occurrences).

| Code | Class (from `sources-census.sh:24-33`) | Count | Present in receipt |
|---|---|---|---|
| E01 | malformed row (NF != 13) | 0 | absent |
| E02 | id not `S[0-9]{3,}` | 0 | absent |
| E03 | duplicate id | 0 | absent |
| E04 | duplicate URL + scope (no `supersedes`) | 0 | absent |
| E05 | kind enum violation | 0 | absent |
| E06 | tier enum violation | 0 | absent |
| E07 | status enum violation | 0 | absent |
| E08 | `opened` not a past/present ISO date | 0 | absent |
| E09 | invalid recheck | 0 | absent |
| E10 | community at tier A | 0 | absent |
| E11 | used-by path missing on disk | 0 | absent |
| E12 | row-shaped source outside `## Registry` | 0 | absent |
| **W01** | tier-C mined with non-`—` used-by | **1** | yes — `S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md` |
| W02 | rejected row, thin `teaches` | 0 | absent |
| W03 | mined row with used-by = `—` | 0 | absent |
| **W04** | same URL across scopes | **93** | yes — 93 lines |
| `ok` | clean-lane line (emitted when no E-class finding) | 1 | yes — `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` |

95 output lines = 93 W04 + 1 W01 + 1 ok. **No error class fires: E01–E12 = 0.** Warnings deliberately do not affect exit status (`sources-census.sh:738-745`: `lane_errors` is set only by a `\tE[0-9]+\t` match, and `[ "$lane_errors" = 1 ] || emit "$lane\tok\t$f"`), which is why exit 0 with 94 warning lines is the documented behaviour and not a swallowed finding.

Population behind those counts (`census-mode-kama.out`, exit 0): `rows 222`, `tier.A 211`, `tier.B 7`, `tier.C 4`, `status.mined 203`, `status.queued 8`, `status.rejected 11`, `FLEET.missing 0`. 222 registry rows in the file are confirmed independently by `grep -c '^| S[0-9]' corpus/SOURCES.md` = 222.

### 2.1 W04 is structural, not random: 93 of 222 rows (41.9%), 29 distinct URLs

W04 flags a row whose normalized URL was already seen under a **different** scope (`sources-census.sh:645-646`), so the count is `Σ(scopes−1)` over multi-scope URLs, not a row tally. Distribution (`census-root-kama.out`, top groups):

| Rows flagged | URL |
|---|---|
| 33 | `github.com/ggml-org/llama.cpp/blob/704366d76…/tools/server/server-schema.cpp` |
| 15 | `…/tools/server/server-context.cpp` |
| 9 | `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…/tools/server/server-common.cpp` |
| 2 each | `server.cpp`, `server-common.cpp`, `server/README.md`, `src/llama-context.cpp`, `common/arg.cpp`, `man7.org/…/ld.so.8.html`, `git-scm.com/docs/git-log`, `git-scm.com/docs/git-cat-file`, `docs.python.org/3.14/library/subprocess.html`, `docs.python.org/3.14/library/os.html` |
| 1 each | 16 further URLs (git, nix, go, tldp, ollama, jj, python) |

The lane re-pins one commit-pinned `llama.cpp` file once per registry row across scopes; `server-schema.cpp` alone accounts for 33 of the 93. This is the corpus's per-row pinning design meeting a cross-scope uniqueness warning — a **warning class stated**, not a data error, and the frozen tool's judgement (exit 0) is correct by its own contract.

W01's single row is `corpus/SOURCES.md:234` (`| S481 | vLLM pull request 58552 … | community | C | …`): tier C + `mined` + a non-`—` used-by. Both used-by paths exist (`corpus/knowledge/runtime-health-surface-processes.md` 10120 B, `corpus/lessons/round-43.md` 29655 B), so E11 correctly does not fire.

## 3. Independent recompute of every class (the receipt is checked, not trusted)

`recompute.py` (in my out dir, exit 0, output `recompute.out`) re-derives each predicate from the counter's own source text over `corpus/SOURCES.md`, read-only:

```
rows=222 distinct_ids=222 distinct_urls=115 distinct(url,scope)=208
W04 identity: distinct(url,scope) - distinct_urls = 208 - 115 = 93 ; sum(scopes-1) over multi-scope urls = 93 ; multi-scope urls = 29
E01 0   E02 0   E03 0   E04 0   E05 0   E06 0   E07 0   E08 0
E09 0   E10 0   E11 0   E12 0   W01 1 S481   W02 0   W03 0   W04 93
```

Every class reproduces exactly; the W04 figure is confirmed twice (the `208 − 115` identity and the independent `Σ(scopes−1)` sum). One precision note on E09: the counter's symbolic-cadence predicate is `s ~ /^[A-Za-z][A-Za-z0-9 _-]*$/` (`sources-census.sh:582`), so cells like `every round` (6 rows) are legal; a narrower reading would report 6 false E09s. That is a property of the counter's permissive grammar, recorded here as a reading aid, not a defect.

## 4. D4 — gate-registry-check: real invocation, selftest receipt, base and tip

### 4.1 `--help` (exit 0, `gate-help.out`)

```
usage: gate-registry-check.py [-h] [--repo REPO] [--rev REV] [--selftest]
Report tracked round counters whose SKILL.md registry rows are absent or meaningless.
  --repo REPO  repository to evaluate (default: current directory)
  --rev REV    git revision to evaluate (default: the working tree)
  --selftest   run the fail-capable fixture matrix and the lane-tip check
```

The real check invocation is therefore `python3 tools/gate-registry-check.py --repo <repo> [--rev <rev>]` — the `--repo` flag is **not** named in `SKILL.md:1325`, which documents only `[--rev REV]`.

### 4.2 Check on the lane — RED (exit 1)

| Invocation | Exit | Output |
|---|---|---|
| `python3 tools/gate-registry-check.py --repo . --rev 098df344d977a9047ea346a01a93c307887570b0` | **1** | `unregistered tools/round44-release-recheck-audit.py`, `unregistered tools/round44-verdict-ledger-audit.py`, `registered 31 unregistered 2 defective 0` (`gate-check-rev-tip.out`) |
| `python3 tools/gate-registry-check.py --repo .` (working tree) | **1** | identical byte-for-byte (`gate-check-worktree.out`) |

Population at the tip is 33 tracked counters (23 under `tools/`, 10 under `.ufo/waves/round-*/count-*.py`, `gate-population.tsv`); 31 have registry rows, `defective 0`. The two unregistered files are exactly this round's counters, and `grep` of `SKILL.md` finds neither their names nor `round44`/`round-44` anywhere (`grep -n "round44|round-44|release-recheck-audit|verdict-ledger-audit" SKILL.md` → no matches), so they are genuinely absent, not prose-only.

### 4.3 `--selftest` — RED, pass=5 fail=1 (exit 1) at tip AND at the frozen base

| Rev measured | Arm 6 (`lane-tip`) line | Tally | Exit | Receipt |
|---|---|---|---|---|
| `098df344d977` (lane `master`/`HEAD`) | `FAIL lane-tip 098df344d977: exit=1 line='registered 31 unregistered 2 defective 0'` | `GATE_SELFTEST pass=5 fail=1` | **1** | `gate-selftest.out`, `gate-selftest.err` (empty), `gate-selftest.exit` |
| `77d1bbf55c62` (frozen base, throwaway clone) | `FAIL lane-tip 77d1bbf55c62: exit=1 line='registered 31 unregistered 2 defective 0'` | `GATE_SELFTEST pass=5 fail=1` | **1** | `gate-selftest-base77d1bbf5.out` |

Arms 1–5 (hermetic fixtures `valid-row`, `thin-row`, `empty-exit-map`, `missing-path`, `prose-only`) all PASS; arm 6 alone fails, and it fails identically on both revs because both already track this round's two counters without `SKILL.md` rows. The base run is a `git clone --no-hardlinks` of the lane into my scratch with `master` forced to `77d1bbf5`; the receipt records the rev inline, and the clone is deleted.

### 4.4 Does `SKILL.md`'s documented line match? **No.**

`SKILL.md:1325` (same text at `77d1bbf5` and `098df344`), self-test column offset 549 in the line:

> …`--selftest` prints `GATE_SELFTEST pass=6 fail=0`; arms, controls and mutations `.ufo/waves/round-32/c2/SUMMARY.md`, `selftest-final.out` at the landed tip…

Measured at both revs: `GATE_SELFTEST pass=5 fail=1`, exit 1. The documented `pass=6 fail=0` is false on the tree it describes; this is the same stale statement round 42 (`R42A02`) and round 43 (`corpus/lessons/round-43.md:69`) recorded — it remains stale, and round 44 keeps it false by adding two more unregistered counters (population 31 → 33, registered still 31).

## 5. Defects

### D-X9-1 (lane docs, stale invariant): `SKILL.md:1325` documents a self-test tally the tool has not printed since round 35.

- Exact location: `SKILL.md:1325`, row `Gate registry completeness (round-32 repair)`, self-test cell — the clause `` `--selftest` prints `GATE_SELFTEST pass=6 fail=0` ``.
- Command that shows it: `python3 tools/gate-registry-check.py --selftest` → `FAIL lane-tip 098df344d977: exit=1 line='registered 31 unregistered 2 defective 0'` / `GATE_SELFTEST pass=5 fail=1`, exit 1 (`gate-selftest.out`); same at `77d1bbf5` (`gate-selftest-base77d1bbf5.out`).
- Proposed fix (not applied; proposal only): `proposed-SKILL-1325.diff` in the out dir replaces that clause with a revision-bearing statement — five hermetic arms plus a sixth arm on this repo's `master`, prints `pass=N fail=M`, exits 1 unless all six pass. Root fix is the other half of KQ54: add the two `tools/round44-*.py` rows at integration and the same line becomes true again.

### D-X9-2 (tool design, non-hermetic self-test arm): arm 6 measures the live lane branch, so `--selftest`'s exit code tracks working state, not the code under test.

- Exact location: `tools/gate-registry-check.py:333-350` — `run_git(str(lane_root), ["rev-parse", "--verify", "master"])` then `evaluate(...)` at that rev; `lane_root = Path(__file__).resolve().parent.parent`.
- Command that shows it: the two selftest receipts differ only in the measured rev (`098df344d977` vs `77d1bbf5`) while the code executed is identical — the clone run reaches its own `master` because the arm resolves relative to `__file__`, not the invoking repo. A receipt is therefore only interpretable with the rev printed (the arm does print it, which is why this is a design note and not an evidence gap).
- Proposed fix (proposal only): make the arm hermetic by copying the registry into a fixture and asserting the expected tally, or accept the non-hermetic arm but require the rev in the receipt (current behaviour) and stop documenting a fixed `pass=6 fail=0` anywhere. No code change made; the counter is FROZEN for this wave.

### Note (not a defect, for the integrator): this round keeps the KQ54 gate red until `SKILL.md` rows land.

`python3 tools/gate-registry-check.py --repo . --rev <landed tip>` will print `unregistered 2` at integration unless `tools/round44-release-recheck-audit.py` and `tools/round44-verdict-ledger-audit.py` each get a five-column row (KQ54, `corpus/QUALITY.md:362`). Both are reachable work for the L1 seat, not for me; stated here because the D3/D4 evidence makes the count exact.

## 6. Artifacts

All in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/X9Census/`:

| File | Content |
|---|---|
| `census-root-kama.out` / `.err` / `.exit` | validate `--root … kama`, 95 lines, empty stderr, exit 0 |
| `census-file-sources.out` / `.err` / `.exit` | validate `--file …/SOURCES.md`, 95 lines, empty stderr, exit 0 |
| `census-root-kama.rerun.out` / `.rerun.exit` | determinism rerun (byte-identical) |
| `census-mode-kama.out` / `.exit` | population: 222 rows, tier/status histogram, `FLEET.missing 0`, exit 0 |
| `classes.tsv` | every class code with count and present/absent |
| `recompute.py` / `recompute.out` / `.err` / `.exit` | independent class recompute (exit 0) |
| `gate-help.out` / `.exit` | `--help`, exit 0 |
| `gate-selftest.out` / `.err` / `.exit` | `--selftest` at tip, 6 arms, `pass=5 fail=1`, exit 1 |
| `gate-selftest-base77d1bbf5.out` / `.err` / `.exit` | `--selftest` at frozen base (throwaway clone), `pass=5 fail=1`, exit 1 |
| `gate-check-rev-tip.out` / `.err` / `.exit` | real check at tip, 2 unregistered, exit 1 |
| `gate-check-worktree.out` / `.err` / `.exit` | real check on the working tree, identical, exit 1 |
| `gate-population.tsv`, `gate-lineage.txt`, `lane-head.txt` | 33-counter population; base/tip lineage; measured rev |
| `proposed-SKILL-1325.diff` | proposed doc fix (unified diff, one line) |

Scratch `/fast/scratch/hyaku/kama-r44/X9Census` (containing the only clone) removed before finishing. No tool installs were needed; no pacman, no network fetch, no writes outside this out dir and my scratch.

Checks the L1 should run after integration: `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` (expect exit 0, 93 W04 / 1 W01 / 1 ok) and `python3 tools/gate-registry-check.py --repo . --rev <landed tip>` (expect exit 0 and `unregistered 0` once the two round-44 rows exist), and `python3 tools/gate-registry-check.py --selftest` (expect `pass=6 fail=0` only after that registration).
