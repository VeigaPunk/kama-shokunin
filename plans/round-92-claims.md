# Round 92 — frozen claims (kama)

Base revision `ed018ca0fa956c5052b3dc6b714a2cb72973da21` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0 tracked=0 untracked=0). L1 `KamaR92` (holds the §3 planner seat). Frozen in the commit that adds
this file; nothing below changes after that commit. Every control named here was executed before this file was
committed; its receipt is committed with it under `.ufo/waves/round-92/controls/`.

Closure history read before declaring: `corpus/lessons/round-91-verifier-spotcheck.md` (r91 **rejected-honest-stop**:
C1 verified, C2 not verified — frozen K2 fired on T07; routed R1–R5), r90 and r89 admitted, r86–r88
rejected-honest-stop (MANIFEST). Both claims answer routed defects: C1 is R4 (T07 and the six overreaching rows need
superseding rows, not prose) under KQ146; C2 is R5 (wave-1 SC02 F1–F3: three super-linear paths present at base).

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7. Lowest
non-retired: depth / calibration / adjacency (7). C1 works depth.

## C1 — depth (lowest axis, 7): serving defaults re-declared under KQ146, each bound to the line the binary uses

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round92-server-defaults.py --repo . --rev <M1> --binary /home/vgpnk/.local/opt/llama-b12177/llama-server`
prints `SERVER_DEFAULTS rows=<n> bound=<n> unbound=0 duplicates=0 engines=<e> fetch_failures=0 help_checked=<h>
help_disagree=0 supersedes=14 …` with n >= 14, e >= 3, h >= 7, and exits 0 at the measured commit M1, the counter's
bytes identical to this freeze commit.

- Population: rendered rows of `SKILL.md` `## Serving defaults (round 92 revision)` (10 cells; counter docstring).
  Binding = the round-91 rules B1–B7 plus KQ146 (`corpus/QUALITY.md`, round-91 lesson M1): H1 every llama.cpp row
  with an option equals the pinned binary's `--help` default (binary sha256 `ba272ee3…` pinned, else exit 2); H2 a
  llama.cpp default no option prints binds only to the server entry point (`/tools/server/`); every round-91 row
  T01–T14 is superseded by a bound row.
- Do-nothing control: base `rows=0`, exit 1 (`controls/c1-base.out`).
- Forgery and positive controls (`controls/c1-forgeries.py` → `controls/c1-forgeries.out`, 9/9 as expected): P0 the
  candidate table drafted before freeze (`controls/c1-candidate-section.md`, rows `c1-candidate-rows.md`) exits 0 (the
  counter is not a blanket refusal); V1 the round-91 T07 row transplanted (S593:464, value 1) → `help-default=-1`;
  V2 value -1 on the shared-struct line → value not in literal; V3 a derived row on `common.h` → not entry point; V4
  R15 dropped → `supersedes=13`; V5 an option row passed off as derived → not entry point; V6 an env var in a llama
  flag cell → not an option; V8 an unpinned binary → exit 2. **Disclosed limit (V7, exits 0):** the counter cannot
  tell which vLLM line is read at run time (the `TYPE_CHECKING` declaration `envs.py:26` binds as well as the
  `environment_variables` lambda line 812); that, and every decision's fit to its line, is the K2 reviewer read.
- Sourced: new rows S596 (llama.cpp `common/arg.cpp` @ b12177) and S597 (`tools/server/server.cpp` @ b12177), opened
  this round (sha256 `c69c0e07…`, `d4d343db…`); S593–S595 re-opened this round (digests equal to their rows).
- Kill rules (any one → C1 not verified): K1 the counter changes after this commit; K2 a non-author reviewer finds a
  row whose parameter, value, line or probe decision misstates its source line or the binary (reported per row; any
  such row → C1 not verified); K3 a row cites a source not re-opened this round.

## C2 — operability: the three super-linear probe paths wave-1 SC02 measured run in linear time

**Predicate:** `python3 tools/round92-linear-paths.py --repo . --rev <M2> --work <scratch>` prints
`LINEAR_PATHS cells=15 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured commit M2, the
counter's bytes identical to this freeze commit.

- Cells (counter docstring): 6 large cells, each finishing within 20 s wall (killed at 120 s) with a frozen verdict or
  persisted value — L1 one 1 900 000-backslash id and L2 one 1 900 000-quote id (`jstr`, F1; served_model must be the
  per-byte form D1/D2 pin, scaled), L3 80 000 unloaded router entries under `*` and L4 60 000 unloaded `good` entries
  then one loaded (`router_refine` `cand`, F2), L5 `snapshot` of 16 000 path ids and L6 one 200 000-byte slash-free id
  (`served_persist`, F3; latest.tsv served column by the normalised-basename rule). 9 differential cells D1–D9: the
  probe at M2 prints byte-identical output to the probe at BASE (same path, same stub) for ordinary answers (specials,
  router statuses, autoload with missing files, snapshot rows); a D failure is harm (`positive_mismatches`).
- Do-nothing control: base probe `controls/c2-base.out` (exit 1; L cells killed or over budget).
- Forgery controls (`controls/c2-forgeries.sh` → `controls/c2-f*.out`, `--probe-file`, print `probe=override`, can
  never meet the predicate): F1 `jstr` that truncates values over 1 MiB (fast, wrong) — L1/L2 `served_scaled=0`;
  F2 `router_refine` that reads only the first 1 000 router entries — L4 misses the final loaded entry; F3
  `served_persist` that keeps only the first 1 000 ids — L5 `served_rule=0`.
- Rule to implement (intent; the claim is judged only by the counter): `jstr` escapes in one awk pass (no
  `${s//…}` over the value), `router_refine` collects candidates in an array, `served_persist` normalises every id in
  one awk pass — same rules, no count cap.
- Kill rules: K1 `positive_mismatches>0` at M2; K2 a harm suite regresses against `controls/harm-base.out`
  (`controls/harm.sh`: `tests/probe-verdicts/check.py`, `tools/test-snapshot.sh`, `round89-unloadable-cells.py`,
  `round90-hostile-answers.py`, `round91-answer-time.py`); K3 the counter changes after this commit.
- Held-out (not in the predicate): wave seats build unseen large/slow answers after M2 and report base and M2 verdicts
  and times; a held-out cell where base is right and M2 wrong is harm.

## Separability, sources, carried defects

- C1's counter never runs the probe; C2's counter never reads `SKILL.md` or `SOURCES.md`. Either verifies with the
  other unlanded.
- Sourced claim: C1 (S596, S597 new; S593–S595 re-opened).
- Carried from the r91 closure: R1 (`round75-instruments` `bad_rows=19`, L0 open) stays open, not claimed; R2 (S593
  teaches cell still says "one parallel sequence") — dated correction appended to `corpus/SOURCES.md` this round;
  R3 (twin seats sharing scratch) — every wave item names its own scratch root
  `/fast/scratch/hyaku/kama-r92/<seat>/`; R4 is C1; R5 is C2.
