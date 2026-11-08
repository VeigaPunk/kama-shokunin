# EX02HarmSuites — round 95, C1 kill rule K2 (harm suites, base vs tip)

## Scope

Ran the seven suites C1's K2 names, plus one read-only GET pair on the operator router
(`127.0.0.1:1234 /v1/models` + `/props`), against **two** probe revisions on this host, and produced
the two receipts the plan names. No tracked lane file was edited; nothing was committed; no
subagent was dispatched.

- Base revision (B): `2011161d5e5612fa953708cf54084b7f10ce99b1` — probe sha256
  `27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4`. That sha equals
  `probe_sha256=` in the frozen do-nothing control `controls/c1-base.out`, so the base receipt is
  anchored to the same probe bytes the frozen control graded.
- Round-95 revision: `f63256607916cdeb35580a7af315b5f4b54eba18` (M1). Probe sha256
  `436d994c71c0af3a96bc1f5ab0f884f629395313f3c02716738cf7af7931b722`, verified byte-identical to
  the working-tree `tools/kama-probe.sh` at run time and to `git show ca531563:tools/kama-probe.sh`
  (lane HEAD when the receipts were written).
- Isolation: `TMPDIR`, `LLAMA_CACHE`, `HF_HOME` all under the seat scratch; the round-89 suite was
  run with `LLAMA_CACHE`/`HF_HOME` pointing at one empty dir (round-94 MT01 DEFECT-4). Lane cwd,
  read-only; the four counters read the probe with `git show <rev>:tools/kama-probe.sh`. No suite
  was skipped for runtime; the slowest was 82.7 s. Host load during the wave: load1 43.7 → 143.4
  (32-core multi-agent box, 0 CPU burners started by this seat).

## Commands and outputs (true exit codes)

Base (probe bytes materialised with `git show 2011161d:tools/kama-probe.sh`):

| Suite | Exit | Result | Wall |
|---|---|---|---|
| `python3 tests/probe-verdicts/check.py --probe <base> --json` | 0 | tests=77 passes=77 failures=0 | 45.9 s |
| `KAMA_PROBE=<base> bash tools/test-snapshot.sh` | 0 | pass=30 fail=0 | 2.8 s |
| `LLAMA_CACHE/HF_HOME=<empty> python3 tools/round89-unloadable-cells.py --repo . --rev 2011161d --work <scratch>` | 0 | cells=11 mismatches=0 positive=0 | 54.5 s |
| `python3 tools/round90-hostile-answers.py --repo . --rev 2011161d --work <scratch>` | 0 | cells=13 mismatches=0 positive=0 | 9.8 s |
| `python3 tools/round91-answer-time.py --repo . --rev 2011161d --work <scratch>` | 0 | cells=12 mismatches=0 positive=0 | 14.5 s |
| `python3 tools/round92-linear-paths.py --repo . --rev 2011161d --work <scratch>` | 0 | cells=15 mismatches=0 positive=0 | 31.3 s |
| `python3 tools/round93-router-repeat.py --repo . --rev 2011161d --work <scratch>` | 0 | cells=10 mismatches=0 positive=0 (load1=136.52) | 82.7 s |
| `curl -sS -m 10 :1234/v1/models`; `curl -sS -m 10 :1234/props` | 0 | 200/4054 B and 200/233 B | 0.03 s |

Tip (`--rev f6325660`, probe bytes identical to the working tree):

| Suite | Exit | Result | Wall |
|---|---|---|---|
| `check.py --probe <tip> --json` | 0 | tests=77 passes=77 failures=0 | 63.0 s |
| `test-snapshot.sh` (KAMA_PROBE=<tip>) | 0 | pass=30 fail=0 | 5.8 s |
| `round89-unloadable-cells.py --rev f6325660` | 0 | cells=11 mismatches=0 positive=0 | 52.7 s |
| `round90-hostile-answers.py --rev f6325660` | 0 | cells=13 mismatches=0 positive=0 | 15.3 s |
| `round91-answer-time.py --rev f6325660` | 0 | cells=12 mismatches=0 positive=0 | 52.8 s |
| `round92-linear-paths.py --rev f6325660` | 0 | cells=15 mismatches=0 positive=0 | 59.9 s |
| `round93-router-repeat.py --rev f6325660` | 0 | cells=10 mismatches=0 positive=0 (load1=143.24) | 74.5 s |

Paired A/B re-run of round-91, interleaved base/tip/base/tip at load1 107.7/104.2/104.5/106.5: all
four runs exit 0, 12/12 cells ok.

## Findings

- **NOTE (no regression).** No suite passes at base and fails at tip; every verdict, reason and
  `ok=` cell is identical. Under the requested normalization (digests + timings stripped) the
  residual differences are only `rev=`, `probe_sha256=`, ephemeral stub ports and the round-90
  `sent=` byte counts; with those also stripped all seven suites are byte-identical.
  Evidence: `controls/harm-base.out`, `controls/harm-tip.out` (last section), `evidence/diff-*.txt`,
  `evidence/diff-strict-*.txt`. ⇒ K2 does not fire.
