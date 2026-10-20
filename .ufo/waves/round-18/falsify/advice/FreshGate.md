VERDICT: partial — 4/4 fresh source mutants survive the built-in gate selftest; all four are killed by distinguishing off-suite detectors after green pristine runs and byte-exact restoration.

# FreshGate — scoped fresh-mutation evidence

Seat: `KamaR18.FreshGate`. Subject revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
This is an author-wave mutation probe, **not** an outside non-author judgment or a claim-admission decision. No production fix is proposed or integrated.

## Axes and scope

Axes: exact HTTP-status admission; loading-response multiplicity; v3 boolean-schema integrity; minimum-schema compatibility; targeted detector attribution and exact restoration.

Required context read: `corpus/lessons/round-18.md:13–29,116–145,152–176`; `SCORECARD.md:737–760`; `corpus/QUALITY.md:125–133` (KQ23/KQ24); official `runs/commands.json` gate invocations and `runs/gate-selftest.stdout`. The official gate selftest output hashes to `da22d995d478ac6cf941e944e70cf365bb3507606e54664d9cf5c1a4391aca8f` and says 61 receipt mutations plus unreadable case. The current cloned gate selftest reproduces that exact stdout on pristine, every mutation, and every restoration. No official counting command was run against the live lane (or rerun in this seat).

Only the assigned clone's gate was mutated. There were four independently applied defects; FG1 changes two duplicated status guards belonging to one logical predicate. No combined mutants. The six off-suite receipts were frozen before any detector run and reused unchanged. Each phase runs the same built-in selftest and six-case off-suite suite; no assertions were weakened following a survival. The experiment source below never edits the gate; source mutations/restorations used surgical edits at the exact sites below.

## Preregistration and clone

Executed (exit 0, no stdout/stderr):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-FreshGate && git -C /tmp/kama-r18-falsify-FreshGate switch -q -c seat/FreshGate 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

Preregistration was written before `prepare`, before pristine detection, and before the first mutant. Its SHA-256 remained `5e8693c8459f43b385afc1bf2bcd236bd95b9acfc35c4c7e423ed86a27176d46` in all twelve phase records. Full preregistration and exact executable experiment source are embedded below, rather than leaving ephemeral `/tmp` references as the only evidence.

## Mutants and attributable results

Fresh-source-mutant denominator: **4**. Built-in selftest: **0 killed, 4 survived, 0 equivalent, 0 site_missing, 0 inconclusive**. Off-suite detector: **4 killed, 0 survived, 0 equivalent, 0 site_missing, 0 inconclusive**. These are separate denominators from the named round-17 set; a built-in survivor is not silently relabelled a built-in kill because an added detector catches it.

| ID | Exact pristine site in `tests/llamacpp-live/check-receipt.py` | Smallest defect | Off-suite distinguishing receipt | Built-in result | Off-suite result |
|---|---|---|---|---|---|
| FG1 | 906 and 932 | `if models_cap_status != 200:` → `if not (200 <= models_cap_status < 300):` at both duplicated guards | Ready models status 201, exact ids/owners/hash unchanged, both observed statuses consistently 201 | Survived, exit 0 | Killed: targeted bad receipt changes INVALID/1 → VALID/0 → INVALID/1 |
| FG2 | 1220–1221 | `transition_counts[digest] = (transition_counts.get(digest, 0) + 1 + repeats)` → `transition_counts[digest] = 1 + repeats` | Two recorded loading rows with the same body digest, each repeats=0; retained repeats=0 and total=1 undercount the two recorded responses | Survived, exit 0 | Killed: understated receipt INVALID/1 → VALID/0 → INVALID/1; correctly counted positive also becomes INVALID only under mutant |
| FG3 | 795 | `if not isinstance(evaluated, bool):` → `if evaluated not in (True, False):` | `models_alias_id.evaluated` is JSON integer 1 instead of boolean true; all other receipt bytes follow valid fixture | Survived, exit 0 | Killed: bad type INVALID/1 → VALID/0 → INVALID/1 |
| FG4 | 2096 | `version < minimum` → `version != minimum` | Valid v3 pass receipt under `--require-schema v2` with all four pins | Survived, exit 0 | Killed: legal above-floor schema VALID/0 → INVALID/1 → VALID/0 |

