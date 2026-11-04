# MT01 — mutation test of the three round-80 instruments

Seat **MT01Mutation** (leaf, mutation-tester). Round 80, wave 1.
Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; base `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`;
C1 sealed revision `a9b4543f14625d0f37daa42ef664ee6f6ea975ea`.
Lane tip at test time: `97cfec8a21d6b45e6584814d3382d3f7bd1b33d1` (`git rev-parse master`).

Tested bytes (sha256, copies in `MT01Mutation/pristine-copy/`):

| module | sha256 | note |
|---|---|---|
| `tools/round80-selfrecord-round79.py` | `61e49d4fcdac3a4d987ef693f50c33b9ee5054905973d0981d535edc8129e46d` | first copy `39750885…` (tip `fe7b978`) was revised mid-run by `28debbcf`; all four C1 mutants re-applied and re-caught on the current bytes |
| `tools/round80-engine-pin-relations.py` | `22da9bd41d3475bd4e818548437d148fe2762b7bebf9256c84aa56afc8b0ba49` | unchanged across the run |
| `tools/round80-ollama-census.py` | `5e3543a6445474a5fd9f383ed6903b676626e8ad37beb59a763cb19e0fa03e4c` | unchanged across the run |
| `registry/engine-pin-relations.tsv` | `15a2a25f8a7f9fca8f5601cb3daac61599bd4a17850a4cccd8b79332472fe134` | used byte-identically in the C2 lane runs |

No lane file was edited by this seat (hashes above are the lane's). Each mutant is a copy under
`MT01Mutation/mutants/<tag>/`; fixtures and git repos lived under
`/fast/scratch/hyaku/kama-r80/MT01Mutation` and were deleted after the receipts were copied here.
Only read-only git was used (`show`, `cat-file`, `rev-parse`, `ls-tree`); no commit/add/checkout.

## Method

1. Pristine copy of each module; `--selftest` must be green before any mutant is graded.
2. Named source mutations: one anchored replacement per mutant, asserted to match exactly once.
3. For each mutant: the module's own `--selftest` **plus** the fixtures it does not cover —
   - C1: synthetic git repos (valid corrections; `at` = a middle commit; a bogus block on a
     fresh fact; corrections outside `## Corrections`), graded with
     `--repo <fixture> --sealed <sealed> --tip <tip>`;
   - C2: the lane's committed tag lists under `--tags-dir`, register copies (as-is, and with
     the `llama.cpp b7200` row removed), and a synthetic git repo whose receipt exists in the
     worktree but is not committed at the tip;
   - C3: crafted probe documents through `grade()`, audit registers (`audit-green`,
     `audit-other-engine`, `audit-one-engine`), and the real pinned-Ollama fixture leg
     (`--probe tools/kama-probe.sh`, v0.40.11 child, scratch HOME/model store, torn down).
4. The same command runs on pristine, mutant, and a byte-identical restored copy; a red
   baseline is inconclusive. Restored copies equal pristine (`restored_sha256 == pristine_sha256`)
   and re-run the baseline outputs exactly (`matches_baseline: true` for c1/c2/c3).
5. Mutants are graded on behavior only; no lane module was patched.

## Pristine baselines

| counter | command | exit | line |
|---|---|---|---|
| C1 | `python3 tools/round80-selfrecord-round79.py --selftest` | 0 | `SELFRECORD_R79_SELFTEST pass=9 fail=0` |
| C1 | `python3 tools/round80-selfrecord-round79.py --repo <lane>` | 0 | `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0` |
| C2 | `python3 tools/round80-engine-pin-relations.py --selftest` | 0 | `PIN_RELATIONS_SELFTEST pass=12 fail=0` |
| C2 | `--repo <lane> --tags-dir <lane>/.ufo/waves/round-80/measured/after/c2-tags` | 0 | `PIN_RELATIONS engines=3 refs=5 unexplained=0` |
| C3 | `python3 tools/round80-ollama-census.py --selftest` | 0 | `OLLAMA_CENSUS_SELFTEST pass=6 fail=0` |
| C3 | `--repo <lane> --audit` | 0 | `CLASS_ENGINES engines=2 verified=2 stale=0` |
| C3 | real fixture leg: `--repo <lane> --work <scratch> --out <scratch> --probe tools/kama-probe.sh` | 0 | `OLLAMA_CENSUS port=41579 engine=ollama unregistered=1 governed=1 class_missing=0` |