- **NOTE (receipt diff hygiene).** `tests/probe-verdicts/check.py` embeds the ephemeral stub port and
  a curl millisecond count inside each `evidence` string, so a naive digest/timing strip leaves 156
  differing lines that are pure infrastructure. `evidence/normalize.py --strict` removes them and the
  document becomes identical.
- **NOTE (a counter cell is nondeterministic by construction).** `round90` H1/H2/H3 print
  `sent=` socket-delivery bytes that vary per run (H1: 2 621 512 base vs 72 tip; H2 6 488 136 vs
  5 963 848; H3 6 357 044 vs 5 242 932). The cell grades `sent <= 16 MiB`, both runs pass, and the
  verdict is `FOREIGN_SERVICE`/`MODEL_UNLOADED` in both — a diff that keeps `sent=` therefore shows
  noise, not behaviour. Evidence: `evidence/diff-round90.txt`.
- **NOTE (a single-shot timing comparison misleads on this host; the change costs nothing measurable).**
  Single-shot walls looked like a 2–4× tip slowdown (round91 14.5 s → 52.8 s; round92 31.3 s → 59.9 s),
  but the runs were not load-matched. The interleaved A/B at load1 ≈ 105 gives T-cell median ratio
  **1.19** against a P-cell control median of **0.97**, where the P cells (plain `/v1/models` lists)
  cannot enter the changed router file-state path at all. Evidence: `evidence/paired-ab-round91.txt`.
- **NOTE (routed, NOT reproduced — for CR01/SC01, not a harm-suite result).** The pass allowance is
  per **entry**, the work is per **distinct inode**: `ncand` counts unloaded candidate entries
  (`tools/kama-probe.sh:879`) and the limit is `20 + 15*ncand` (`:829`), while `file_state()` parses
  **every** `PATH_FLAGS` path of an entry (`:761-777`) and only repeated *inodes* share the memo
  (`:597-608`). The comment at `:828` ("ncand over-estimates the work and never under-estimates") holds
  for repeated/aliased paths but not for an entry naming two distinct worst-case files
  (`-m A --mmproj B`, or three with `-md`). The probe's own comment (`:826-827`) prices one MAX_STEPS
  parse at ~4 s idle / ~12 s loaded; two distinct such parses per entry under load exceed 15 s per
  entry, which would truncate the pass and leave the tail candidates `-` (loadable → `MODEL_OK`).
  Round-93 `R06-slow-mmproj-x64` cannot see this because all 64 entries share the same `--mmproj`
  inode. [INFERENCE] — I did not build the held-out fixtures (that is `SC01HeldOutListings` /
  `CR01BudgetCounter` territory, and reproducing it needs 16×~100 MB worst-case headers plus load).
- **NOTE (live router, read-only).** `:1234` answers `role=router`, `models_autoload=true`,
  `max_instances=2`, `build_info=b1-39febd2`, 4 entries all `unloaded`
  (`LFM3-1.7B`, `LFM3-1.7B-Uncensored`, `LFM3-Omni-2B`, `LFM3-VL-2B`). GET only; the probe was *not*
  pointed at 1234 (it would also GET `/health` and stat the candidates' files). Evidence:
  `evidence/live-models.json`, `evidence/live-props.json`.
- **NOTE (prereqs held).** round-89 pinned `llama-server` sha256 `ba272ee3…62b0` and model
  `stories260K.gguf` sha256 `270cba1b…256d` both matched, so its 11 cells are a real router's
  answers, not an environment fault.

No BLOCKER and no DEFECT is filed from this seat: every named suite is green at both revisions.

## Deliverables

- `controls/harm-base.out` — base receipt (rev, probe sha, load samples, all 8 suite outputs, cross-revision diff).
- `controls/harm-tip.out` — round-95 receipt (same shape).
- `evidence/` — `check-base.json`, `check-tip.json`, `raw-{base,tip}-{snapshot,round89..round93}.out`,
  `diff-*.txt` (digests+timings stripped), `diff-strict-*.txt` (ports/revs/sent also stripped),
  `normalize.py`, `paired-ab-round91.txt`, `ab-{base,tip}-91-{1,2}.out`, `live-models.json`, `live-props.json`.

Tooling: nothing installed or upgraded (no package manager ran). Seat scratch
`/fast/scratch/hyaku/kama-r95/EX02HarmSuites` removed after the deliverables were copied; no process
this seat started is alive (`pgrep -af EX02HarmSuites` → none); no CPU burner was ever started.

VERDICT: holds — all 7 K2 harm suites plus the read-only live GET pass at base `2011161d` and at the round-95 probe `f6325660` with identical verdicts; no suite regresses, so C1's K2 does not fire.