**Why these are fresh and non-equivalent:** FG1 preserves rejection of existing status-503 selftest (`:1896–1900`) while exposing the untested 2xx/exact-200 distinction on an evaluated pass receipt. FG2 preserves existing forged-total and 257-distinct-body cases (`:1916–1919,1967–2000`) but loses multiplicity only when a digest recurs in multiple transition rows. FG3 continues rejecting the existing string `evaluated="yes"` (`:1927–1930`) but accepts Python's equality-compatible integer 1. FG4 preserves all existing floor cases (`:1873–1882`) because they test exact-match successes and below-floor failures, not an above-floor success. Their distinguishing receipt changes are not any existing selftest case. Every mutant has a different witness class, and all unrelated off-suite cases retain their expected result (FG2's symmetric count-control failure is attributable to the same accumulator defect).

### Actual targeted stdout (all corresponding stderr empty)

Pristine and restored outputs were identical, including hashes. Full unique stdout and the per-phase output-ID ledger are retained below. Key transitions:

- FG1 pristine/restored: `models_alias_id: captures.models.status 201 != 200 (round-18 RevTriStateDesign)` and `models_owned_by_llamacpp: captures.models.status 201 != 200`; mutant: `VALID .../FG1-status201.json`.
- FG2 pristine/restored: `loading_503_bodies digests/repeats do not cover the stored /v1/models 503 transitions exactly` plus `check 'loading_envelope_graded' passed True != re-derived False`; mutant: `VALID .../FG2-understated.json`. Its correctly retained control is VALID on pristine/restored and has those same two targeted count assertions under the mutant.
- FG3 pristine/restored: `check 'models_alias_id': evaluated is not a boolean`; mutant: `VALID .../FG3-integer-evaluated.json`.
- FG4 pristine/restored: `VALID .../FG4-v3-minimum-v2.json`; mutant: `schema 'kama-llamacpp-live/v3' is below --require-schema v2`, exit 1. This deliberately implausible message is the observable consequence of the minimum-to-equality defect, not a genuine below-floor receipt.

Every phase also accepts the plain valid v3 receipt with `--require-schema v3`; FG1–FG3 red results are not caused by an invalid original positive. A pristine gate returning INVALID on the deliberately bad witnesses is a **green detector result**, not a baseline failure. FG4 uses a valid positive witness, so its mutation-induced false rejection is also a detector kill.

## Hashes and exact restoration

At start the live-lane and clone gate both hashed to pristine P below. Each mutation was reversed before the next mutant. All four restored phases re-hashed to P **before** running the same detector suite, and all restored suites exited 0. Final `sha256sum` again recorded P. No production bytes were written.

| Label | Gate SHA-256 |
|---|---|
| P: all pristine and restored bytes | `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` |
| FG1 mutated | `08b441579677f57f5f4e75a4cdb8f0223fe9d75ae931caab3206274ecfdb70c8` |
| FG2 mutated | `da6471c0d3884c30d63d863a807c5c93b57d3f1ddd232fbfc8d14be85a481741` |
| FG3 mutated | `e06a426098461e7bb7fff9e7f441a3c425af30252e11d0e9da5f42f6670ad921` |
| FG4 mutated | `dfe437593972c4a249a545975186b54f23643c5aa3dee147def60d0d954063f7` |

The exact detector source SHA-256 is `ddf07fb015730c953313ba2243098bc804e19a0af7a64c255904272d211896f1`. The official commands JSON read at the start hashed to `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`.

### Frozen off-suite fixture identities