The C3 real leg ran version `0.40.11`, `doc_no` registered=`no`, `doc_yes` registered=`yes`,
`teardown {returncode: 0, port_closed: true}`; `pgrep -f ollama-v0.40.11` was empty afterwards.

## Mutants

`CAUGHT` = the mutant's `--selftest` failed **or** a detector's exit/stdout differed from the
pristine baseline on the same bytes. Every mutant was applied to the tested bytes above.

| # | module | mutation | caught by | baseline → mutant |
|---|---|---|---|---|
| c1-m1 | C1 | drop the `new != seen_tip` re-derivation: any `new` answers a block | `--selftest` (`new-not-rederived`) + bogus-block fixture | selftest 9/0 → 8/1; fixture exit 1 `unbacked=1` → exit 0 `unbacked=0` |
| c1-m2 | C1 | `at` need only resolve; the `resolved != sealed` check dropped | fixture: valid 40-hex `at` naming a middle commit | exit 1 `F6 … reasons=at-not-sealed` → exit 0 `corrected=3 unbacked=0` |
| c1-m3 | C1 | a fact counts corrected when any block is present (old/at/new not re-derived) | `--selftest` (4 arms) + ancestor-`at` + bogus-block fixtures | selftest 9/0 → 5/4; fixtures exit 1 → exit 0 |
| c1-m4 | C1 | `verdict()` ignores `unbacked` (`mismatches or unbacked` → `mismatches`) | fixture: garbage block on a fresh fact | exit 1 `unbacked=1` → exit 0 (same line) |
| c2-m1 | C2 | version keys emitted as dotted strings → lexicographic comparison | lane register + committed tag lists; synthetic register | exit 0 `engines=3 refs=5 unexplained=0` → exit 1 `stale-tag line 6 vllm v0.32.0 … derived=behind/31/v0.9.2` |
| c2-m2 | C2 | a missing ref counts as covered when another ref of the same engine has a row | register with the `llama.cpp b7200` row removed | exit 1 `missing-ref engine=llama.cpp ref=b7200` → exit 0 `engines=3 refs=4 unexplained=0` |
| c2-m3 | C2 | `receipt_committed()` returns `True` unconditionally | `--selftest` (`missing-receipt`) | selftest 12/0 → 11/1 |
| c3-m1 | C3 | the `no` registry leg is written with the port (`write_registry(no_reg, port)`) | real fixture leg (only) | exit 0 `OLLAMA_CENSUS port=41579 … unregistered=1 governed=1 class_missing=0` → exit 1 `port=48777 … unregistered=0 governed=0` + `legs-agree`, `unregistered-leg=yes`, `governed-count`, `unregistered-count` |
| c3-m2 | C3 | the per-leg `governed` count check is removed | crafted docs through `grade()` | findings `[governed-count leg=no governed=1]` → `[]` |
| c3-m3 | C3 | `--audit` drops `engine in text` (receipt may name another engine) | `audit-other-engine` fixture | exit 1 `receipt-names-other-engine ollama …` → exit 0 `engines=2 verified=2 stale=0` |
| c3-m4 | C3 | `--audit` drops the two-engine requirement (`len(engines) < 2`) | `audit-one-engine` fixture | exit 1 `one-engine engines=1` → exit 0 `engines=1 verified=1 stale=0` |

Result: **11 mutants, 11 CAUGHT, 0 survived, 0 inconclusive.** Mutants c1-m2, c1-m4, c2-m1,
c2-m2 and c3-m1 survive the module's own `--selftest`; each is caught by the fixture named in
the table (c3-m1 only by the real fixture leg — the registry-leg coupling lives in
`run_fixture()`, which `--selftest` does not exercise).

## Findings for the L1

A survivor is a coverage finding, not permission to change the contract. These are recorded
observations, not mutant verdicts:

1. **C1-OBS2 (highest): the F2 tip leg is no longer graded, and the module cites a "freeze
   divergence 4" that the lesson does not record.** The current module sets
   `SEALED_BOUND = {"F2"}` and grades F2 only at the sealed revision. The lesson at master
   (`97cfec8`) records divergences **1–3 only**; `grep -rn 'divergence 4'` over `corpus/`,
   `plans/`, `LOG.md` finds nothing. Evidence of the behavioral difference: on the same tip,
   the pre-change bytes (`39750885…`) print
   `FACT F2 … tip=population=sources:297,knowledge:53 status=stale` and
   `SELFRECORD_R79 claims=6 mismatches=1 corrected=3 unbacked=0`, exit 1; the current bytes
   print `F2 … status=fresh` and the target line, exit 0. The frozen predicate requires every
   fact to "match the same fact re-derived at the tip"; the tip population is `297/53` while the
   sealed value is `293/52`. Either the lesson must record divergence 4 (the lane's convention
   for divergences 1–3) or the counter must grade F2 at the tip — the frozen `corrected=3`
   leaves no correction budget for F2.
