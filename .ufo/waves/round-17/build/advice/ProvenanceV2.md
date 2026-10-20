VERDICT: confirm — round-17 dispatch-provenance.py landed; defect-1 (a)–(d) implemented, 28/28 selftest, real policy parses v2/64-100-100.

Seat: KamaR17.ProvenanceV2-2. Routed defect 1 of `corpus/lessons/round-16-verifier-spotcheck.md:182` ("Record the policy version in every wave's validation ... Use a single taskCall digest canonicalization ... counts async pending spawns: the ledger shows spawned:0 for 79").

## Files written

| Path | sha256 | Bytes |
|---|---|---|
| `.ufo/waves/round-17/dispatch-provenance.py` | `11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df` | 37928 |
| `.ufo/waves/round-17/build/advice/ProvenanceV2.md` | (this file) | — |

No other file touched. Started from the round-16 tool; every round-16 flag and ledger/entry field is retained (superset).

## What implements each defect

- **(a) policy identity** — every entry (`wave_run`, `attempt`) carries `policy{path, sha256, version, policy_version, band{waveMinLanes,waveMaxLanes,maxLanes}}`. `path` = `ENV_BINDINGS["UFO_CONFIG_PATH"]`; `sha256` = file bytes read at record time; `version` parsed by `hyaku campaign policy (v\d+)` from `sighting.dispatch.swarm.note` (fallback: first matching `note` string anywhere in the doc); `policy_version` is the same value under the defect-1a field name; nulls on missing/unparseable (sha256 kept whenever bytes were read). Verified against the live policy: `version=v2`, band `64/100/100`, sha256 `70418a0f…f9f9` — matching the L1-recorded `build/validation.json`.
- **(b) one canonicalization** — `json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')`, the same literal L1 recorded in `build/validation.json:19`. Pinned in the module docstring and the `CANONICALIZATION` constant; recorded verbatim as `canonicalization` in every entry and validation file so verifiers never guess (the r16 defect: build needed `ensure_ascii=True`, falsify producer used `False`).
- **(c) async pending counts** — `spawned` resolution precedence, recorded in `spawned_method`, all observations kept in `spawned_methods`:
  1. `omp_text_spawned_header` — `Spawned N background agents` regex in any `text` string;
  2. `omp_text_member_bullets` — ``- `Name` (job ...)`` bullet lines;
  3. `omp_progress_members` — length of `progress` lists whose elements all carry `id`+`status`;
  4. `omp_progress_pending` — subset with `status=="pending"`;
  5. `key_status_tally` — legacy tally only when positive (preserves r16 behaviour for non-OMP payloads).
  Non-JSON result files are scanned as raw text for the header/bullet patterns (`parseable:false` but spawned still counted). `refused` keeps the legacy tally unchanged. Scratch run on an OMP-shaped fixture (header + 2 bullets + 2 pending progress rows): `spawned=2 via omp_text_spawned_header`, `bound_task_call_sha256` bound to the last wave_run.
- **(d) `--write-validation PATH`** — emits `{argv, cwd, env_bindings, exit, stdout_sha256, taskCall_sha256, canonicalization, counts, policy{path,sha256,version,band}, recorded_at}` — exactly the required key set, policy restricted to the four keys matching `build/validation.json`. Usable two ways: appended to a `--spec` run (this run's validation), or standalone from the ledger's latest `wave_run` (backfills falsify's missing file — though the r16 taskCall digest may not reproduce, see limitations). Exclusive create via tempfile + `os.link`: an existing path is refused, never clobbered (verified: exit 64).
- **`--selftest`** — 28 checks, all in-memory/tempdir fixtures covering (a)–(d): canonicalization formula + `ensure_ascii=False` pin, policy parse/fallback/null paths, all five spawned methods, entry binding, exact validation key set, v1-ledger acceptance, exclusive-create refusal. `28/28` passed.

## Design choices

- Ledger schema `dispatch-provenance-ledger-v2`; v1 ledgers accepted for appending and keep their v1 tag on write (round-16 ledgers stay usable; `load_ledger` returns the doc as read, `write_ledger` re-serializes it unchanged).
- `build_run_entry`/`build_attempt_entry`/`parse_attempt_result`/`parse_policy` are pure functions so the selftest exercises real code paths without spawning node or reading the real policy.
- `refused` intentionally un-touched: no "Refused N" textual shape was observed in round-16 results; widening it would guess at a format [INFERENCE].
- `spawned_methods` retains per-method observations so a verifier can audit the chosen total (e.g. header 82 vs bullets 82 vs pending 82 agree).

## Verification exercised

`python3 -m py_compile` ok; `--selftest` 28/28; `--help` renders; scratch `/tmp` run of `--attempt-result` (spawned=2/header) and `--write-validation` (exact key set, real policy v2/64-100-100, existing-file refusal exit 64). Scratch dir and `__pycache__` removed; no ports bound (`ss -ltnp` clean on 8080/34113). Not run against a real spec — L1's per assignment.

## Limitations / notes for L1

- Mode-3 re-emission re-reads the policy file at emit time: the `policy` block reflects the file *now*, which may differ from the policy digest recorded in the `wave_run` entry (entry remains authoritative for the run).
- `counts` in emitted validation copies the ledger entry's `counts` object (wave-runner shape), not the `{spawn,resume,total}` shape L1 hand-recorded in `build/validation.json` — different provenance, both recorded.
- A round-16-committed `taskCall_sha256` produced with `ensure_ascii=True` will not reproduce under this canonicalization; the falsify digest `72e81bc6…` reproduced with `False` per the spot-check (`round-16-verifier-spotcheck.md:57` — build used True). [INFERENCE] If the falsify result predates this canonicalization, mode-3 backfill records the r16 digest as committed and the canonicalization field declares the discrepancy.
- Bullet regex requires `` `name` (job `` backtick form; non-OMP bullet styles fall through to lower-precedence methods.

## Installs

None. No pacman transaction (paused); no tool install needed.