All fixture paths were absolute children of `/tmp/kama-r18-falsify-FreshGate/FreshGate-lab/`. Their exact construction from the pinned, pristine `_selftest_receipt_v3()` is in the embedded experiment source. Synthetic pins intentionally use the gate's fixture values; they are not claims of fixture/model authentication against installed files.

| Fixture | SHA-256 |
|---|---|
| `valid.json` | `2d617126fe19f7fdc60c1dfad34afbf02f35f6865c6d5ab69b73b4d0af94e0b4` |
| `FG1-status201.json` | `a7771866605ddbb886246e0dca5fdc3fdc335e251012467fef2dcdc9c031cbe0` |
| `FG2-understated.json` | `f8bbd1b4fc752790e2bdef5047769fee72364289714125e354b205663f3f6777` |
| `FG2-valid-two-bursts.json` | `44a9f8e55dd53f9725ec85be91b01981cd013c2ecca4621e6f837435fb0ececd` |
| `FG3-integer-evaluated.json` | `b8366cd106a881c6ef6e5f4a93a86de2a2abee9aebf26bfd130dd65b0759e3df` |
| `FG4-v3-minimum-v2.json` | `2d617126fe19f7fdc60c1dfad34afbf02f35f6865c6d5ab69b73b4d0af94e0b4` |

## Executed detector commands and phase ledger

`prepare` command (exit 0): `/usr/bin/python3 -B /tmp/kama-r18-falsify-FreshGate/FreshGate-experiment.py prepare`.
Each row below is an actual command `/usr/bin/python3 -B /tmp/kama-r18-falsify-FreshGate/FreshGate-experiment.py <phase> <ID>`, with cwd `/tmp/kama-r18-falsify-FreshGate`. The embedded source gives every exact inner argv: `/usr/bin/python3 -B <absolute-gate> <absolute-receipt> --require-schema v3|v2` plus model=`a`×64, server=`b`×64, probe=`c`×64, tool=`9`×64 pins. The selftest inner argv is `/usr/bin/python3 -B /tmp/kama-r18-falsify-FreshGate/tests/llamacpp-live/check-receipt.py --selftest`.

The fixed run order within each phase is: **selftest, valid, FG1-status201, FG2-understated, FG2-valid-two-bursts, FG3-integer-evaluated, FG4-v3-minimum-v2**. The seven inner processes are launched concurrently. Restored FG1/pristine FG2, restored FG2/pristine FG3, and restored FG3/pristine FG4 were run as concurrent pairs on identical pristine bytes; no edit occurred while either paired phase was running.

| ID/phase | Outer exit | Inner exit vector (fixed order) | Selftest detector | Off-suite detector | Actual stdout IDs (fixed order) |
|---|---:|---|---|---|---|
| FG1/pristine | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG1/mutated | 1 | `0, 0, 0, 1, 0, 1, 0` | green | red (targeted) | O1, O2, O8, O4, O5, O6, O7 |
| FG1/restored | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG2/pristine | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG2/mutated | 1 | `0, 0, 1, 0, 1, 1, 0` | green | red (targeted) | O1, O2, O3, O9, O10, O6, O7 |
| FG2/restored | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG3/pristine | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG3/mutated | 1 | `0, 0, 1, 1, 0, 0, 0` | green | red (targeted) | O1, O2, O3, O4, O5, O11, O7 |
| FG3/restored | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG4/pristine | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |
| FG4/mutated | 1 | `0, 0, 1, 1, 0, 1, 1` | green | red (targeted) | O1, O2, O3, O4, O5, O6, O12 |
| FG4/restored | 0 | `0, 0, 1, 1, 0, 1, 0` | green | green | O1, O2, O3, O4, O5, O6, O7 |

All 84 directly recorded inner invocations had empty stderr (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). There were no timeouts, crashes, missing source sites, or invalid-pristine runs. Outer exit 1 is the expected killed-mutant detector failure, not a tool execution fault.

