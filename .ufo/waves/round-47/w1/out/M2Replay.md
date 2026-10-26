# M2Replay — round 47 w1, replay tool mutation test (lane kama)

**Verdict:** 24 mutants of `tools/kama-live-replay.py` at 3a09a1d93dcc16799cf6c4b48786e6440af134c4 — 12 killed by `--selftest`, 0 killed by the frozen C2 counter alone, 10 SURVIVED both (real coverage findings, proposed selftest cases below), 2 equivalent; baseline and restored-bytes counter runs both `met=True`, every mutant commit restored byte-exact.

Tooling installs: none (stdlib python3 only). No lane file was modified; all lane runs went through `git clone --shared` copies; the only git mutations were commits inside my scratch fixture (fixture identity `M2Replay-fixture <m2replay@fixture.invalid>`, toplevel asserted before every commit).

## 1. Setup and baselines

- Pristine bytes: `git -C $S/lane show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/kama-live-replay.py` → sha256 `39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0`.
- Pristine selftest: `python3 pristine.py --selftest --scratch $S/st-pristine` → exit 0, `KLR_SELFTEST pass=10 fail=0` (all 10 cases pass). (`--scratch` must already exist; the first sweep without `mkdir` crashed all runs — logs discarded, rerun with existing dirs.)
- Fixture: `git clone --shared` of the lane, detached at 3a09a1d9, one row appended to `corpus/SOURCES.md` (S488, registers b11909 = caa8191df159f764fb0160e3d2fc6be008948aee + asset digest, mirrors S486/S487 shape; the counter's newrow leg needs only a `| S` line containing release+commit). Fixture BASE = `ca53deab817a34eb3e5321f040f9a02d1ff48a95`, worktree clean before commit.
- Baseline C2 (pristine tool bytes, frozen counter):
  `python3 tools/round47-live-replay-audit.py --repo <fixture> --tip ca53deab… --scratch $S/c2-baseline`
  → exit 0, `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (4.6 s wall). Baseline failure would have made every mutant run inconclusive; it passed.

## 2. Mutants and verdicts

Generated programmatically; every edit pattern asserted to occur exactly once; all 24 mutants `compile()` clean. Per-mutant files + unified diffs: `out/M2Replay/mutants/`, hashes in `mutants/manifest.json`. Line numbers refer to pristine.

| id | mutation (file:line) | category | selftest | counter | verdict |
|----|----------------------|----------|----------|---------|---------|
| m01 | acquire(): `if got != sha` refusal removed (L92-95) | refusal on mismatch | FAIL exit 1 (2 cases) | — | killed-by-selftest |
| m02 | model digest acquired AFTER `extract(archive, tree)` (L141-144 reordered) | digest check order | 10/10 exit 0 | met=True | **survived** |
| m03 | `fetch(archive)` then `extract`, digest verified after (L141-144 reordered) | digest check order | 10/10 exit 0 | met=True | **survived** |
| m04 | `os.unlink(dest)` on mismatch removed (L93) | refusal on mismatch | 10/10 exit 0 | met=True | equivalent (leftover file under `--work` only) |
| m05 | provenance model-digest ≡ receipt model check removed (L81-82) | model digest vs receipt model | FAIL exit 1 (1 case) | — | killed-by-selftest |
| m06 | `or ".." in member.split("/")` dropped (L84) | member traversal | FAIL exit 1 (unsafe-member) | — | killed-by-selftest |
| m07 | `filter="data"` → `filter=None` (L100) | member traversal | 10/10 exit 0 | met=True | **survived** |
| m08 | realpath-inside-tree gate removed, isfile kept (L146) | member traversal | 10/10 exit 0 | met=True | **survived** (latent; needs m07) |
| m09 | receipt schema gate reduced to `prov is None` (L70) | schema check | FAIL exit 1 (v3-receipt, exit 0) | — | killed-by-selftest |
| m10 | rerun schema not compared (compare() L110-111) | compare rules | 10/10 exit 0 | met=True | **survived** |
| m11 | rerun outcome not compared (L112-113) | compare rules | 10/10 exit 0 | met=True | **survived** |
| m12 | rerun server sha not compared (L114 → `("model",)`) | compare rules | 10/10 exit 0 | met=True | **survived** |
| m13 | rerun model sha not compared (L114 → `("server",)`) | compare rules | 10/10 exit 0 | met=True | **survived** |
| m14 | `check:{cid}:not-evaluated` → `continue` (L120-121) | compare rules | 10/10 exit 0 | met=True | **survived** |
| m15 | `er[cid] != passed` → `not er[cid]` (L122) | compare rules | FAIL exit 1 (check-differs) | — | killed-by-selftest |
| m16 | Refused exit 2 → 0 (L168) | exit codes | FAIL exit 1 (8 cases) | — | killed-by-selftest |
| m17 | Refused exit 2 → 1 (L168) | exit codes | FAIL exit 1 (8 cases) | — | killed-by-selftest |
| m18 | match/differ exit → always 0 (L165) | exit codes | FAIL exit 1 (check-differs) | — | killed-by-selftest |
| m19 | match↔differ exits swapped (L165) | exit codes | FAIL exit 1 (2 cases) | — | killed-by-selftest |
| m20 | `file://` scheme no longer accepted (L59) | file:// acceptance | FAIL exit 1 (5 cases) | — | killed-by-selftest |
| m21 | scheme check removed entirely (L59-60) | file:// acceptance | FAIL exit 1 (http-refused) | — | killed-by-selftest |
| m22 | missing-provenance never refused (`missing = []`, L75) | schema check | FAIL exit 1, uncaught `AttributeError: 'NoneType'.split` at L140, no summary | — | killed-by-selftest |
| m23 | HEX64 digest-format loop emptied (L78) | refusal on mismatch | 10/10 exit 0 | met=True | **survived** (low sev.) |
| m24 | `evaluated()` gate `and c.get("evaluated")` dropped (L105) | compare rules | 10/10 exit 0 | met=True | equivalent on frozen data |

Counts: 24 = 12 killed-by-selftest + 10 survived-both + 2 equivalent. Counter runs for all 12 selftest-survivors: every one `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`, exit 0 (see `logs/counter-summary.tsv`).

Key kill evidence (selftest, from `logs/selftest-*.log`):
- m01: `asset-digest-wrong` case exits **0** with `mism=[]` — a receipt with a wrong asset digest replays clean.
- m16: all 8 refusal cases exit 0 (e.g. `digest-mismatch` refused with exit 0).
- m22: crash instead of refusal — `AttributeError` at `need["model.url"].split("?")`, exit 1, no `KLR_SELFTEST` line.

## 3. Findings (survivors) with proposed selftest cases

Full concrete proposals: `out/M2Replay/proposed-selftest-cases.py` (proposal only — counter and tool are frozen; do not edit in place).

1. **m02/m03 — digest verified after extraction** (`replay()` L141-144). Contract (docstring and C2 docstring): "verifies each sha256 against the receipt BEFORE anything is extracted or executed". Both mutants keep the refusal and its reason, so the existing cases pass; the official b11909 archive is benign, so the counter's tamper leg also passes. Fix case: assert `work/server` absent after the two existing digest-refusal cases, plus `asset-digest-wrong-unextractable` (non-tar bytes + wrong recorded sha → pristine refuses `digest-mismatch` before tarfile; m03 surfaces `could-not-run:ReadError`).
2. **m07 — tarfile data filter disabled** (`extract()` L100). `filter=None` extracts traversal/absolute members of a digest-verified archive outside `work/server`. Only exploitable upstream of a github compromise, but it is the tool's only extraction sandbox. Fix case: `traversal-member-refused` (archive with an extra `../escape.txt` member → pristine refuses `could-not-run`; m07 exits 0).
3. **m08 — realpath-inside-tree gate removed** (L146). Redundant while `filter="data"` holds (data_filter rejects escaping links), i.e. pure defense-in-depth — but combined with m07 a symlinked `llama-server` member would execute an arbitrary host binary and still "match". Combo case: `symlink-member-refused`.
4. **m10–m14 — compare() rule weakenings** (L108-124). Each drops one mismatch class (schema, outcome, server sha, model sha, missing check). On the frozen benign data the rerun matches on every axis the counter independently re-checks, so neither detector sees it; the tool's `match` boolean and exit 0/1 contract become unreliable the moment a rerun differs in exactly the dropped axis. Fix: make the fake live tool spec-driven and add the five one-axis-differs cases (kills each mutant individually).
5. **m23 — digest format check removed** (L78-80). Not fully equivalent: a receipt with non-hex `model.sha256` (equal to `rec.model.sha256`) is refused **only after the mutant downloads it** — network I/O on malformed provenance; pristine refuses `provenance-bad-digest` before any fetch. Distinguishing case: `non-hex-digest-refused` asserting the refusal prefix.

Equivalents: m04 leaves the mismatched download in `--work` (tool writes only under `--work`/J; no consumer reads it after refusal). m24 makes the tool stricter, but receipt-1/2/3 have 11/11 checks `evaluated` and the rerun likewise (verified on receipt-1), so no behavioral delta on the frozen data; it would cause false mismatches on receipts with non-evaluated entries.

Counter observation: for this tool the counter killed nothing the selftest didn't — its tamper leg fires only on digest-refusal mutants (m01 class), which are already selftest-covered, and its replay leg independently re-verifies schema/outcome/shas/checks, which masks compare-rule mutants on benign data. The selftest is the load-bearing detector here; the 10 survivors are selftest coverage gaps, not counter defects. No defect found in the frozen counter or preregistration itself.

## 4. Restoration evidence

- After each of the 12 counter runs: `git checkout $BASE -- tools/kama-live-replay.py`, worktree sha256 re-hashed == `39cd387a…` (`restored_sha_ok=yes` for all 12, `logs/counter-summary.tsv`).
- Final restored-bytes counter run on BASE: exit 0, `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (`logs/c2-restored.log`); worktree sha `39cd387a…` confirmed immediately before.
- Fixture commits live only in my scratch (deleted at cleanup); the lane at 3a09a1d9 untouched.

## 5. Artifacts

- Report: `.ufo/waves/round-47/w1/out/M2Replay.md` (this file)
- `out/M2Replay/mutants/` — 24 mutant files + `diffs/` + `manifest.json`
- `out/M2Replay/logs/` — selftest logs (pristine + 24), counter logs (baseline + 12 mutants + restored), `selftest-summary.tsv`, `counter-summary.tsv`
- `out/M2Replay/pristine-kama-live-replay.py`, `SHA256SUMS` (93 files)
- `out/M2Replay/receipt-1.json` (copy of cited receipt)
- `out/M2Replay/proposed-selftest-cases.py`