2. **C2-OBS1: `receipt_committed()` accepts a worktree file that is not committed at the tip.**
   Synthetic git repo with `receipts/alpha.txt` untracked: `PIN_RELATIONS engines=2 refs=3
   unexplained=0`, exit 0; deleting the file flips to `missing-receipt`, exit 1. The predicate
   requires "every row's receipt path exists and is committed"; the fallback clause enforces
   existence only, and no selftest case uses a git repo, so the committed leg is unexercised.
3. **C3-OBS1: the selftest does not carry the arms the control bullet declares.** The C3 control
   names `absent-probe`, `probe-error`, `class-missing` and `one-engine` as selftest arms; the
   landed selftest covers `both-legs`, `class-missing`, `legs-agree`, `owner-not-ollama`,
   `verdict-not-model-ok`, `counts-do-not-move` (`pass=6 fail=0`). Mutant c3-m4 (one-engine
   guard removed) survives `--selftest` and is caught only by the audit fixture.
4. **C1-OBS1 (minor): corrections are read from the whole lesson, not the declared
   `## Corrections` container.** A lesson whose blocks sit under `## Notes` scores
   `corrected=3 unbacked=0`, exit 0. The C1 scope ruling names the §Corrections container.

## Receipts

Seat directory (durable): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/MT01Mutation/`

| receipt | contents | produced by |
|---|---|---|
| `MT01.json` | full matrix: tested hashes, per-mutant mutation/commands/outputs/exits, observations, restoration evidence | `finalize.py` (exit 0) |
| `mutants/<tag>/<module>` (11 files) + `mutants/index.json` | the mutated sources, one anchored replacement each; hashes match `MT01.json` | `apply_mutants.py` (exit 0) |
| `pristine-copy/` | the three tested modules plus `round80-selfrecord-round79.py.pre-28debbcf` | `cp` |
| `logs/matrix.json` | raw driver matrix (full stdout/stderr per check) | `drive.py` (exit 0) |
| `logs/final-c{1,2,3}-selftest.out` | pristine selftests, exits 0 | direct runs |
| `logs/c1-pristine-lane.out`, `logs/c2-pristine-lane.out`, `logs/c3-pristine-audit.out` | lane target lines, exits 0 | direct runs |
| `logs/c1-oldbytes-lane.out` | pre-change C1 bytes on the tip: F2 stale, exit 1 | direct run |
| `logs/c3run-pristine.{log,json}`, `logs/c3run-m1.{log,json}` | real fixture leg, pristine exit 0 / mutant exit 1, child torn down | direct runs |
| `logs/obs-c2-uncommitted-receipt.out`, `logs/obs-c2-missing-receipt-control.out` | C2-OBS1 evidence: exit 0 with untracked receipt, exit 1 after deletion | direct runs |
| `fixtures/{gen_c1,gen_c2,gen_c3,apply_mutants,drive,finalize}.py` | fixture builders, mutation applier, detectors | authored this seat |

Commands and exit codes (representative):

- `python3 pristine/round80-selfrecord-round79.py --selftest` → exit 0
- `python3 pristine/round80-engine-pin-relations.py --selftest` → exit 0
- `python3 pristine/round80-ollama-census.py --selftest` → exit 0
- `python3 drive.py "$S" "$LANE"` → exit 0 (11 mutants graded, restored runs match baselines)
- `python3 pristine/round80-ollama-census.py --repo "$LANE" --work "$S/c3work-pristine" --out "$S/out/c3run-pristine.json" --probe "$LANE/tools/kama-probe.sh"` → exit 0
- `python3 mutants/c3-m1-legs-share-registry/round80-ollama-census.py --repo "$LANE" --work "$S/c3work-m1" --out "$S/out/c3run-m1.json" --probe "$LANE/tools/kama-probe.sh"` → exit 1

Scratch `$S = /fast/scratch/hyaku/kama-r80/MT01Mutation` was deleted after these receipts were
copied; the pinned Ollama child was terminated and its port closed by the module
(`teardown.port_closed=true`), and no listener process remained. No tool was installed or
upgraded for this seat.