### Complete distinct stdout, deduplicated without alteration

Each code block includes its actual final newline. The phase ledger above binds every invocation to its complete stdout and SHA-256. No omitted failure trace or partial stdout is substituted.

**O1** — SHA-256 `da22d995d478ac6cf941e944e70cf365bb3507606e54664d9cf5c1a4391aca8f`

```text
selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected
```

**O2** — SHA-256 `3f443c10906ce4754ae5b5922b5903938413fae059643c4aef4c56558f73b8bd`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/valid.json
```

**O3** — SHA-256 `b30fa93231ec39c68d9d1c12d1e29558b7c1d447d11a0581a4083d4f1fe85b68`

```text
INVALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG1-status201.json: 2 problem(s)
  - models_alias_id: captures.models.status 201 != 200 (round-18 RevTriStateDesign)
  - models_owned_by_llamacpp: captures.models.status 201 != 200
```

**O4** — SHA-256 `7226c9919e33175acf58702f6771cab3f8e37d889ab3ef007598c377498f20bd`

```text
INVALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG2-understated.json: 2 problem(s)
  - loading_503_bodies digests/repeats do not cover the stored /v1/models 503 transitions exactly
  - check 'loading_envelope_graded' passed True != re-derived False
```

**O5** — SHA-256 `bab504b0a5e18f2850cd88a896ff99744e2bae14533cb17c7fea606b67620dc1`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG2-valid-two-bursts.json
```

**O6** — SHA-256 `4785b0318a2a35479ef4509bd99aa3c77ae3f355321b9c146372b1bd7fda208d`

```text
INVALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG3-integer-evaluated.json: 1 problem(s)
  - check 'models_alias_id': evaluated is not a boolean
```

**O7** — SHA-256 `ef289c0eddfa9c11cc781c36d9e5f354156896c688a387156dac69102abd692d`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG4-v3-minimum-v2.json
```

**O8** — SHA-256 `b464001f960e929702816883bb061d2c415be8da48d8dbfe006c66dcec966fa4`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG1-status201.json
```

**O9** — SHA-256 `2d8175d0713f92da9d4476e3f92ed4c0104dd9dc94e19bf8b4dac6bc3828db4e`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG2-understated.json
```

**O10** — SHA-256 `c20a4446de7f0f16da0742225e7ada372971dfbaa55190007d7ed548f7815b71`

```text
INVALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG2-valid-two-bursts.json: 2 problem(s)
  - loading_503_bodies digests/repeats do not cover the stored /v1/models 503 transitions exactly
  - check 'loading_envelope_graded' passed True != re-derived False
```

**O11** — SHA-256 `c58f3c57e7483a0c27342d482dbb937488c39d86c8781897550b3ae442b74a93`

```text
VALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG3-integer-evaluated.json
```

**O12** — SHA-256 `5f479f28abfebb01a6c83a8612688995acb83241adf4b3d622f43bb3e117c72a`

```text
INVALID /tmp/kama-r18-falsify-FreshGate/FreshGate-lab/FG4-v3-minimum-v2.json: 1 problem(s)
  - schema 'kama-llamacpp-live/v3' is below --require-schema v2
```

### Original per-phase raw JSON digests

These scratch artifacts were not copied back; the output ledger and exact source above/below preserve the experiment in this sole permitted report. Digests identify the original command/result records, including per-run timings, argv, PGIDs, cleanup flags, stdout and stderr.

| Scratch filename | SHA-256 |
|---|---|
| `FG1-pristine.json` | `0fe6de2a4da99fd85d3a1cc1ec32417da842d7173ec68cf751c1e2af56912867` |
| `FG1-mutated.json` | `7045f9b78e7cf7ce35aecc1b2a0239c092ce0d976178891683c98358c8ba145c` |
| `FG1-restored.json` | `e5c4201011eccb4e44d32a2613c6bb1c09f492c3d8016dbda0d17732d716e968` |
| `FG2-pristine.json` | `21175dc2830eff938d2e7ef35a9b1ea35ff63e6e0d45b47097b9ec568fc61e05` |
| `FG2-mutated.json` | `e4e3033b097e3de742aa92aff205074daf2526cc1bc8edb4446d8b75bb3b8fc3` |
| `FG2-restored.json` | `e5de6e81e7cfb8ea8fd586cb39d318e91f58a726d21158d5117cb8a621887816` |
| `FG3-pristine.json` | `4213a07f3ddaa4b13ca4c658d988fcf049370abeeb769acb6861311bb07b8b4e` |
| `FG3-mutated.json` | `c00bc6e7719382c1cf00e667b01f8ec9128024a028df45d0c7074aa5ee6a0bd2` |
| `FG3-restored.json` | `9667fef45cb5d17a9dcfb64df63ab2886762cdb5634fa2257c70e171c68de04f` |
| `FG4-pristine.json` | `54220ae066c8fd9f39ce80b62d780e595afd5a76c24555c3cd777d2cd70d8fc8` |
| `FG4-mutated.json` | `f00da18198a558bccc775079d9f115bfb64c116c8f349a8e45c7df183b65f64e` |
| `FG4-restored.json` | `a72f8055a61b162fccee39084b5027c2ab22401f7845df698367ad096dd1ec3c` |

## Limits, isolation, installs, and claim implications

- **No production defect established by these four probes:** the pristine v3 gate rejects all three bad off-suite witnesses and accepts the above-floor positive. The demonstrated defect is **selftest coverage**: all four plausible source regressions survive the shipped built-in detector. This does not refute C2's expressly bounded named-survivor repair (`round-18.md:21–24,139–145`; `SCORECARD.md:753–760`), and it cannot support a claim of general immunity.
- The off-suite controls are synthetic receipts derived from a pinned test builder, not live llama.cpp observations. FG2 exercises the validator's language for two recorded same-digest transition rows; it does not establish that a particular live sampling schedule emits that synthetic sequence. No model quality, registered-consumer health, producer/gate runtime agreement, process ownership or signal behavior was measured here.
- Subprocess deadline was 20 seconds each; outer phase deadline 40 seconds. Actual maximum directly recorded duration was 2.461 seconds. All child groups were killed/checked after completion; tempfile writes were redirected into this seat's scratch tree by `TMPDIR`. No HTTP server, socket bind, model load, other runtime, systemd action, global configuration or registered port was used.
- Tool substrate: `/usr/bin/python3`, Python `3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]`; existing Git/coreutils/procps/iproute2 commands only. **Installs/updates: none.** Pacman was not invoked. Operator RULES.md was read.
- No subagents, fleet mutation, index writes, jj operations, interactive-session/config/credential/history-store access, or environment-value dumps. Only the isolated clone and this report were written. No build, lint, formatter or unassigned runtime/counting suite was run.
- Coverage observation only; L1 owns any admission/integration decision. The detector additions are recorded as experiment source, not shipped changes.

### Final process/listener evidence

The following is the actual final cleanup observation after all detector phases. `ps` output was filtered for recorded process-group IDs and this absolute scratch path; `ss` output was filtered for recorded process IDs. Full unrelated host listener/process lists were not dumped. Every gate/selftest child was started in its own process group, and all groups (including inherited selftest descendants) were absent; the experiment runner itself never opens sockets. Thus no seat-owned listener remains.

```json
{
  "recorded_process_groups": [
    1904115,
    1904117,
    1904121,
    1904122,
    1904123,
    1904125,
    1904126,
    1913315,
    1913317,
    1913320,
    1913321,
    1913322,
    1913325,
    1913326,
    1925418,
    1925421,
    1925424,
    1925428,
    1925430,
    1925431,
    1925433,
    1925434,
    1925436,
    1925438,
    1925439,
    1925440,
    1925442,
    1925443,
    1987933,
    1987936,
    1987939,
    1987943,
    1987944,
    1987947,
    1987954,
    2078605,
    2078607,
    2078610,
    2078613,
    2078617,
    2078618,
    2078620,
    2078623,
    2078624,
    2078628,
    2078629,
    2078630,
    2078631,
    2078633,
    2108894,
    2108895,
    2108897,
    2108900,
    2108901,
    2108904,
    2108905,
    2117944,
    2117945,
    2117948,
    2117949,
    2117952,
    2117955,
    2117956,
    2117958,
    2117959,
    2117963,
    2117964,
    2117965,
    2117966,
    2117967,
    2123332,
    2123333,
    2123335,
    2123337,
    2123339,
    2123341,
    2123342,
    2125566,
    2125568,
    2125571,
    2125572,
    2125574,
    2125576,
    2125577
  ],
  "groups_still_present_after_each_run": 0,
  "ps_command": [
    "/usr/bin/ps",
    "-eo",
    "pid=,pgid=,args="
  ],
  "ps_exit": 0,
  "matching_seat_processes": [],
  "ss_command": [
    "/usr/bin/ss",
    "-ltnp"
  ],
  "ss_exit": 0,
  "matching_recorded_pid_listeners": [],
  "child_timeout_count": 0,
  "direct_subprocess_count": 84,
  "max_seconds": 2.461
}
```

## Exact preregistration source

`/tmp/kama-r18-falsify-FreshGate/FreshGate-preregister.json` (UTF-8, final newline):

```json
{
  "seat": "KamaR18.FreshGate",
  "revision": "1c325b2e58fcfdc6761f645b44cedfb1d65243e6",
  "axes": ["exact status admission", "loading multiplicity accounting", "v3 boolean schema integrity", "minimum-schema compatibility", "bounded detector attribution and exact restoration"],
  "subject": "/tmp/kama-r18-falsify-FreshGate/tests/llamacpp-live/check-receipt.py",
  "detectors": ["unchanged built-in --selftest", "off-suite fixture suite with v3 four-pin CLI gates"],
  "preregistered_before_execution": true,
  "mutants": [
    {
      "id": "FG1",
      "site": "tests/llamacpp-live/check-receipt.py:906,932",
      "before": "if models_cap_status != 200:",
      "after": "if not (200 <= models_cap_status < 300):",
      "defect": "Treat any successful HTTP status as the documented exact ready status, at the duplicated alias/owner guards.",
      "witness": "A v3 pass receipt with models capture status 201 and both observed.status values consistently 201; all ids, owners, hashes and other evidence unchanged.",
      "expected_pristine_witness": "exit 1; both models status assertions",
      "expected_mutated_witness": "exit 0 VALID",
      "expected_selftest": "survive; status 503 remains rejected"
    },
    {
      "id": "FG2",
      "site": "tests/llamacpp-live/check-receipt.py:1220-1221",
      "before": "transition_counts[digest] = (transition_counts.get(digest, 0) + 1 + repeats)",
      "after": "transition_counts[digest] = 1 + repeats",
      "defect": "Overwrite an earlier same-digest burst rather than accumulate loading responses.",
      "witness": "Two /v1/models 503 transitions with the same exact body/digest, each repeats=0; retained body repeats=0 and observed.total_503_responses=1 understate the two recorded responses.",
      "expected_pristine_witness": "exit 1; exact digests/repeats coverage and loading passed re-derivation",
      "expected_mutated_witness": "exit 0 VALID",
      "expected_selftest": "survive; its loading rows have one transition per digest"
    },
    {
      "id": "FG3",
      "site": "tests/llamacpp-live/check-receipt.py:795",
      "before": "if not isinstance(evaluated, bool):",
      "after": "if evaluated not in (True, False):",
      "defect": "Use equality membership instead of the JSON boolean type requirement, admitting integer 1/0.",
      "witness": "An otherwise valid v3 pass receipt with models_alias_id.evaluated=1 (JSON integer, not true).",
      "expected_pristine_witness": "exit 1; models_alias_id evaluated is not a boolean",
      "expected_mutated_witness": "exit 0 VALID",
      "expected_selftest": "survive; existing nonboolean evaluated case is a string, not integer"
    },
    {
      "id": "FG4",
      "site": "tests/llamacpp-live/check-receipt.py:2096",
      "before": "if version is not None and version < minimum:",
      "after": "if version is not None and version != minimum:",
      "defect": "Accidentally implement an exact schema match instead of a minimum supported version.",
      "witness": "A valid v3 pass receipt gated with --require-schema v2 and all four identity pins.",
      "expected_pristine_witness": "exit 0 VALID",
      "expected_mutated_witness": "exit 1; v3 incorrectly reported below v2",
      "expected_selftest": "survive; its valid floor tests only use exact matching versions"
    }
  ],
  "bounds": "Four fresh mutants, independently applied/restored; no production changes, live server, other runtime, socket binding, official counting command, or named-round17 denominator update. Each subprocess is limited to 20 seconds. A timeout, invalid pristine or missing site is inconclusive, never a kill."
}
```

## Exact executable experiment source

`/tmp/kama-r18-falsify-FreshGate/FreshGate-experiment.py` (UTF-8, final newline). Source mutations are the exact four surgical substitutions listed above, each reversed before the next pristine phase; this script is intentionally not a mutator.

```python
#!/usr/bin/env python3
"""Four preregistered local receipt mutants; this script never edits the gate."""
import concurrent.futures
import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import signal
import subprocess
import sys
import time

ROOT = Path('/tmp/kama-r18-falsify-FreshGate')
GATE = ROOT / 'tests/llamacpp-live/check-receipt.py'
LAB = ROOT / 'FreshGate-lab'
PYTHON = '/usr/bin/python3'
PRISTINE_SHA = 'c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335'
PRE = ROOT / 'FreshGate-preregister.json'
TIMEOUT = 20


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(receipt, name):
    return next(c for c in receipt['checks'] if c['id'] == name)


def prepare():
    assert sha(GATE.read_bytes()) == PRISTINE_SHA
    LAB.mkdir()
    (LAB / 'tmp').mkdir()
    subject = runpy.run_path(str(GATE), run_name='fresh_gate_fixture')
    base = subject['_selftest_receipt_v3']()
    status = copy.deepcopy(base)
    status['captures']['models']['status'] = 201
    for name in ('models_alias_id', 'models_owned_by_llamacpp'):
        check(status, name)['observed']['status'] = 201
    counts = copy.deepcopy(base)
    first = counts['transitions'][1]
    first['repeats'] = 0
    later = copy.deepcopy(first)
    later['t_ms'] = 60
    counts['transitions'].insert(2, later)
    counts['loading_503_bodies'][0]['repeats'] = 0
    check(counts, 'loading_envelope_graded')['observed']['total_503_responses'] = 1
    counts_good = copy.deepcopy(counts)
    counts_good['loading_503_bodies'][0]['repeats'] = 1
    check(counts_good, 'loading_envelope_graded')['observed']['total_503_responses'] = 2
    boolean = copy.deepcopy(base)
    check(boolean, 'models_alias_id')['evaluated'] = 1
    fixtures = {'valid': base, 'FG1-status201': status,
                'FG2-understated': counts, 'FG2-valid-two-bursts': counts_good,
                'FG3-integer-evaluated': boolean, 'FG4-v3-minimum-v2': base}
    manifest = {}
    for name, receipt in fixtures.items():
        data = (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode()
        path = LAB / (name + '.json')
        path.write_bytes(data)
        manifest[name] = {'path': str(path), 'sha256': sha(data)}
    (LAB / 'fixtures-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'event': 'prepared', 'gate_sha256': sha(GATE.read_bytes()),
                      'preregister_sha256': sha(PRE.read_bytes()),
                      'python': sys.version, 'fixtures': manifest}, indent=2))


def invoke(name, argv, expected_exit):
    env = dict(os.environ)
    env['TMPDIR'] = str(LAB / 'tmp')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    start = time.monotonic()
    proc = subprocess.Popen(argv, cwd=str(ROOT), env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)
    timeout = False
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        timeout = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    finally:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        os.killpg(proc.pid, 0)
        group_remains = True
    except ProcessLookupError:
        group_remains = False
    prefix = {0: 'VALID ', 1: 'INVALID ', 3: 'NOT-EVALUATED '}
    matched = (not timeout and proc.returncode == expected_exit
               and (name == 'selftest' or stdout.startswith(prefix[expected_exit])))
    return {'name': name, 'argv': argv, 'cwd': str(ROOT), 'pid_pgid': proc.pid,
            'expected_exit': expected_exit, 'exit': proc.returncode,
            'seconds': round(time.monotonic() - start, 3), 'timeout': timeout,
            'matches_expected': matched, 'post_cleanup_group_exists': group_remains,
            'stdout': stdout, 'stderr': stderr,
            'stdout_sha256': sha(stdout.encode()), 'stderr_sha256': sha(stderr.encode())}


def run_phase(stage, mutant):
    source_sha = sha(GATE.read_bytes())
    if stage in ('pristine', 'restored'):
        assert source_sha == PRISTINE_SHA
    else:
        assert stage == 'mutated' and source_sha != PRISTINE_SHA
    common = [PYTHON, '-B', str(GATE)]
    pins = ['--expect-model-sha256', 'a' * 64,
            '--expect-server-sha256', 'b' * 64,
            '--expect-probe-sha256', 'c' * 64,
            '--expect-tool-sha256', '9' * 64]
    cases = [('valid', 0, 'v3'), ('FG1-status201', 1, 'v3'),
             ('FG2-understated', 1, 'v3'), ('FG2-valid-two-bursts', 0, 'v3'),
             ('FG3-integer-evaluated', 1, 'v3'), ('FG4-v3-minimum-v2', 0, 'v2')]
    tasks = [('selftest', common + ['--selftest'], 0)]
    for name, expected, floor in cases:
        tasks.append((name, common + [str(LAB / (name + '.json')),
                                     '--require-schema', floor, *pins], expected))
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        futures = [pool.submit(invoke, *task) for task in tasks]
        runs = [f.result() for f in futures]
    result = {'stage': stage, 'mutant': mutant, 'gate_sha256': source_sha,
              'preregister_sha256': sha(PRE.read_bytes()),
              'selftest_passed': runs[0]['matches_expected'],
              'off_suite_passed': all(r['matches_expected'] for r in runs[1:]),
              'any_timeout': any(r['timeout'] for r in runs),
              'any_group_remains': any(r['post_cleanup_group_exists'] for r in runs),
              'runs': runs}
    path = LAB / (mutant + '-' + stage + '.json')
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['selftest_passed'] and result['off_suite_passed'] else 1


if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare()
    else:
        raise SystemExit(run_phase(sys.argv[1], sys.argv[2]))
```

## Scratch removal evidence

After capturing the exact sources and results into this report, executed (exit 0; stderr empty):

```sh
/usr/bin/rm -rf -- /tmp/kama-r18-falsify-FreshGate && /usr/bin/test ! -e /tmp/kama-r18-falsify-FreshGate && /usr/bin/printf 'scratch_absent=1\n'
```

Actual stdout:

```text
scratch_absent=1
```

No scratch directory remains. The restored gate hash and final listener/process-group evidence were captured before removal. This report is the only delivered file.
